
# Solution Architecture

## Approach
The goal is to build an agentic system (AI Code Agent/ACE) that can write, debug, and explain code, utilizing best practices from Blinky and Copilot Agent architectures. The system is composed of several collaborating agents (or modular agent functions):

1. Task Agent: Understands user requests and scopes the coding problem.
2. Code Generation Agent: Writes code based on requirements, using an LLM fine-tuned or specialized for code generation.
3. Debugging Agent: Detects and fixes issues using logs, traces, or test results, running code in a safe sandboxed environment.
4. Explanation Agent: Explains the generated code, reasoning, and debugging steps in natural language.

Agents communicate and orchestrate tasks via a shared workspace/context (using frameworks like CrewAI or AutoGen), enabling step-by-step, plan-act-observe-refine cycles for complex tasks and iterative improvements. Integrate with developer tools (IDE extensions, GitHub Actions, codebase access) for developer-centric workflows and automation.

Focus on permission-scoped, secure execution, explicit and detailed prompting, modular multi-agent design, and iterative context-driven development.

## Architecture Diagram
```mermaid
graph TD;
UA([User in IDE/Web]) -->|Task Request| TGA(Task Generation Agent);
TGA -->|Clarified Requirements| CGA(Code Generation Agent);
CGA -->|Draft Code| DGA(Debugging Agent);
DGA -->|Debugged/Tested Code,<br/>Error Reports| CGA;
DGA -->|Debug Info| EA(Explanation Agent);
CGA -->|Generated Code (with docstrings)| EA;
EA -->|Explanation| UA;
CGA -->|Code| VFS((Virtual File System/Sandbox));
DGA -->|Execution/Test| VFS;
subgraph "LLM/Agent Orchestration Framework"
  TGA
  CGA
  DGA
  EA
end
subgraph "DevOps Integration"
  VFS
  IDE((IDE Extension/API))
  GITHUB((GitHub/Actions Integration))
end
UA -->|Monitor, Approve, Refine| IDE
IDE -->|Export/Commit| GITHUB
GITHUB -->|CI/Test Feedback| DGA
```

## Design Patterns
- Agentic Patterns: Modular multi-agent orchestration, separating concerns (generation, debugging, explanation, planning)
- Plan-and-Act Loop: Agents use iterative reasoning (plan, code, test/run, observe, refine)
- One-Task-Per-Agent Principle: Each agent performs a well-defined function (aligned with best practices)
- Sandbox Execution: All code tested and debugged in isolated, permission-restricted subsystems
- Secure Context Passing: Only relevant code/context shared with LLM to reduce risk, improve performance
- IDE/DevOps Integration: Agents operate within or communicate with developer tools/environment for seamless UX


## LLM, SDKs, Tools, Frameworks
- LLMs: 
  - GPT-4o (OpenAI, best for code synthesis/explanation),
  - Gemini 2.5 Pro (Google, great for context management),
  - Claude 3.5 Sonnet (Anthropic, excels at code reasoning),
  - Code Llama 70B (Meta, open-source option for private deployments),
  - DeepSeek V3 (open-source code LLM, if privacy/control is prioritized)
- Frameworks: 
  - CrewAI (multi-agent open-source framework)
  - AutoGen (for autonomous/async agent orchestration)
  - LangGraph (multi-step workflow definition for LLM/agent tasks)
- SDKs: OpenAI, Anthropic, Google Gemini APIs
- Sandboxing/Execution: Docker-based sandbox (for secure code execution)
- Integration: VSCode extension API, GitHub Actions API, or JetBrains plugin SDK
- Optional: WebSocket/REST API for agent communication


## Detailed Design
1. **User Inputs Request:**
    - IDE extension or chat frontend sends user query to Task Agent (TGA).
2. **Task Parsing/Planning:**
    - TGA clarifies/expands requirements, retrieves context (files, previous issues), and creates a plan.
3. **Code Generation:**
    - Code Generation Agent (CGA) uses LLM to write code (with high-quality docs), referencing retrieved context.
4. **Debugging & Testing:**
    - Debugging Agent (DGA) runs code/tests in a Docker sandbox, captures errors, analyzes stack traces/logs, and requests code fixes from CGA via explicit bug reports.
    - May iterate multiple times with plan-act-observe cycles until code passes or user stops.
5. **Explanation:**
    - Explanation Agent (EA) generates clear, educational output for: code design, algorithms, rationale for code changes, and debug process/results.
6. **IDE/DevOps Integration:**
    - Extension integrates feedback (e.g. inline suggestions, file changes, PR creation, test runs) into developer workflow. GitHub/CI feedback may be re-ingested as extra context.

**Security:** All code execution is sandboxed strictly. Agents require explicit permission for codebase modification. Sensitive data masked in all LLM interactions.

**Scalability/Extensibility:**
- New agents can be added for code review, documentation, or managing PRs/issues.
- Modular agent design allows for flexible orchestration (CrewAI/AutoGen or custom orchestrator).

## Prompting Technique
- Chain-of-Thought (CoT) prompting for reasoning/debugging steps in Code Generation and Debugging agents.
- Case-specific, highly explicit prompts (provide full context, objectives, constraints).
- Use system and user roles to instruct the LLMs clearly about their specialized functions (e.g., 'You are a senior backend developer specializing in debugging Python errors...').
- Include code context, error messages, and goals in the LLM input for best results.
- For explanations: prompt for step-by-step reasoning, analogies, and examples.

## GitHub Links
- Blinky (VSCode AI debugging agent): https://github.com/sweepai/blinky
- Tabby (open-source coding assistant): https://github.com/TabbyML/tabby
- patched.codes (multi-workflow AI agent): https://github.com/patchedcodes/patched
- CrewAI (multi-agent LLM framework): https://github.com/joaomdmoura/crewAI
- OpenAgents (agent orchestration): https://github.com/OpenAgentsInc/OpenAgents
- SWE-Agent (AI code agent): https://github.com/princeton-nlp/SWE-agent

