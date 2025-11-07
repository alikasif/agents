# Declarative Prompt Engineering

This project contains small libraries and example code for declarative prompt engineering and prompt optimization. It includes two primary subpackages:

- `dspy/` — foundational prompt-programming utilities and prompt optimizers
- `opik/` — a small agent/optimizer example built on the declarative tooling

These modules are experimental utilities intended for learning and prototyping prompt engineering workflows and optimization techniques.

## Quick start

1. From the repository root, create and activate a Python virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the example modules to see basic behavior. From the repo root:

```powershell
python .\declarative_prompt_engineering\dspy\dspy_example.py
python .\declarative_prompt_engineering\opik\opik_agent.py
```

Note: some scripts are small experiments and may expect mock inputs or to be imported by other scripts. Inspect the top of each file for usage examples.

## Structure and file descriptions

dspy/
- foundational/
  - `dsp_reasoning.py` — helpers related to declarative signal processing style reasoning; likely contains reasoning primitives and patterns used by higher-level workflows.
  - `dspy_adapter.py` — adapter utilities to interface the `dspy` abstractions with different LLM or prompt execution backends.
  - `dspy_example.py` — runnable example demonstrating `dspy` usage patterns.
  - `dspy_module.py` — core module scaffolding for building declarative prompt components.
  - `dspy_signatures.py` — type/signature definitions and interfaces used across `dspy` components.
  - `dspy_tools.py` — utility functions to support prompt creation, formatting, or evaluation.

- optimizers/
  - `few_shot_learning.py` — utilities for few-shot prompt design and evaluation experiments.
  - `prompt_optimization_gepa.py` — an optimizer implementation (GEPA) used to search/optimize prompt variants.
  - `prompt_optimization_miprov2.py` — another optimizer implementation (MiPro v2) for prompt improvements and experiments.

opik/
- `opik_agent.py` — a small experiment agent that demonstrates applying optimization strategies (may tie together `dspy` utilities with an optimization loop).
- `opik_optimization.py` — optimization routines and helpers used by the `opik` agent.

## Usage patterns

- Explore `dspy/foundational/dspy_example.py` to see a minimal demonstration of composing declarative prompt pieces.
- Use `optimizers/*` scripts as starting points for running prompt-search or few-shot tuning loops. They typically implement a search/score/evaluate loop that can be adapted to your LLM backend.
- `opik` shows how an agent can orchestrate optimization over prompt candidates and apply results in a simple agent loop.

## Development notes

- This codebase is experimental and contains small prototypes rather than production-ready APIs. Expect rapid changes and varied styles across files.
- If you add examples, include small `readme.md` files in each subfolder showing how to run them and any required environment variables or keys.

## Suggested next steps

- Run the provided examples and inspect console output to understand patterns.
- Add short README snippets to each subpackage (e.g., `dspy/foundational/readme.md`, `dspy/optimizers/readme.md`) describing expected inputs/outputs.
- Add small unit tests around the optimizer loops to validate search behavior and scoring.

## License

This folder follows the repository license (see top-level `LICENSE`).

---
If you want, I can also generate per-file short READMEs or example invocation scripts that automatically detect an available LLM backend and run a demo.
