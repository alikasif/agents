# ACE — Agentic Context Engineering

ACE (Agentic Context Engineering) is a lightweight framework for scalable, incremental context adaptation for LLM-driven systems. ACE treats context not as a single static prompt but as a living playbook that can continuously accumulate, distill, and organize strategies. It is suitable for both offline use (e.g., system prompt optimization) and online use (e.g., memory / context adaptation during testing or deployment).

Key ideas
- Context as a structured set of entries (bullets) rather than one monolithic prompt.
- Split responsibilities across three specialized agentic roles to avoid single-model bottlenecks: Generator, Reflector, and Curator.
- Incremental Delta updates and Grow-and-Refine lifecycle to support efficient, low-latency updates and long-term scalability.

Why ACE
- Avoids brevity bias from compressing knowledge into short summaries.
- Prevents context collapse by preserving and evolving relevant items rather than re-writing everything.
- Supports parallel incremental updates and multi-epoch refinement for robust, continual learning.

Core components

- Generator
  - Generates reasoning trajectories (chains of thought, solution attempts, or multi-step outputs) for a task.
  - Marks which existing context entries were useful, neutral, or harmful during reasoning.
  - Primary role is exploration and surfacing of strategies and failure modes.

- Reflector
  - Analyzes Generator trajectories and distills specific insights from successes and failures.
  - Produces candidate incremental entries (delta entries) that capture strategies, error patterns, and domain concepts.
  - Can iterate on a candidate to refine clarity, generality, and usefulness before curation.

- Curator
  - Integrates delta entries into the main context via lightweight logical edits (not a full LLM rewrite).
  - Handles merging, deduplication, metadata updates, and conflict resolution.
  - Ensures updates are localized, enabling many updates to be merged in parallel.

Data model: entry-based context

Each context is a set of entries. An entry is a small JSON-like object with two parts:

- Metadata
  - id: unique identifier (UUID or hash)
  - score / counters: e.g., useful_count, harmful_count, last_seen
  - tags / domain / provenance

- Content
  - short text snippet: a reusable strategy, warning about a common pitfall, or a compact domain fact

This design enables:
- Localization: updates target only relevant entries.
- Fine-grained retrieval: Generators can fetch and prioritize the most relevant bullets.
- Incremental adaptation: Curator can do localized merges and in-place updates.

Incremental Delta Update

Rather than rewriting the whole context, ACE produces a compact delta context: a small set of candidate entries created by Reflector (based on Generator outputs). The Curator then:

1. Matches candidate entries to existing entries via semantic similarity (embeddings or lightweight heuristics).
2. Merges or appends — updating metadata counters (e.g., increment useful_count) or inserting new entries.
3. Optionally triggers deduplication or distillation if the context grows beyond policy limits.

Advantages
- Much lower latency and compute than full-context rewrites.
- Keeps historical knowledge intact while still allowing evolution.
- Enables parallelism: many delta contexts can be created and merged concurrently.

Grow-and-Refine lifecycle

ACE continually grows the context with new entries while periodically or conditionally performing refinement:

- Grow: append new delta entries produced by the Reflector.
- Refine: merge duplicates, prune low-utility items, and distill clusters of related entries into compact artifacts.
- Triggering: refinement can be run after each batch of updates, on a schedule, or when the context exceeds configured limits.

Deduplication and similarity

- Use semantic embeddings + a similarity threshold to detect near-duplicates.
- When duplicates are found, merge content and aggregate metadata counters.

Workflow example (single task)

1. Generator receives a task, consults context bullets, and produces a reasoning trajectory.
2. Generator annotates which bullets influenced the trajectory and whether they were helpful or harmful.
3. Reflector consumes the trajectory and annotations, producing one or more delta entries capturing lessons learned.
4. Curator ingests the delta entries, matches them to existing entries, merges or appends, and updates metadata.
5. Optional: run Grow-and-Refine to compress the context if needed.

Batch / parallel adaptation

Because delta updates are localized, multiple Generators/Reflectors can operate in parallel on the same base context and produce disjoint delta sets. The Curator can merge these concurrently, enabling scalable adaptation (useful for datasets, test-suite runs, or multi-agent deployments).

Multi-epoch adaptation

ACE supports revisiting the same task across multiple epochs: repeated exposure allows counters to accumulate, rare but valuable items to surface, and low-quality or noisy entries to be down-weighted.

Implementation notes and suggestions

- Represent the context as a lightweight vector store or simple list-of-objects persisted to disk.
- Use off-the-shelf embedding models for similarity detection and retrieval.
- Keep Curator logic deterministic and low-cost (no heavy LLM calls for merge decisions).
- Keep Reflector LLM-focused (it benefits from being able to generate concise lessons from trajectories).
- Maintain clear provenance metadata so entries can be audited and replayed.

API surface (suggested)

- generate(task, context) -> trajectory, annotations
- reflect(trajectory, annotations) -> delta_entries
- curate(delta_entries, context) -> updated_context, merge_log
- retrieve(context, query, k=10) -> ranked_entries

Edge cases and design tradeoffs

- Latency vs. quality: more Reflector iterations produce clearer entries but add latency.
- Growth control: without pruning, the playbook can grow large; configure periodic distillation.
- Consistency: parallel merges require deterministic merge rules to avoid oscillation.

Quick start (conceptual)

1. Create an initial context: a JSON file with a small set of entries.
2. Run a Generator on tasks to obtain trajectories.
3. Run Reflector to produce candidate entries.
4. Run Curator to integrate deltas and optionally run Refine.

Where to go next

- Provide example scripts: simple Generator/Reflector/Curator stubs and an end-to-end demo.
- Add tests for merging, deduplication, and metadata aggregation.
- Provide an optional web UI for browsing and editing entries.

References

- Dynamic Cheatsheet (agentic architecture): see arXiv:2504.07952 for the architectural inspiration.

License and contribution

This repository follows the license in the project root. Contributions welcome — please open issues or pull requests with reproducible changes and tests where applicable.

Contact

For questions, ping the maintainers or create an issue in the repository.
