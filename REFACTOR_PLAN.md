# Project Refactoring Plan

## Goal

Standardize all sub-projects to follow a consistent structure:

```
<sub_project>/
├── prompts.py        # All prompts using XML-based syntax
├── tools.py          # All tool definitions
├── agents.py         # Agent definitions/creation
├── data_classes.py   # Pydantic models, TypedDicts, dataclasses
├── runner.py         # Entry point / orchestration
├── readme.md         # Documentation
└── __init__.py       # Package init
```

### Conventions

| File | Convention |
|------|-----------|
| `prompts.py` | All prompts as `UPPER_SNAKE_CASE` string constants using XML-based syntax (`<agent>`, `<instructions>`, `<tools>`, `<context>`, `<output_format>`, `<guardrails>`, `<examples>`) |
| `tools.py` | All tool functions with appropriate framework decorators (`@function_tool`, `@tool`, etc.) |
| `agents.py` | Agent class/factory definitions, wiring prompts + tools together |
| `data_classes.py` | All Pydantic `BaseModel`, `TypedDict`, and `@dataclass` definitions |
| `runner.py` | `main()` function with `if __name__ == "__main__"` guard |
| `__init__.py` | Public API exports |

---

## Reference Projects (Already Well-Structured)

These projects closely follow the target structure and serve as templates:

- **`browser_agent`** — XML prompts in `prompts.py`, `@function_tool` in `tools.py`, agent in `agent.py`, runner in `runner.py`
- **`command_line_agent`** — XML prompts, clean separation, includes `hooks.py` pattern
- **`test_driven_coding_agent`** — XML prompts, `@function_tool` tools, clean 4-file split
- **`ai_blogger/agentic`** — proper separation (prompts, tools, agent, runner) though prompts not XML

---

## Non-Agentic Projects (No Refactoring Needed)

These are utility/infra projects with no prompts, agents, or tools:

| Project | Reason |
|---------|--------|
| `course_browser` | Pure scraping + ranking, no LLM |
| `quantization_tool` | Numerical computation only |
| `llm_fine_tuning` | HuggingFace training scripts |
| `msft_foundry_local` | Local model management demo |
| `mcp/fastmcp/composition` | MCP server/client infra demo |
| `llm_key_checker` | API key validation utility |
| `automation` | Empty (readme only) |
| `agentic_recommendation_engine` | Empty folder |
| `multi_agent_debate` | Empty folder |
| `vibe_coding` | Empty folder |
| `code_refactorer` | Empty (readme only) |
| `books` | Documentation / book content |

---

## Detailed Per-Project Task List

---

### 1. `a2a_communication`

**Current State:**
- 4 agent files, each with **inline prompts** (plain text)
- Tools are inline methods (`list_remote_agents`, `send_message`)
- Uses 3 different SDKs: Google ADK, Autogen, OpenAI Agents SDK
- No `prompts.py`, `tools.py`, `agents.py`, or `data_classes.py`

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 1.1 | Create `prompts.py` | Extract inline `instruction=` / `system_message=` / `instructions=` from all 4 agent files. Convert each to XML syntax. Constants: `INCIDENT_COMMANDER_PROMPT`, `INCIDENT_COMMS_PROMPT`, `INCIDENT_POST_MORTEM_PROMPT`, `INCIDENT_TRIAGE_PROMPT` |
| 1.2 | Create `tools.py` | Extract `list_remote_agents()` and `send_message()` from `incident_commander_agent.py` |
| 1.3 | Create `agents.py` | Consolidate all agent definitions (currently in 4 separate files) into one file. Import prompts from `prompts.py`, tools from `tools.py` |
| 1.4 | Create `data_classes.py` | Define models for incident data if used |
| 1.5 | Create `runner.py` | Move `multi_agent_trigger.py` logic into `runner.py` with `main()` + `__main__` guard |
| 1.6 | Delete old files | Remove `incident_commander_agent.py`, `incident_comms_agent.py`, `incident_post_mortem_agent.py`, `incident_triage_agent.py`, `multi_agent_trigger.py` |
| 1.7 | Create `__init__.py` | Export public API |

**Files changed:** 5 deleted, 5 created

---

### 2. `ACE`

