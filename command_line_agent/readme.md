# Command Line Agent

## Overview
The **Command Line Agent** is an intelligent assistant designed to bridge the gap between natural language and shell commands. It leverages LLMs (LiteLLM) to convert user requests into executable Bash or PowerShell commands, runs them safely using agentic tools, and logs feedback for continuous learning.

## Key Features

### 1. 🖥️ Cross-Platform Support
-   **Linux**: Generates and executes Bash commands.
-   **Windows**: Automatically detects the OS and supports:
    -   **PowerShell** (Preferred for complex tasks on Windows).
    -   **Command Prompt (CMD)** compatibility.

### 2. 🛡️ Safety & Guardrails
-   **Structured Prompts**: Uses XML-tagged system prompts (`<instructions>`, `<guardrails>`, `<tools>`) to ensure strict adherence to format.
-   **Critical Command Interception**: The LLM is instructed *NOT* to auto-execute destructive commands (deletion, killing processes) via tools. Instead, it asks for user confirmation.
-   **Execution Hooks**: A **Human-in-the-loop** mechanism using `CustomHooks` intercepts *every* tool execution to request explicit user confirmation (`type yes to continue...`) before running any command.

### 3. 🛠️ Tool Usage
The agent has access to specific tools to interact with the system:
-   `execute_bash_command`: For running commands on Linux/Unix systems.
-   `run_powershell`: For running commands on Windows.

### 4. 🧠 Active Learning & Feedback
-   Records every interaction (`User Input` -> `Command` -> `Feedback`) into `history.json`.
-   This data can be used to fine-tune the model or provide few-shot examples in future iterations.

## Architecture

```
command_line_agent/
├── agent.py        # Core agent logic, model initialization, and tool definition
├── prompts.py      # System prompts (XML structure) with context & guardrails
├── tools.py        # Implementation of verify_bash_command and run_powershell
├── hooks.py        # CustomHooks for pre-execution user confirmation
├── runner.py       # Main CLI loop for user interaction
└── readme.md       # Project documentation
```

## Setup & Usage

### Prerequisites
-   Python 3.x
-   `litellm`
-   `python-dotenv`
-   Access to an LLM provider (e.g., Gemini, OpenAI)

### Environment Variables
Create a `.env` file in the root or ensure variables are set:
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-pro
```

### Running the Agent
```bash
python runner.py
```

### Usage Example
```text
You: Show me all python files in the current folder
Agent Output:
User Input: Show me all python files in the current folder
Command: Get-ChildItem -Path . -Filter *.py
Result: [Output from PowerShell tool]

Feedback (optional): correct
```

## Future Improvements
-   [ ] **Safe Mode Level**: Configurable safety levels (e.g., allow read-only commands without confirmation).
-   [ ] **RAG Integration**: Use `history.json` to inject past successful commands into the context.
-   [ ] **Undo Capabilities**: Generate reverse commands for operations like `mkdir` or `mv`.
