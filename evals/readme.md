
# Evals — LLM & LLM-System Evaluation

This project holds notes, examples, and tools for evaluating LLM models and LLM-powered systems. The content here summarizes evaluation concepts, recommended metrics, methods (online/offline), tooling options, and practical guidance for building reliable evaluation pipelines.

## Why Evals?

Evaluations ("Evals") are the structured tests and metrics that determine whether an LLM or LLM-powered application is production-ready. Evals measure not only raw model quality but also system-level behavior (retrieval, tool use, agent workflows) and user-facing outcomes.

Key benefits:
- Surface regressions and improvements during development
- Measure real-world performance via online evaluation
- Help prioritize fixes (hallucinations, tool errors, latency)

## Levels of evaluation

- Model (LLM) evaluation: measures the core language model's capability (e.g., fluency, coherence, accuracy)
- System evaluation: measures end-to-end application behavior (retrieval quality, tool correctness, task completion)

## Offline vs Online Evaluation

- Offline: run in a controlled environment using curated datasets and ground truth. Great for CI/CD and repeatable metrics (accuracy, BLEU, ROUGE).
- Online: run against live traffic or shadow traffic to capture real user behavior (user satisfaction, success rate, real-world edge cases).

## Recommended core metrics

Pick a small set of metrics (we recommend <=5) that are highly correlated with user success. Examples:

- Answer Relevancy
- Task Completion
- Correctness / Faithfulness
- Hallucination rate
- Tool Correctness (for agentic systems)
- Contextual Relevancy (for RAG)
- Responsible metrics: toxicity, bias

Quantitative metrics should be reliable, fast to compute, and interpretable.

## Evaluation methods and scorers

- Statistical scorers: BLEU, ROUGE, METEOR — limited for long-form or subjective outputs
- Model-based scorers: BLEURT, G-Eval, Prometheus — use LLMs as judges for subjective judgments
- Hybrid approaches: QAG (question-answer generation) for faithfulness, GPTScore, SelfCheckGPT for hallucination detection

Practical tip: use model-based scorers for subjective criteria (style, helpfulness), and deterministic scorers for factual checks when possible.

## LLM-as-a-judge & HITL

- LLM-as-a-judge can scale human-like evaluation but has biases (position bias, verbosity bias, self-affinity). Mitigate via few-shot prompting, position swapping, and hybrid human+LLM workflows.
- Human-in-the-loop (HITL) remains the gold standard for nuanced or high-stakes domains (healthcare, finance).

## RAG & Agentic metrics (system-level)

- RAG metrics: Faithfulness, Contextual Precision, Contextual Relevancy — measure how well retrieved context supports generated outputs
- Agentic metrics: Tool Correctness, Task Completion — measure whether an agent selects and uses the right tools and completes the intended workflow

## Benchmarks & tools

- Common benchmarks: MMLU, HumanEval, TruthfulQA, GLUE/SuperGLUE
- Tools and frameworks: Giskard, DeepEval, MLFlow LLM Evaluate, RAGAs, Deepchecks, Arize, LLMBench, PromptFlow

## Building an evaluation pipeline — practical advice

- Define a concise metric set (1-2 custom + 2-3 system/generic)
- Keep metrics stable across model or system swaps
- Instrument both offline and online evaluations
- Cache results, version datasets and prompts, and track experiment metadata
- Surface contradictions and confidence scores; route high-impact failures to HITL

## Limitations & bias mitigation

- LLM-based evaluators may be stochastic and biased. Use position swapping, few-shot calibration, and hybrid evaluation to mitigate biases.

## Next steps (starter tasks)

1. Create a small evaluation harness that runs: QAG for faithfulness, a model-based G-Eval scorer for helpfulness, and a toxicity/bias pass.
2. Add an online telemetry pipeline to capture user satisfaction and success rates.
3. Integrate a lightweight HITL review workflow for high-impact failures.
4. Explore open-source tools (Giskard, DeepEval) and run on sample datasets.

---

