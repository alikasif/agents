# From Vibe Coding to Agent-Assisted Coding  
## Why `agents.md` Is the Missing Control Plane

Vibe coding has become the default way many of us interact with AI for software development.

You describe what you want.  
The agent writes code.  
You iterate conversationally.  
Velocity feels incredible.

Until a few weeks later—when you realize the codebase has quietly turned into a verbose, inconsistent mess.

This post argues that **vibe coding is not wrong**, but it is **structurally incomplete**.  
To make AI coding sustainable across sessions, teams, and time, we must evolve toward **agent-assisted coding**—and the key enabler is a simple but powerful artifact: **`agents.md`**.

---

## The Vibe Coding Failure Mode

Vibe coding optimizes for *local productivity*, not *global coherence*.

Over multiple sessions, the same patterns appear:

- Abstractions multiply without justification
- Naming conventions drift
- Architectural intent gets lost
- “Helpful” helper functions accumulate
- Boilerplate grows faster than functionality

None of this happens because the agent is incompetent.  
It happens because the agent has **no durable source of truth**.

Each session becomes a fresh optimization problem.

---

## The Root Problem: No Control Plane

In traditional software teams, discipline comes from:

- Coding standards
- Architecture documents
- Reviews
- Institutional memory

In vibe coding, all of that is replaced by **chat history**, which is:

- Ephemeral
- Unstructured
- Ambiguous
- Non-enforceable

Natural language instructions like *“keep it clean”* or *“follow best practices”* are not constraints. They are vibes.

Agents don’t need more vibes.  
They need **structure**.

---

## Enter Agent-Assisted Coding

Agent-assisted coding treats AI not as a magic code generator, but as a **junior engineer with superpowers**:

- Fast
- Tireless
- Knowledgeable
- But lacking judgment unless guided

The shift is subtle but critical:

| Vibe Coding | Agent-Assisted Coding |
|------------|----------------------|
Prompt-driven | Constraint-driven |
Chat history | Persistent artifacts |
Local correctness | Global consistency |
Speed-first | Sustainability-first |

The centerpiece of this shift is **`agents.md`**.

---

## What Is `agents.md`?

`agents.md` is a **machine-readable constitution** for AI agents working on your codebase.

It is:
- Versioned
- Explicit
- Always loaded
- Non-negotiable

If `README.md` explains your project to humans,  
**`agents.md` explains your project to agents.**

---

## What Goes Into `agents.md` (and What Shouldn’t)

`agents.md` is not documentation.  
It is not a style guide essay.  
It is **a set of enforceable constraints**.

### 1. Core Engineering Principles

These are not suggestions. They are rules.


## Engineering Principles

- Prefer simple functions over abstractions
- Do not introduce new interfaces unless there are at least two concrete implementations
- Avoid generic utility modules
- Explicit code is preferred over clever code

---

### 2. Architectural Guardrails

Define where agents *can* and *cannot* operate.

## Architecture Boundaries

- Domain logic must not depend on infrastructure
- No cross-module imports outside approved dependency graph
- Shared code must live in `/core`, not `/utils`

---

### 3. Verbosity and Complexity Limits

Agents default to verbosity unless constrained.

## Code Quality Constraints

- Max function length: 40 lines
- Max file length: 300 lines
- Prefer deletion over extension
- If net LOC increases by >20%, justify explicitly

---

### 4. Forbidden Patterns (This Is Crucial)

Most teams never write this down—and pay the price.

## Forbidden Patterns

- Over-generalized helper functions
- “Just in case” abstractions
- Wrapper classes without behavior
- Rewriting files when a diff would suffice

---

### 5. Change Discipline

Force agents to reason about *impact*, not just correctness.

## Change Rules

- Work on diffs, not full-file rewrites
- Every change must explain:
  - Why it exists
  - Why it could not be simpler
  - What was intentionally not done

---

## Why `agents.md` Works (When Prompts Don’t)

### 1. Persistence Across Sessions

Chat context resets.
`agents.md` does not.

Every agent invocation starts from the same foundation.

---

### 2. Deterministic Interpretation

Natural language prompts are fuzzy.
Constraint documents are not.

Agents are far better at obeying rules than interpreting vibes.

---

### 3. Reviewable and Versioned

When an agent produces bad code, you don’t argue with it.
You update `agents.md`.

That feedback loop is everything.

---

## `agents.md` Enables Better Agent Architectures

Once you have a stable control plane, powerful patterns become possible:

### Builder + Critic Agents

* Builder writes code
* Critic checks against `agents.md`
* Critic is explicitly allowed to reject changes

### Diff-First Workflows

* Agents operate on patches
* Large rewrites require justification
* Entropy stays bounded

### Multi-Session Coherence

* Agents don’t “forget” decisions
* Architectural intent survives context windows

---

## A Hard Truth About AI Coding

> **Garbage code is not an AI problem.
> It is a governance problem.**

If you let agents infer standards implicitly, they will drift.
If you encode standards explicitly, they will comply—remarkably well.

---

## From Vibes to Systems

Vibe coding unlocked speed.
Agent-assisted coding unlocks **sustainability**.

The difference is not better models.
It’s better structure.

And today, the simplest, most effective structure we have is a single file:

> **`agents.md` — the control plane for AI-driven software engineering.**

---

If you want, I can next:

* Provide a **production-ready `agents.md` template**
* Show how to wire this into **OpenAI / LangGraph / Cursor / Copilot**
* Design a **full agent workflow** (builder, critic, verifier)
* Share **real failure cases** where lack of `agents.md` caused long-term damage

Just tell me how far you want to take it.