**Current State:**
- `prompts.py` exists (plain text with `.format()`)
- `tools.py` exists (LangChain `Tool`)
- Agent logic in `prompt_optimizer_workflow.py` (LangGraph StateGraph)
- `data_classes.py` exists
- `curator.py`, `generator.py`, `reflector.py` are **empty placeholder files**

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 2.1 | Update `prompts.py` | Convert `reasoning_trajectory_prompt`, `reflector_prompt`, `curator_prompt` from plain text to XML syntax |
| 2.2 | Create `agents.py` | Extract agent node functions (`generate`, `agentic_reflector`, `agentic_optimizer`, `re_generate`, `judge`) and `create_react_agent` calls from `prompt_optimizer_workflow.py` |
| 2.3 | Create `runner.py` | Extract `run()` function and graph construction from `prompt_optimizer_workflow.py` |
| 2.4 | Delete empty files | Remove `curator.py`, `generator.py`, `reflector.py` (empty placeholders) |
| 2.5 | Delete old file | Remove `prompt_optimizer_workflow.py` (split into `agents.py` + `runner.py`) |

**Files changed:** 4 deleted, 2 created, 1 updated

---

### 3. `agentic_trading`

**Current State:**
- `prompts.py` exists (683 lines, plain text)
- `council_prompt.py` — **second prompt file** (should be merged)
- `tools.py` exists (`@function_tool`)
- `council.py` has council agent, `research_agent.py` has research agent + runner
- `data_classes.py` exists

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 3.1 | Update `prompts.py` | Convert all prompts to XML syntax. Merge `council_prompt.py` content (`COUNCIL_SYSTEM_PROMPT`) into `prompts.py` |
| 3.2 | Create `agents.py` | Move agent definitions from `council.py` and `research_agent.py` into `agents.py` |
| 3.3 | Create `runner.py` | Extract `__main__` runner logic from `research_agent.py` |
| 3.4 | Delete old files | Remove `council.py`, `council_prompt.py`, `research_agent.py` |

**Files changed:** 3 deleted, 2 created, 1 updated

---

### 4. `ai_blogger/agentic`

**Current State:**
- `prompts.py` exists (plain text)
- `tools.py` exists (`@function_tool`)
- `blog_writer_agent.py` has agent definitions
- `runner.py` exists
- `structured_output.py` has Pydantic models

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 4.1 | Update `prompts.py` | Convert `analyst_prompt`, `research_prompt`, `blogger_prompt`, `editor_prompt` to XML syntax |
| 4.2 | Rename `blog_writer_agent.py` → `agents.py` | |
| 4.3 | Rename `structured_output.py` → `data_classes.py` | |
| 4.4 | Create `__init__.py` | |

**Files changed:** 2 renamed, 1 updated, 1 created

---

### 5. `ai_blogger/langgraph`

**Current State:**
- `prompt.py` (singular, LangChain `PromptTemplate`, plain text)
- `tools.py` exists (`@tool`)
- 4 separate agent files: `analyst_agent.py`, `blog_writer_agent.py`, `editor_agent.py`, `researcher_agent.py`
- `data_classes.py` exists
- `llm.py` utility
- `runner.py` exists

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 5.1 | Rename `prompt.py` → `prompts.py` | Convert prompts to XML syntax |
| 5.2 | Create `agents.py` | Consolidate `AnalystAgent`, `ResearcherAgent`, `BloggerAgent`, `EditorAgent` from 4 files into one |
| 5.3 | Delete old agent files | Remove `analyst_agent.py`, `blog_writer_agent.py`, `editor_agent.py`, `researcher_agent.py` |
| 5.4 | Keep `llm.py` and `utils.py` | Utility files are fine |

**Files changed:** 4 deleted, 1 renamed+updated, 1 created

---

### 6. `ai_solution_architect`

**Current State:**
- `deep_agent_prompt.py` (prompts, plain text — wrong filename)
- `deep_agent_v2.py` (agent + tools + runner all-in-one)
- `state_data_classes.py` (data classes — wrong filename)

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 6.1 | Rename `deep_agent_prompt.py` → `prompts.py` | Convert `system_prompt`, `review_prompt`, `refine_prompt` to XML syntax |
| 6.2 | Create `tools.py` | Extract `GoogleSerperAPIWrapper` tool setup from `deep_agent_v2.py` |
| 6.3 | Create `agents.py` | Extract `DeepAgent` class from `deep_agent_v2.py` |
| 6.4 | Create `runner.py` | Extract `__main__` logic from `deep_agent_v2.py` |
| 6.5 | Rename `state_data_classes.py` → `data_classes.py` | |
| 6.6 | Delete old file | Remove `deep_agent_v2.py` (split into agents + tools + runner) |

