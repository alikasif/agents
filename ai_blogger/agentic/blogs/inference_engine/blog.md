
# How an LLM Inference Engine Really Works: A Guided Tour with vLLM

When you deploy a large language model behind an API, the model weights are only half the story. Between a user’s prompt and the streamed response sits an **inference engine**: the software stack that decides which requests to run, how to pack them on the GPU, how to manage memory, and which kernels to call.

This post walks through how such an engine works internally, using **vLLM** as a concrete example. The goal is to assume you know transformers and GPUs, but haven’t yet looked inside a serving engine.

---

## 1. The Core Problem: Many Users, One (Big) GPU

Imagine you have:

- A 7B–70B parameter LLM on a single GPU.
- Dozens or hundreds of users hitting a chat endpoint.
- Hard constraints on latency and cost.

A naïve setup—“take each request, call `model.generate()` one by one”—fails quickly:

- **GPU under‑utilization**: during token‑by‑token decoding, a lot of GPU compute sits idle while memory is being shuffled around.
- **Out‑of‑memory errors**: long prompts and responses blow up the key–value (KV) cache.
- **Unpredictable latency**: a few long generations can block many short ones.

An inference engine exists to solve exactly this: *turn many irregular, streaming conversations into efficient, predictable GPU workloads*.

To see how it does this, first look at what the workload actually looks like.

---

## 2. The Workload: Prefill vs Decode

When a user sends:

> `Hello, my name is`

it does not get processed the same way as the tokens in the continuation:

> `John, and I work as a software engineer...`

Internally, LLM inference has two phases:

### Prefill: “Read the whole prompt”

In **prefill**, the model ingests all input tokens in one shot:

1. Tokenize the prompt into, say, 5 tokens.
2. Run those 5 tokens through all layers of the transformer.
3. For each position, compute attention over all previous positions.

This is a large, dense matrix computation. It maps well to GPUs: all tokens in the prompt can be processed in parallel across layers. This phase is **compute‑heavy**: the GPU cores are busy almost all the time.

### Decode: “Write the answer, token by token”

Once the prompt has been processed, the model starts **decoding**:

- At step 1, it looks at the 5‑token context and generates token 6.
- At step 2, it looks at 6 tokens and generates token 7.
- And so on.

At each decode step, you only add **one** new token, but the model must look back at all previous tokens in the sequence. That means:

- Reading lots of data (model weights and cached states) from memory.
- Doing relatively little new computation.

This makes decode **memory‑bound**: the GPU often waits for data rather than arithmetic. Prefill loves parallelism; decode is inherently sequential.

An inference engine is built around this asymmetry. It needs to:

- Keep the GPU busy even though decode is serial.
- Keep memory under control even though sequences and batch sizes grow.

To do that, it focuses on two dimensions: **memory layout** and **scheduling**.

***

## 3. The Big Pieces Inside an Inference Engine

Although implementations differ, you can mentally split an engine like vLLM into four big components:

1. **Front‑end & Scheduler**  
   Receives requests (e.g., HTTP), tokenizes them, keeps track of which ones are waiting and which ones are actively decoding, and decides what to run next each step.

2. **KV Cache Manager (Paged KV Layer)**  
   Owns the GPU memory used for attention key/value states, slices it into reusable blocks, and tracks which blocks belong to which request.

3. **Model Executor (Kernels)**  
   Runs the actual transformer layers for the current batch of tokens using optimized attention and matmul kernels.

4. **Sampling & Streaming Layer**  
   Turns logits into tokens (top‑k, nucleus, temperature), and streams tokens back to the client as they’re produced.

The magic comes from how these pieces cooperate. Let’s go deeper into the two core ideas: how KV is stored, and how requests are batched.

***

## 4. KV Paging: Managing Memory Like an Operating System

### Why KV cache is a problem

In a transformer, attention at each layer needs K and V for all previous tokens so that each new token can “look back” over the context. Recomputing K and V at every step would be prohibitively expensive, so engines **cache** them.

For one sequence, the memory used by KV cache scales roughly with:

- number of layers,
- hidden size,
- sequence length.

When you multiply that by the number of concurrent sequences, KV cache quickly becomes one of the biggest memory consumers in the system.

A naïve design might allocate a big contiguous KV buffer for each request sized for some maximum context length. That leads to:

- **Wasted memory**: short prompts and short responses don’t use their full slice.
- **Fragmentation**: when requests finish at different times, you end up with holes that are hard to reuse efficiently.

### The paging idea

vLLM instead treats GPU KV memory a bit like an OS treats RAM:

- Break the KV space into fixed‑size **blocks** (often enough space for K and V for a small number of tokens, e.g., 16).
- Maintain a global pool of free blocks.
- For each request, keep a small table: “my tokens live in blocks [b7, b20, b21, ...].”

Nothing says those blocks must be contiguous in physical memory. They’re just “pages” that can be mapped to any request.

### A simple walk‑through

Take our running example:

> `Hello, my name is`

Suppose it becomes 5 tokens, and each block can hold KV for 16 tokens.

1. **Prefill**:  
   - The KV manager sees it needs space for 5 tokens → 1 block is enough.
   - It pops, say, block 42 from the free list and marks: request A → .

2. **Decode**:  
   - As the model generates tokens 6, 7, 8, … it keeps writing their KV into block 42.
   - Once the 17th token arrives, block 42 is full.
   - The KV manager grabs another block (e.g., 7) and updates the table: request A →.[1]

3. **Finish**:  
   - When the model stops (EOS or max tokens), blocks  are returned to the free pool.[1]

Because all blocks are identical in size and can be reused by any request, memory stays packed and fragmentation is low. That means:

