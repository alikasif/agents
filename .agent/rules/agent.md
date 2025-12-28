---
trigger: always_on
---

## 1. Engineering Principles

- Prefer simple, explicit code over abstractions
- Do not generalize unless required by current use cases
- Optimize for readability and maintainability over cleverness
- Delete code when possible; fewer lines is a feature
- Design for change, not speculation

---

## 2. Architectural Guardrails

### 2.1 Dependency Rules

- Domain code MUST NOT depend on infrastructure or frameworks
- Cross-module imports are forbidden unless explicitly allowed
- Shared logic belongs in `/core`, not `/utils`

### 2.2 Abstraction Rules

- No new interfaces unless ≥ 2 concrete implementations exist
- No base classes without meaningful shared behavior
- No wrapper classes that only forward calls

---

## 3. Code Quality Constraints

### 3.1 Size & Complexity

- Max function length: 40 lines
- Max class length: 200 lines
- Max file length: 300 lines
- Cyclomatic complexity must remain low and obvious

### 3.2 Verbosity Control

- Avoid boilerplate and defensive scaffolding
- Prefer direct logic over helper indirection
- If net LOC increases by >20%, justify explicitly

---

## 4. Forbidden Patterns

The following are explicitly disallowed:

- Generic `utils`, `helpers`, or `common` modules
- Premature abstractions (“future-proofing”)
- Configuration-driven indirection without need
- Rewriting entire files when a diff suffices
- Adding comments that restate obvious code

---

## 5. Change Discipline

All changes MUST:

- Be diff-based (no full-file rewrites without justification)
- Explain:
  - Why this change exists
  - Why it could not be simpler
  - What alternatives were considered and rejected

Agents should prefer **removal** over addition.

---

## 6. Testing & Safety

- Modify or add tests only when behavior changes
- Do not add tests solely to justify new abstractions
- No snapshot tests unless unavoidable

---

## 7. What Agents Must NOT Do

- Introduce new architectural patterns
- Change naming conventions
- Reformat unrelated code
- “Clean up” code unless explicitly asked

---

## 8. Default Agent Behavior

When uncertain:
- Ask for clarification
- Choose the simplest implementation
- Do nothing rather than guess

Silence is better than incorrect assumptions.