**Files changed:** 1 deleted, 2 renamed, 3 created

---

### 7. `ai_stock_agent`

**Current State:**
- **No separation at all** — prompts, tools, agents all inline
- `agent.py` has prompts + tool functions + agent logic
- `financial_analysis_agent.py` has `BaseTool` subclasses + inline prompts + agent
- `app.py` is Streamlit runner

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 7.1 | Create `prompts.py` | Extract all inline prompts from `agent.py` (`explain_top_picks` f-string, `ChatPromptTemplate` in `analyze_data`) and `financial_analysis_agent.py` (tool descriptions, system messages). Convert to XML syntax |
| 7.2 | Create `tools.py` | Extract `BaseTool` subclasses (`InsightGeneratorTool`, etc.) from `financial_analysis_agent.py` and tool functions from `agent.py` |
| 7.3 | Create `agents.py` | Extract agent creation logic (`initialize_agent`, agent wiring) from both files |
| 7.4 | Create `data_classes.py` | Extract any Pydantic models |
| 7.5 | Rename `app.py` → `runner.py` | Keep Streamlit runner |
| 7.6 | Delete old files | Remove `agent.py`, `financial_analysis_agent.py` |

**Files changed:** 2 deleted, 4 created, 1 renamed

---

### 8. `api_chatbot`

**Current State:**
- `agent.py` has inline prompt + tool function + agent definition (Autogen)
- `api_bot.py` is empty
- `main.py` is runner
- No `prompts.py`, `tools.py`, or `data_classes.py`

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 8.1 | Create `prompts.py` | Extract inline `system_message=` from `agent.py`. Convert to XML syntax |
| 8.2 | Create `tools.py` | Extract `read_yaml_spec()` function from `agent.py` |
| 8.3 | Rename `agent.py` → `agents.py` | Keep agent definition, import prompts + tools |
| 8.4 | Rename `main.py` → `runner.py` | |
| 8.5 | Delete `api_bot.py` | Empty placeholder |

**Files changed:** 1 deleted, 2 created, 2 renamed

---

### 9. `arguing_agents`

**Current State:**
- `prompts.py` exists (plain text)
- `tools.py` exists (`@function_tool`)
- `arg_agents.py` has agents + runner

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 9.1 | Update `prompts.py` | Convert `PROPONENT_SYSTEM_PROMPT`, `OPPONENT_SYSTEM_PROMPT` to XML syntax |
| 9.2 | Rename `arg_agents.py` → `agents.py` | Keep agent definitions |
| 9.3 | Create `runner.py` | Extract `__main__` block (debate loop) from `arg_agents.py` |
| 9.4 | Create `data_classes.py` | Extract any inline models |

**Files changed:** 1 renamed, 1 updated, 2 created

---

### 10. `autonomous_expert_agent`

**Current State:**
- `prompts.py` exists (**already has XML-like tags** — `<example>`, `<reasoning>`)
- `tools.py` exists (empty docstring only)
- `planning_agent.py` has agent + runner

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 10.1 | Update `prompts.py` | Enhance XML structure to full standard (`<agent>`, `<instructions>`, `<tools>`, etc.) |
| 10.2 | Populate `tools.py` | Add actual tool implementations or remove if truly unused |
| 10.3 | Rename `planning_agent.py` → `agents.py` | Keep agent definition |
| 10.4 | Create `runner.py` | Extract `__main__` block from `planning_agent.py` |

**Files changed:** 1 renamed, 1 updated, 1 created

---

### 11. `browser_agent`

**Current State: ✅ ALREADY WELL-STRUCTURED**
- `prompts.py` — Full XML syntax
- `tools.py` — `@function_tool`
- `agent.py` — Agent class
- `runner.py` — Entry point

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 11.1 | Rename `agent.py` → `agents.py` | Consistency |
| 11.2 | Create `data_classes.py` | If any inline models exist |
| 11.3 | Create `__init__.py` | |

**Files changed:** 1 renamed, 1-2 created

---

### 12. `budget_aware_tool_use`

