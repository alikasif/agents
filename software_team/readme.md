# Software Team — Multi-Agent System

A multi-agent system that simulates a software engineering team. A **Lead Agent** interprets user requirements, builds a plan, and spawns **Specialist Agents** that work in parallel — coordinating through a shared task list and plan document. **Reviewer Agents** continuously review completed work and provide feedback. A **GitHub Agent** periodically pushes committed code to the remote repository.

---

## How It Works

```
User Requirement
       │
       ▼
 ┌────────────┐
 │ Lead Agent │  ← understands requirements, creates plan & task list
 └─────┬──────┘
       │ analyzes which agents are needed
       │ spawns ONLY the required agents
       ▼
 ┌──────────────┐
 │ Project      │  ← creates top-level folder structure
 │ Structure    │     before any other agent starts
 └──────┬───────┘
        │
        ▼
 ┌───────────┬───────────┬──────────┬──────────┬───────────┐
 │ Frontend  │  Python   │   Java   │ Database │  Testing  │  Documentation
 │  Agent    │  Agent    │  Agent   │  Agent   │  Agent    │  Agent
 └─────┬─────┴─────┬─────┴────┬─────┴────┬─────┴─────┬─────┴──────┬──────┘
       │           │          │          │           │            │
       │      each agent commits code with proper messages       │
       │           │          │          │           │            │
       └───────────┴──────────┴──────────┴───────────┴────────────┘
                          ▲        │
                          │        ▼
                   ┌─────────────────┐
                   │  Shared State   │
                   │  - task_list    │       ┌─────────────────┐
                   │  - plan.md      │◄─────►│  Code Reviewers │
                   │  - project      │       │  (feedback loop)│
                   │    structure    │       └─────────────────┘
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  GitHub Agent   │  ← periodically pushes to remote
                   └─────────────────┘
```

---

## Core Concepts

### Lead Agent

The Lead Agent is the entry point. It:

1. Accepts a user requirement in natural language.
2. **Analyzes the requirement to determine which specialist agents are needed.** Not every job requires every agent. A pure backend task doesn't need a Frontend Agent. A documentation-only request doesn't need Database or Testing agents.
3. Breaks the requirement down into discrete, assignable tasks.
4. **Writes an initial plan** (starting with `# Project Name: [name]`) and **task list**.
5. **Git Strategy**: Defines the branch strategy in the plan using a `snake_case` project name.
6. **Spawns the Project Structure Agent first**, then spawns only the necessary specialist agents.
7. Monitors progress and resolves cross-agent conflicts or dependencies.

The Lead Agent does **not** write code. Its job is orchestration.

> **Key design decision:** Agent selection happens *before* task assignment. The Lead Agent first decides *who* is needed, then decides *what* each agent does. This avoids wasting resources on idle agents and keeps the system lean.

### Project Structure Agent

The Project Structure Agent runs **before any specialist agent starts**. It:

1. Reads the plan to find the **Project Name**.
2. Creates the **Dynamic Project Root** (e.g., `workspace/my_project/`) and all subfolders (`backend/`, `frontend/`, `database/`, `tests/`).
3. Initializes git, creates the branch, commits, and **pushes to remote immediately**.
4. Writes `project_structure.json` to shared state so all specialist agents know where to put their code.

The Project Structure Agent owns only the **high-level scaffold**. Inner folders and files within each module are the responsibility of the specialist agent that owns that module.

> All specialist agents **must read the project structure** from shared state before starting work. They place their code within the designated directories.

### Specialist Agents

Each specialist agent owns a domain:

| Agent         | Responsibility                                                  |
|---------------|---------------------------------------------------------------|
| Frontend      | UI components, styling, client-side logic                      |
| Python        | Python backend services, scripts, APIs                         |
| Java          | Java backend services, microservices                           |
| Database      | Schema design, migrations, queries, seed data                  |
| Testing       | Unit tests, integration tests, test plans                      |
| Documentation | API docs, user guides, inline documentation                    |

Not all agents are spawned for every job. The Lead Agent selects only the agents relevant to the current requirement. Selected agents run **independently and in parallel**. They do not call each other directly.

#### Git Awareness

Every specialist agent is **git-aware** and **test-driven**. As agents complete units of work, they:

1. **Build & Test**: Run local tests (pytest, mvn test, npm test) and linting.
2. **Fix Failures**: Code is NOT committed if tests fail.
3. **Commit**: Commit code locally with a clear concept message (e.g., `feat(frontend): add login form`).
4. **Interface First**: Define APIs/Interfaces before implementation. Backend generates `openapi.json` for Frontend to consume.

Agents receive **GitHub details** from the Lead Agent. The Project Structure Agent pushes the initial scaffold. The GitHub Agent handles subsequent syncs.

### Code Reviewer Agents

Reviewer Agents operate as a **continuous feedback loop**. They watch `task_list.json` for tasks marked `done` and review the output.

| Reviewer             | Scope                                                        |
|----------------------|--------------------------------------------------------------|
| Frontend Reviewer    | UI quality, accessibility, responsiveness, component design  |
| Backend Reviewer     | API design, error handling, performance, security            |
| Architecture Reviewer| Module boundaries, dependency direction, design patterns     |
| Database Reviewer    | Schema design, query performance, migrations, data integrity |

**Review workflow:**

1. A specialist agent marks a task `done`.
2. The relevant reviewer picks it up and reviews the output files.
3. If the review passes → task stays `done`.
4. If the review has feedback → reviewer sets the task to `review_feedback` with comments in `task_list.json`. The specialist agent picks it up, fixes it, and re-submits.

Reviewers are spawned selectively — only reviewers matching the active specialist agents are started.

### GitHub Agent

The GitHub Agent runs in the background and handles all remote git operations:

1. **Periodically scans** for new local commits from specialist agents.
2. **Pushes to remote** on a configurable interval.
3. Tracks push status in shared state so the Lead Agent knows what's been synced.

The GitHub Agent is the **only** agent that talks to the remote repository. This avoids push conflicts between specialist agents.

---

## Shared State (Coordination Layer)

Agents coordinate through shared artifacts:

- **`task_list.json`** — structured list of tasks with status, assignee, dependencies, review feedback, and outputs.
- **`plan.md`** — high-level plan describing the system being built, module boundaries, and integration points.
- **`project_structure.json`** — top-level directory layout created by the Project Structure Agent. All specialist agents read this before starting.

Every agent **reads** shared state before starting work and **writes** updates when:

- A task is picked up (`status: in_progress`).
- A task is completed (`status: done`) with output paths.
- A task is blocked and needs another agent's output (`status: blocked`, `blocked_by: <task_id>`).
- A reviewer provides feedback (`status: review_feedback`).
- The plan needs amendment (e.g., a schema change that affects the API contract).

This is the **only** coordination mechanism. No direct agent-to-agent messaging.

---

## Execution Flow

```
 1. User submits requirement
 2. Lead Agent analyzes requirement
 3. Lead Agent determines which specialist agents are needed
    - e.g. "Build a Python CLI tool" → Python Agent + Testing Agent only
    - e.g. "Full-stack web app" → Frontend + Python + Database + Testing + Docs
 4. Lead Agent writes plan.md and task_list.json
 5. Lead Agent spawns Project Structure Agent
    - Creates top-level directories, git init, config files
    - Writes project_structure.json to shared state
 6. Lead Agent spawns selected specialist agents + matching reviewers + GitHub Agent
 7. Each specialist agent:
    a. Reads project_structure.json to know where to place code
    b. Reads task_list.json, picks its assigned tasks
    c. Reads plan.md for context and contracts
    d. Executes tasks, writes code/artifacts
    e. Commits code locally with descriptive commit messages
    f. Updates task_list.json (status, outputs)
    g. Updates plan.md if contracts change
 8. Reviewer agents watch for completed tasks:
    a. Review code when task is marked done
    b. Approve or send back with feedback
    c. Specialist agent fixes and re-submits if needed
 9. GitHub Agent periodically pushes local commits to remote
10. Lead Agent polls for completion
11. Lead Agent resolves conflicts, re-plans if needed
12. Done when all tasks are marked complete and reviews pass
```

---

## Task List Schema

Each task in `task_list.json` follows this structure:

```json
{
  "id": "task-003",
  "title": "Create users table migration",
  "assignee": "database",
  "status": "todo",
  "priority": "high",
  "dependencies": [],
  "blocked_by": null,
  "outputs": [],
  "review_feedback": null,
  "notes": "Must include created_at and updated_at timestamps."
}
```

**Status values:** `todo` → `in_progress` → `done` → `review_feedback` → `in_progress` (fix) → `done` | `blocked`

---

## Plan Document