- You can run more requests at once.
- You can handle longer prompts and outputs without hitting OOM.

Paged KV is the “memory half” of vLLM’s design.

***

## 5. Continuous Batching: Keeping the GPU Busy

The other half is **how work is scheduled**.

### What goes wrong with static batching

Imagine you collect 32 requests, run them as a batch, then wait until all 32 have finished generating before starting the next batch:

- If one user generates 10 tokens and another generates 500, the short one waits for the long one.
- The GPU is often under‑utilized, because as requests finish, the effective batch size shrinks, but you don’t refill it until the whole batch is done.

Static batching gives decent throughput but can give terrible tail latency.

### The continuous batching approach

vLLM instead operates like a conveyor belt:

- It maintains:
  - a **waiting queue** of new requests needing prefill,
  - and a **running set** of requests currently decoding.
- At each small time step (think “next token step”), it decides:
  - which waiting prompts to prefill,
  - and which active sequences to advance by one token of decode.

There are simple constraints like “don’t process more than X prefill tokens or Y total tokens in a single step,” but within those, the engine:

- adds new sequences as soon as there is room,
- drops finished sequences immediately.

The result is that the GPU is almost always working on as many tokens as it can handle, spread across both prefill and decode, and no short request is forced to wait for an entire large batch to complete.

### The same example, now on the conveyor belt

Imagine:

- Request A: `Hello, my name is` (5‑token prompt, short answer).
- Request B: long prompt plus long answer (hundreds of tokens).
- Request C: arrives a bit later while A and B are already running.

In continuous batching:

1. First steps:
   - A and B both go through prefill together.
2. Decode starts:
   - A and B are decoding token‑by‑token in the same GPU passes.
3. A finishes early:
   - It’s removed immediately; its KV blocks are freed.
4. C arrives:
   - Scheduler sees free KV capacity and token budget → C is added to prefill and later joins decode passes.

All of this happens without resetting the batch or waiting for B to finish. That’s how you maintain high utilization and reasonable latency at the same time.

***

## 6. How the Forward Pass Actually Runs

So far, we’ve talked about scheduling and memory. How do they interact with the actual model code?

On each step, after the scheduler decides “these are the tokens we’re going to process now,” vLLM needs to:

1. Build a **packed tensor** of input tokens for all selected sequences.
2. Map each position in that tensor back to:
   - which request it belongs to,
   - which token index in that request it is.
3. Use that mapping and the block tables to find the right KV blocks for attention.
4. Run the transformer with optimized kernels.

Instead of padding every sequence to the maximum length in the batch and wasting compute on padding tokens, vLLM packs tokens tightly and uses a **slot mapping** to tell the attention kernel how to respect sequence boundaries.

Think of slot mapping as an array like:

- Slot 0–4 → request A, tokens 0–4
- Slot 5–12 → request B, tokens 0–7  
- ...

The attention kernel uses this along with the KV block table to ensure:

- each token only “attends” to the right previous tokens of its own sequence,
- even though physically, the data is laid out in a packed format in memory.

This layout makes it easier to use highly optimized kernels like FlashAttention, which fuse multiple attention operations into a single pass to reduce memory traffic.

***

## 7. A Request’s Journey End‑to‑End

Let’s tie it all together with the kind of flow you might trace in a debugger.

User sends:

> `Explain quantum computing in simple terms`

1. **Front‑end**  
   - Receives the HTTP request.
   - Tokenizes the prompt.
   - Creates an internal request object with status “waiting.”

2. **Scheduler**  
   - In the next iteration, sees that there is available token budget for prefill.
   - Picks this request (and others) for the prefill batch.

3. **KV Manager**  
   - Computes how many KV blocks are needed for the prompt tokens.
   - Takes that many blocks from the free pool.
   - Records the mapping: request → list of blocks.

4. **Model Executor**  
   - Builds a packed tensor of all prefill tokens for this step.
   - Builds a slot mapping for these tokens.
   - Runs the transformer forward pass using paged attention and optimized kernels.
   - Fills the allocated KV blocks with K and V for each token.

5. **Sampling & Streaming**  
   - Takes the logits for the last token position.
   - Samples the next token using the configured decoding strategy.
   - Starts streaming the first pieces of text back to the client.

6. **Decode loop**  
   - Scheduler now treats this as an active decoding request.
   - On each iteration:
     - It may mix this decode step with other requests’ prefill or decode steps.
     - The KV manager appends new K/V into existing blocks (and allocates a new block if a previous one fills).
     - The model executor runs another forward pass for the new token.
     - Sampling picks the next token and streams it.

7. **Completion**  
   - Once an end‑of‑sequence token appears or a max token limit is reached:
     - The scheduler removes the request from the active set.
     - The KV manager returns all its blocks to the free pool.
     - The front‑end closes the response stream.

From the user’s perspective, they just see tokens appearing quickly. Underneath, the engine has juggled memory blocks, token budgets, packed tensors, and kernels dozens or hundreds of times for this one answer.

***

## 8. Where to Go Deeper Next

This post focused on two core ideas:

- **Paged KV**: treating KV cache like a paged memory system so many sequences can share GPU memory efficiently.
- **Continuous batching**: treating decode as a stream of tiny scheduling opportunities rather than as fixed batches.

Once these mental models are clear, it’s much easier to layer on:

- quantization and model‑level optimizations,
- multi‑GPU and multi‑node setups,
- external KV cache layers,
- or routing and prefill/decode separation.

But even without those, understanding these building blocks is enough to reason about why an engine like vLLM behaves the way it does in production—and how to tune it for your workloads.

[1](https://www.anyscale.com/blog/continuous-batching-llm-inference)