**Current State:**
- `prompts.py` exists (XML tags: `<think>`, `<tool_code>`, `<answer>`)
- `tools.py` exists (plain functions, not decorated)
- `react_agent_openai.py` has agent class + runner
- `budget_tracker.py` + `config.py` have data classes

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 12.1 | Update `prompts.py` | Enhance to full XML standard structure |
| 12.2 | Rename `react_agent_openai.py` → `agents.py` | |
| 12.3 | Create `runner.py` | Extract runner logic from `react_agent_openai.py` |
| 12.4 | Rename `budget_tracker.py` + `config.py` → merge into `data_classes.py` | Consolidate `BudgetTracker`, `BudgetState`, config dataclasses |
| 12.5 | Rename `example_usage.py` | Merge into `runner.py` or delete |

**Files changed:** 3 renamed/merged, 1 created, 1 updated

---

### 13. `chain_of_agents`

**Current State:**
- `prompts.py` exists (plain text)
- `manager_agent.py` + `workers.py` have agents
- `data_classes.py` exists
- `runner.py` exists
- `chunker.py`, `llm.py` are utilities

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 13.1 | Update `prompts.py` | Convert to XML syntax |
| 13.2 | Create `agents.py` | Merge `ManagerAgent` (from `manager_agent.py`) and `WorkerAgent` (from `workers.py`) |
| 13.3 | Delete old files | Remove `manager_agent.py`, `workers.py` |
| 13.4 | Keep utilities | `chunker.py`, `llm.py` remain as-is |
| 13.5 | Rename `graph.py` | Consider merging into `runner.py` if it's the workflow graph |

**Files changed:** 2 deleted, 1 created, 1 updated

---

### 14. `command_line_agent`

**Current State: ✅ ALREADY WELL-STRUCTURED**
- `prompts.py` — Full XML syntax
- `tools.py` — `@function_tool`
- `agent.py` — Agent class
- `runner.py` — Entry point
- `hooks.py` — Extra utility

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 14.1 | Rename `agent.py` → `agents.py` | Consistency |
| 14.2 | Create `__init__.py` | |

**Files changed:** 1 renamed, 1 created

---

### 15. `data_chatbot`

**Current State:**
- `sql_generator.py` has **inline prompts** + raw OpenAI API call
- `db_metadata.py` has DB utilities
- `main.py` is runner
- No `prompts.py`, `tools.py`, `agents.py`, or `data_classes.py`

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 15.1 | Create `prompts.py` | Extract `system_prompt` and `user_prompt` from `sql_generator.py`. Convert to XML syntax |
| 15.2 | Create `tools.py` | Extract DB query execution functions if applicable |
| 15.3 | Create `agents.py` | Extract LLM call logic from `sql_generator.py` into an agent class |
| 15.4 | Rename `main.py` → `runner.py` | |
| 15.5 | Keep `db_metadata.py` | Utility file, or rename to `utils.py` |

**Files changed:** 3 created, 1 renamed, 1 refactored

---

### 16. `design_patterns/Plan_Execute`

**Current State:**
- `prompt.py` (singular, some prompts — plain text)
- `content_writer.py` has agent + inline `planner_prompt` + runner + data classes

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 16.1 | Rename `prompt.py` → `prompts.py` | Move **all** prompts here (including inline `planner_prompt` from `content_writer.py`). Convert to XML |
| 16.2 | Create `agents.py` | Extract agent/node definitions from `content_writer.py` |
| 16.3 | Create `data_classes.py` | Extract TypedDict state + Pydantic models from `content_writer.py` |
| 16.4 | Create `runner.py` | Extract graph construction + `__main__` from `content_writer.py` |
| 16.5 | Delete old file | Remove `content_writer.py` |

**Files changed:** 1 deleted, 1 renamed, 3 created

---

### 17. `design_patterns/ReACT`

**Current State:**
- `prompt.py` (plain text)
- `deep_researcher.py` has agent + **inline tools** + runner

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 17.1 | Rename `prompt.py` → `prompts.py` | Convert to XML syntax |
| 17.2 | Create `tools.py` | Extract `_google_search()` from `deep_researcher.py` |
| 17.3 | Rename `deep_researcher.py` → `agents.py` | Keep `ReACTAgent` class |
| 17.4 | Create `runner.py` | Extract `__main__` block |

**Files changed:** 2 renamed, 2 created

---

### 18. `design_patterns/Reflexion`

