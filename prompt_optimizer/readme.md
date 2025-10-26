
## Prompt Optimizer Workflow

This project implements an iterative prompt optimization system that continuously improves both
prompts and user inputs through a cyclic pattern of reflection, optimization, and generation.
The goal is to converge on prompts and inputs that produce outputs better aligned with user
intent, better grounded in facts, and easier to validate.

### High-level overview

- Workflow pattern: generate -> reflector -> optimizer -> regenerate -> [repeat or judge]
- Components:
   - Reflector — analyzes user input, prompt, and generated output; emits structured feedback.
   - Optimizer — applies reflector feedback to produce an improved prompt and (optionally) a
      clarified user input.
   - Generator — produces content from the (optimized) prompt and user input.
   - Judge — optional evaluator that compares original and regenerated outputs to decide when
      to stop iterating.

### Why this pattern

This separation of concerns lets each component focus on a single responsibility:

- The Reflector diagnoses problems and suggests targeted fixes.
- The Optimizer translates those suggestions into a concrete prompt (and input) change.
- The Generator exercises the new prompt to validate whether the changes improved output.

Repeated iterations reduce ambiguity, tighten constraints, and improve factual grounding.

---

### Files of interest

- `prompt_optimizer/prompts.py` — prompt templates for generator, reflector, optimizer, judge, and the
   reviewer (the reviewer returns bulleted prompt improvements).
- `prompt_optimizer/prompt_optimizer_workflow.py` — the LangGraph workflow wiring the components.
- `prompt_optimizer/readme.md` — this file.

### Quick start (development)

1. Create a `.env` file with your provider credentials and model names, for example:

```
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
GEMINI_MODEL=gemini-1.5
GEMINI_API_KEY=...
```

2. Install Python requirements (example):

```
pip install -r requirements.txt
```

3. Run the workflow (example entrypoint):

```
python prompt_optimizer/prompt_optimizer_workflow.py
```

The script uses `python-dotenv` to load environment variables and `langgraph` to run the
state-machine workflow.

### Example usage flow

1. Start with a `generator_prompt` and `user_input`.
2. `generate` runs the Generator to produce an initial output.
3. `agentic_reflector` runs the Reflector (or `prompt_reviewer`) to produce bullets with
    concrete suggested prompt improvements.
4. `optimizer` consumes the reflector output and emits an improved `generator_prompt`.
5. `re_generate` runs the Generator again using the improved prompt; repeat until the Judge
    determines convergence or max iterations are reached.

### Example reviewer bullet suggestions (format)

The `prompt_reviewer` is intentionally strict: it returns only bullet points that begin with
`PROMPT:` and propose concrete edits. Example bullets:

- PROMPT: Add `"Support claims with one concrete example and a reference if available"` — adds
   verifiability to claims.
- PROMPT: Add constraint `"Limit to 200-300 words"` — controls verbosity.

These bullets are machine-readable and can be programmatically applied or presented to a user.

### Configuration and extensibility

- Swap LLM providers by setting provider-specific environment variables and adjusting
   `get_model` in `prompt_optimizer_workflow.py`.
- Add new reviewers/reflectors by editing `prompts.py` and wiring new response formats in
   `data_classes.py`.

### Tests and validation

- Recommended tests:
   - Unit test the reviewer to confirm it outputs only `PROMPT:` bullets.
   - Integration test a single cycle (generate -> reflect -> optimize -> regenerate) and assert
      the regenerated output is different and addresses at least one reflector suggestion.

### Next steps / TODOs

- Wire `prompt_reviewer` fully into the workflow so that its bullets are parsed and used
   by the optimizer.
- Add automated tests (unit + integration) for the reviewer and optimizer.

---

If you want, I can add a short runnable example that executes one iteration and prints the
reflector bullets and the optimized prompt. Tell me which model/provider you want to use for the
example (OpenAI or Google) and I will add it.
