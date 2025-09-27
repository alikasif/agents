
# Evals — Testing Semantic Kernel Workflows Using  Evaluations Frameworks

This folder contains materials and small utilities to evaluate and benchmark different evaluation frameworks against agent workflows and automation built using Microsoft's Semantic Kernel and related agent patterns in this repository.

Purpose
-------
The goal of `evals/` is to provide reproducible experiments, example prompts, transcripts, and helper scripts that let you compare evaluation frameworks and tooling when applied to:

- multi-step agent workflows
- tool-augmented LLM agents
- automated orchestration built with Semantic Kernel primitives

This is not a single monolithic test runner. Instead it collects examples, transcripts, and lightweight harnesses you can use to measure quality, correctness, cost, and latency of agent behaviors across different evaluation approaches.

What you'll find here
---------------------

- data_classes.py — shared datatypes used by evaluation harnesses (if present)
- semantic_store.py — small helpers for storing/retrieving transcripts and evaluation artifacts
- simple_rag.py — minimal retrieval-augmented-generation example used in some experiments
- readme.md — (this file) guidance and quickstart
- data/ and transcripts/ — example input datasets, agent outputs, and transcripts used for evaluation

Design principles
-----------------

1. Reproducible: keep experiments small, pinned, and easy to run locally.
2. Compare apples-to-apples: provide the same prompts, seeds, and inputs across frameworks.
3. Lightweight: avoid heavy infra dependencies; prefer small scripts and fixtures.
4. Extensible: make it easy to add new evaluation metrics, frameworks, or experiments.

Quickstart
----------

1. Install dependencies for the repository (see top-level `requirements.txt` or `pyproject.toml`).

	- On a Python environment with pip:

	  pip install -r requirements.txt

2. Inspect the example transcripts and prompt files in this directory. Many experiments are self-contained and have instructions in nearby files.

3. Run a simple example (if provided) from the project root. For example, to run the simple RAG example used in some evals:

	python -m evals.simple_rag

	(Adjust the module path as needed depending on how you run Python in this workspace.)

4. To add an evaluation, create a small harness that:

	- Takes a fixed input set / seed
	- Runs the agent workflow (or replays a transcript)
	- Produces structured outputs (JSONL recommended)
	- Computes metrics or emits artifacts consumable by evaluation frameworks

Example evaluation checklist
----------------------------

- Reproducibility: fixed random seed, clear environment variables
- Inputs: include CSV/JSON fixtures in `data/`
- Outputs: write JSONL with one object per run, include metadata (prompt, model, timestamp)
- Metrics: provide at least one automated metric (e.g., exact match, BLEU, or a domain-specific verifier)
- Cost/latency: capture timing and token usage when available

Adding a new framework
----------------------

If you want to compare a new evaluation framework against the examples here:

1. Add an adapter that converts the output JSONL from our harness into the framework's expected format.
2. Add a small script under `evals/` that runs the adapter and invokes the framework on the exported artifacts.
3. Commit the adapter and a README describing how to reproduce the comparison locally.

Contributing
------------

Contributions are welcome. When adding experiments or adapters:

- Keep experiments minimal and well-documented.
- Add small datasets (or pointers) and expected outputs.
- Document exact steps to reproduce and the software versions used.

Acknowledgements
----------------

This repository experiments with Semantic Kernel-based automation and agentic patterns. The `evals/` folder aims to be a neutral place to compare external evaluation tooling on top of those workflows.

License
-------

See the repository root `LICENSE` for licensing details.