**Current State:**
- `prompt.py` (LangChain `PromptTemplate`, plain text)
- `reflection_agent.py` has agent + inline data classes + runner
- `prompt_executor.py` is a secondary runner

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 18.1 | Rename `prompt.py` → `prompts.py` | Convert `PromptTemplate` strings to XML syntax string constants |
| 18.2 | Rename `reflection_agent.py` → `agents.py` | |
| 18.3 | Create `data_classes.py` | Extract inline Pydantic models from `reflection_agent.py` |
| 18.4 | Create `runner.py` | Merge runner logic from `reflection_agent.py` and `prompt_executor.py` |
| 18.5 | Delete `prompt_executor.py` | Merge into `runner.py` |

**Files changed:** 1 deleted, 2 renamed, 2 created

---

### 19. `design_patterns/ReWoo`

**Current State:**
- `prompt.py` (plain text)
- `rewoo_agent.py` has agent + **inline tools** + runner

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 19.1 | Rename `prompt.py` → `prompts.py` | Convert to XML syntax |
| 19.2 | Create `tools.py` | Extract `_google_search()`, `_llm_call()` from `rewoo_agent.py` |
| 19.3 | Rename `rewoo_agent.py` → `agents.py` | |
| 19.4 | Create `runner.py` | Extract `__main__` block |

**Files changed:** 2 renamed, 2 created

---

### 20. `google_map_agent`

**Current State:**
- `prompts.py` exists (plain text) — but some prompts **still inline** in agent file
- `google_map_apis.py` has tools (wrong filename)
- `address_router_agent_adk.py` has agents + inline prompts + runner
- `data_classes.py` exists

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 20.1 | Update `prompts.py` | Move inline agent instructions from `address_router_agent_adk.py` into `prompts.py`. Convert all to XML syntax |
| 20.2 | Rename `google_map_apis.py` → `tools.py` | |
| 20.3 | Rename `address_router_agent_adk.py` → `agents.py` | Remove inline prompts, import from `prompts.py` |
| 20.4 | Create `runner.py` | Extract `__main__` block from `address_router_agent_adk.py` |

**Files changed:** 2 renamed, 1 updated, 1 created

---

### 21. `inbox_chatbot`

**Current State:**
- `prompts.py` exists (plain text, multiple versions v2/v3/v4)
- `tools.py` exists (`@function_tool`)
- Two agent files: `gmail_chatbot_adk.py`, `gmail_chatbot_openai.py`
- `data_classes.py` exists

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 21.1 | Update `prompts.py` | Convert all prompts to XML syntax. Clean up versioning (keep latest or rename clearly) |
| 21.2 | Create `agents.py` | Merge agent definitions from `gmail_chatbot_adk.py` and `gmail_chatbot_openai.py` |
| 21.3 | Create `runner.py` | Extract runner logic from both chatbot files |
| 21.4 | Delete old files | Remove `gmail_chatbot_adk.py`, `gmail_chatbot_openai.py` |

**Files changed:** 2 deleted, 2 created, 1 updated

---

### 22. `multiturn_conversation_summarization`

**Current State:**
- `prompts.py` exists (plain text, has typo `CHTABOT_PROMT`)
- `tools.py` exists (`@function_tool`)
- `chatbot.py` has agent + runner
- `data_classes.py` exists

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 22.1 | Update `prompts.py` | Convert to XML syntax. Fix typo: `CHTABOT_PROMT` → `CHATBOT_PROMPT` |
| 22.2 | Rename `chatbot.py` → `agents.py` | Keep agent definition |
| 22.3 | Create `runner.py` | Extract `__main__` logic from `chatbot.py` |

**Files changed:** 1 renamed, 1 updated, 1 created

---

### 23. `prompt_generator`

**Current State:**
- **No `prompts.py`** — all prompts inline in 3 agent files
- No `tools.py` — agents used as tools via `.as_tool()`
- Inline Pydantic models in each file
- Runner in `prompt_manager.py`

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 23.1 | Create `prompts.py` | Extract `PROMPT_GENERATION_INSTRUCTIONS`, `JUDGE_INSTRUCTIONS`, `GENERATION_MANAGER_INSTRUCTIONS` from all 3 files. Convert to XML |
| 23.2 | Create `data_classes.py` | Extract `PromptAgentOutput`, `CallingAgentOutput`, `Judgement`, `FinalJudgement` |
| 23.3 | Create `agents.py` | Merge agent definitions from `prompt_generator_agent.py`, `prompt_judging_agent.py`, `prompt_manager.py` |
| 23.4 | Create `runner.py` | Extract `generate_and_judge_prompts()` + `__main__` from `prompt_manager.py` |
| 23.5 | Delete old files | Remove `prompt_generator_agent.py`, `prompt_judging_agent.py`, `prompt_manager.py` |