`plan.md` is a living document that contains:

- **Goal** — what the system should do when complete.
- **Modules** — each module, its owner agent, and its responsibilities.
- **Contracts** — API schemas, database schemas, shared interfaces that cross module boundaries.
- **Decisions** — any design decisions made during execution, with rationale.
- **GitHub Details** — repo URL, branch strategy, auth reference.

Any agent can append to the Decisions section. Only the Lead Agent restructures the plan.

---

## Agent Coordination Rules

1. **Read project structure first.** Every specialist agent reads `project_structure.json` before writing any code.
2. **Read before write.** Always read the latest shared state before making changes.
3. **Commit often.** Commit each meaningful unit of work with a clear message.
4. **Atomic updates.** Use file locking or compare-and-swap to avoid lost writes.
5. **Declare dependencies.** If your task depends on another agent's output, set `blocked_by`.
6. **Announce contract changes.** If you change a schema or API, update `plan.md` contracts section and add a note so dependent agents can adapt.
7. **Act on review feedback.** When a task is set to `review_feedback`, the assignee must address comments and re-submit.
8. **No direct communication.** All coordination flows through shared state.

---

## Project Structure

```
software_team/
├── readme.md
├── prompts/                    # Agent Prompt Definitions (.py)
│   ├── lead_agent.py
│   ├── project_structure_agent.py
│   ├── python_coder_agent.py
│   ├── java_coder_agent.py
│   ├── frontend_agent.py
│   └── ... (testing/reviewers)
├── software_subagents_md/      # Subagent Instructions (.agent.md)
│   ├── lead-agent.agent.md
│   ├── planning-subagent.agent.md
│   ├── project-structure-subagent.agent.md
│   ├── python-coder-subagent.agent.md
│   ├── frontend-subagent.agent.md
│   └── ...
├── shared/
│   ├── task_list.json
│   ├── plan.md
│   ├── project_structure.json
│   └── api/                    # Shared API Contracts (OpenAPI/TS)
└── workspace/
    └── [ProjectName]/          # Dynamic Root Folder
        ├── backend/
        ├── frontend/
        ├── database/
        ├── tests/
        └── docs/
```

---

## Example

**User requirement:**

> Build a REST API for a todo app with a React frontend and PostgreSQL database.

**Lead Agent analyzes and selects agents:**

- **Specialist:** Frontend, Python, Database, Testing, Documentation. The Java Agent is **not** spawned.
- **Reviewers:** Frontend Reviewer, Backend Reviewer, Architecture Reviewer, Database Reviewer.
- **Infrastructure:** Project Structure Agent, GitHub Agent.

**Execution:**

1. Project Structure Agent creates: `frontend/`, `backend/`, `database/`, `tests/`, `docs/`, `.gitignore`, `README.md`. Writes `project_structure.json`.
2. All specialist agents read `project_structure.json`, then start in parallel.
3. Database Agent creates migration, commits: `feat(db): add todos table migration`, marks task done.
4. Database Reviewer reviews the migration, approves.
5. Python Agent reads the schema from database output, implements CRUD endpoints, commits: `feat(api): add todo CRUD endpoints`.
6. Backend Reviewer reviews the API, requests error handling improvements → task set to `review_feedback`.
7. Python Agent fixes, re-commits: `fix(api): add validation and error responses`, re-submits.
8. GitHub Agent pushes all local commits to remote.
9. Process continues until all tasks are done and all reviews pass.

---

## Tech Stack

- **LLM backbone** — each agent wraps an LLM (e.g., Gemini, GPT, Claude) with domain-specific prompts.
- **Shared state** — file-based with locking (`core/state.py`).
- **Git operations** — via `core/git.py`, wrapping `git` CLI or `GitPython`.
- **Execution** — Python `asyncio` or `multiprocessing` for parallel agent execution.

---

## How to Use

To use this agent system in your project:

1.  **Setup the Agent Configs**:
    -   Create a folder `.github/agents` under your project root.
    -   Copy all `.agent.md` files from `software_subagents_md/` into `.github/agents/`.

2.  **Start the Lead Agent**:
    -   Open VS Code in your project.
    -   Select **Lead Agent** from the agent selection menu (or `@Lead Agent` in chat).

3.  **Execute**:
    -   Type your problem statement (e.g., "Build a Python CLI to analyze stock prices").
    -   Watch the Lead Agent analyze, plan, and spawn specialist agents to build your software!