**Files changed:** 3 deleted, 4 created

---

### 24. `prompt_optimizer`

**Current State:**
- `prompts.py` exists (plain text, `.format()`)
- `tools.py` exists (LangChain `Tool`)
- `data_classes.py` exists
- `prompt_optimizer_workflow.py` has agents + runner

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 24.1 | Update `prompts.py` | Convert to XML syntax |
| 24.2 | Create `agents.py` | Extract node functions + `create_react_agent` calls from `prompt_optimizer_workflow.py` |
| 24.3 | Create `runner.py` | Extract `run()` + graph construction + `__main__` from `prompt_optimizer_workflow.py` |
| 24.4 | Delete old file | Remove `prompt_optimizer_workflow.py` |

**Files changed:** 1 deleted, 2 created, 1 updated

---

### 25. `tri_layer_reflection`

**Current State:**
- `prompts.py` exists (plain text)
- `tools.py` exists (`@tool`)
- `data_classes.py` exists
- `tri_layer_agents.py` has agents + module-level runner (no `__main__` guard)

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 25.1 | Update `prompts.py` | Convert to XML syntax |
| 25.2 | Rename `tri_layer_agents.py` → `agents.py` | |
| 25.3 | Create `runner.py` | Extract module-level execution into `main()` + `__main__` guard |

**Files changed:** 1 renamed, 1 updated, 1 created

---

### 26. `train_itenary`

**Current State:**
- `agents/prompts.py` exists (nested, plain text)
- `agents/irctc_agent.py` has agent + runner
- Tools come from MCP server (not local)
- Utilities in `utils.py`
- Non-agentic graph logic in `itenary_builder.py`, `train_graph_builder.py`

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 26.1 | Flatten structure | Move `agents/prompts.py` → `prompts.py` (root). Convert to XML |
| 26.2 | Move `agents/irctc_agent.py` → `agents.py` | |
| 26.3 | Create `runner.py` | Extract runner from `agents/irctc_agent.py`. Include MCP server setup |
| 26.4 | Create `data_classes.py` | Define models for train/route data |
| 26.5 | Keep utilities | `utils.py`, `itenary_builder.py`, `train_graph_builder.py`, `graph_persister.py` as-is |
| 26.6 | Delete `agents/` folder | After extraction |

**Files changed:** folder restructured, 3 created, 1 updated

---

### 27. `test_driven_coding_agent`

**Current State: ✅ ALREADY WELL-STRUCTURED**
- `prompts.py` — XML syntax
- `tools.py` — `@function_tool`
- `agent.py` — Agent class
- `runner.py` — Entry point

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 27.1 | Rename `agent.py` → `agents.py` | Consistency |
| 27.2 | Create `data_classes.py` | Extract any inline models from tools |
| 27.3 | Create `__init__.py` | |

**Files changed:** 1 renamed, 1-2 created

---

### 28. `custom_agent/blog_writers`

**Current State:**
- `prompt.py` (singular, f-string templates)
- `tools.py` (plain functions, not decorated)
- 3 agent files: `blog_writer_react_agent.py`, `blog_writer_reflection_agent.py`, `blog_writing_planner_agent.py`
- `data_classes.py` exists

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 28.1 | Rename `prompt.py` → `prompts.py` | Convert to XML syntax |
| 28.2 | Create `agents.py` | Merge all 3 agent classes into one file |
| 28.3 | Create `runner.py` | Extract `__main__` blocks |
| 28.4 | Delete old files | Remove 3 separate agent files |

**Files changed:** 3 deleted, 1 renamed, 2 created

---

### 29. `mcp_utcp_tools`

**Current State:**
- 3 demo files with **inline trivial prompts**
- Tools from MCP/UTCP servers + `@function_tool`
- No separation

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 29.1 | Create `prompts.py` | Extract inline instructions. Convert to XML |
| 29.2 | Create `agents.py` | Merge agent creation from all 3 files |
| 29.3 | Create `runner.py` | Merge `__main__` blocks with option selection |
| 29.4 | Delete old files | Remove `adk_utcp_llm_chat.py`, `open_ai_agent_tools_demo.py`, `open_ai_chat_client_tools_demo.py` |

**Files changed:** 3 deleted, 3 created

---

### 30. `evals`

**Current State:**
- Inline prompts in `simple_rag.py`
- `data_classes.py` exists
- Semantic Kernel process pipeline (not standard agent)

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 30.1 | Create `prompts.py` | Extract system prompt from `simple_rag.py`. Convert to XML |
| 30.2 | Update `data_classes.py` | Move inline step state classes from `simple_rag.py` |
| 30.3 | Rename `simple_rag.py` → `agents.py` | Contains the process steps (agent-equivalents) |
| 30.4 | Create `runner.py` | Extract process builder + execution logic |

**Files changed:** 1 renamed, 2 created, 1 updated

---

### 31. `rag/agentic`

**Current State:**
- `utils/prompt.py` has prompts (wrong path/filename)
- `utils/data_classes.py` has models (wrong path)
- 8 separate RAG agent files (each a class)
- No shared runner

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 31.1 | Move `utils/prompt.py` → `prompts.py` | Convert to XML. Move any inline prompts from agent files |
| 31.2 | Move `utils/data_classes.py` → `data_classes.py` | |
| 31.3 | Create `agents.py` | Consolidate all 8 RAG classes, or keep separate files but add a shared `agents.py` that exports them |
| 31.4 | Create `runner.py` | Unified entry point to select and run a RAG variant |
| 31.5 | Clean up `utils/` | Remove or keep only true utilities |

**Files changed:** 2 moved, 2 created, utils restructured

---

### 32. `rag/naive`

**Current State:**
- Inline prompt in `SimpleRag.__init__()`
- `data_classes.py` exists
- No prompts file

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 32.1 | Create `prompts.py` | Extract inline system prompt. Convert to XML |
| 32.2 | Rename `simple_rag.py` → `agents.py` | |
| 32.3 | Create `runner.py` | Extract execution logic |

**Files changed:** 1 renamed, 2 created

---

### 33. `software_team/prompts`

**Current State:**
- 17 prompt files in `prompts/` directory (one per agent role)
- Prompts already use **XML syntax**
- No agent implementations, tools, or runners

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 33.1 | Merge all into single `prompts.py` | Consolidate 17 files into one `prompts.py` at project root |
| 33.2 | Create `tools.py` | Implement tool functions referenced in XML prompts (e.g., `write_file`, `run_command`, `git_commit`) |
| 33.3 | Create `agents.py` | Wire each role's prompt to an agent instance |
| 33.4 | Create `data_classes.py` | Define models for project structure, code outputs |
| 33.5 | Create `runner.py` | Orchestrate the software team workflow |
| 33.6 | Delete `prompts/` directory | After merging |

**Files changed:** 17 deleted (directory), 5 created

---

### 34. `dspy_mcp_agent`

**Current State:**
- Single file `agent/dspy_agent.py` with everything
- DSPy signatures as prompts
- Inline tool definitions

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 34.1 | Create `prompts.py` | Extract DSPy `Signature` classes (they serve as prompts) |
| 34.2 | Create `tools.py` | Extract tool functions (`phone`, `local_business_lookup`) |
| 34.3 | Create `agents.py` | Extract `Worker`, `Worker2` module classes |
| 34.4 | Create `data_classes.py` | Extract `Tool` Pydantic model |
| 34.5 | Create `runner.py` | Add `__main__` guard |
| 34.6 | Delete `agent/` folder | Flatten structure |

**Files changed:** folder deleted, 5 created

---

### 35. `ai_blogger/crew_ai`

**Current State:**
- YAML config files for prompts and tasks (CrewAI convention)
- `tools/custom_tool.py` (placeholder)
- `crew.py` has agent definitions
- `main.py` is runner

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 35.1 | Create `prompts.py` | Convert YAML prompt content to XML syntax Python constants (keeping YAML for CrewAI framework compatibility) |
| 35.2 | Rename `tools/custom_tool.py` → `tools.py` (root) | Flatten |
| 35.3 | Rename `crew.py` → `agents.py` | |
| 35.4 | Rename `main.py` → `runner.py` | |
| 35.5 | Keep `config/` | CrewAI needs YAML configs at runtime; `prompts.py` serves as documentation |

**Files changed:** 3 renamed, 1 created

---

### 36. `declarative_prompt_engineering/dspy`

**Current State:**
- Educational examples, each file self-contained
- DSPy Signatures serve as declarative prompts
- Tools in `dspy_tools.py`

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 36.1 | Create `prompts.py` | Centralize DSPy Signature classes used across examples |
| 36.2 | Rename `foundational/dspy_tools.py` → `tools.py` | Flatten to root |
| 36.3 | Create `agents.py` | Centralize DSPy module instantiations |
| 36.4 | Create `runner.py` | Unified runner for all examples |

**Files changed:** 1 renamed, 3 created

---

### 37. `declarative_prompt_engineering/opik`

**Current State:**
- `opik_agent.py` is empty
- `opik_optimization.py` has inline prompts + optimizers

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 37.1 | Create `prompts.py` | Extract `ChatPrompt` definitions. Convert to XML |
| 37.2 | Rename `opik_optimization.py` → `agents.py` | Optimizers are the "agents" |
| 37.3 | Create `runner.py` | Extract runner functions, add `__main__` |
| 37.4 | Delete `opik_agent.py` | Empty file |

**Files changed:** 1 deleted, 1 renamed, 2 created

---

### 38. `prompt_sdk`

**Current State:**
- Library project with builder pattern
- No prompts/agents/tools (it IS a prompt SDK)

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 38.1 | No structural changes needed | This is a library, not an agent project |
| 38.2 | Create `__init__.py` | At root if missing, for package exports |

**Files changed:** 0-1 created

---

### 39. `AQL`

**Current State:**
- Custom DSL compiler/parser project
- Agents are runtime stubs

**Tasks:**

| # | Task | Details |
|---|------|---------|
| 39.1 | No prompts restructuring | Prompts are in AQL language, not Python |
| 39.2 | Create `runner.py` | Unified entry point for compile + run |
| 39.3 | Implement real agents | Replace stubs in `runtime/agents/` with LLM-backed implementations |

**Files changed:** 1 created, runtime agents updated

---

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total sub-projects** | ~39 |
| **Already well-structured** | 4 (browser_agent, command_line_agent, test_driven_coding_agent, prompt_sdk) |
| **Non-agentic (skip)** | 12 |
| **Need refactoring** | ~23 |
| **New `prompts.py` to create** | 12 |
| **Existing `prompts.py` to convert to XML** | 14 |
| **New `tools.py` to create** | 8 |
| **New `agents.py` to create** | 20 |
| **New `runner.py` to create** | 18 |
| **New `data_classes.py` to create** | 10 |
| **Files to delete/merge** | ~35 |
| **Files to rename** | ~20 |
| **Total estimated file operations** | ~140 |

---

## XML Prompt Template Standard

All prompts should follow this XML structure:

```python
AGENT_NAME_PROMPT = """
<agent name="agent_name" description="Brief description">
    <instructions>
        Core behavioral instructions for the agent.
        What it should do, how it should think, its role.
    </instructions>

    <tools>
        <tool name="tool_name">
            Description of what the tool does and when to use it.
            <parameters>
                <param name="param_name" type="str" required="true">Description</param>
            </parameters>
        </tool>
    </tools>

    <context>
        Background information, domain knowledge, or
        dynamic context injected at runtime via {placeholders}.
    </context>

    <output_format>
        Expected output structure, format requirements,
        or Pydantic model schema the response should conform to.
    </output_format>

    <examples>
        <example>
            <input>Sample user input</input>
            <output>Expected agent response</output>
        </example>
    </examples>

    <guardrails>
        - Things the agent must NOT do
        - Safety constraints
        - Scope limitations
    </guardrails>
</agent>
"""
```

---

## Recommended Execution Order

1. **Phase 1 — Already-structured projects** (minor renames): `browser_agent`, `command_line_agent`, `test_driven_coding_agent`
2. **Phase 2 — Well-separated projects** (convert prompts to XML): `ACE`, `arguing_agents`, `chain_of_agents`, `tri_layer_reflection`, `prompt_optimizer`, `multiturn_conversation_summarization`
3. **Phase 3 — Needs file splitting** (extract from monoliths): `ai_solution_architect`, `ai_stock_agent`, `data_chatbot`, `design_patterns/*`, `prompt_generator`
4. **Phase 4 — Needs consolidation** (merge scattered files): `a2a_communication`, `agentic_trading`, `inbox_chatbot`, `ai_blogger/*`, `rag/*`
5. **Phase 5 — Special projects** (unique patterns): `software_team`, `dspy_mcp_agent`, `mcp_utcp_tools`, `custom_agent`, `declarative_prompt_engineering/*`
