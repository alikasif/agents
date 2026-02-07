# 🤖 AI Test-Driven Development (TDD) Agent

**An autonomous coding agent that architects tests first, then writes production-grade code to pass them.**

This project demonstrates a fundamental shift in AI-assisted coding: moving from "generating code" to "supervising architecture." It acts as both a **Senior QA Architect** (writing comprehensive test suites) and a **Senior Software Engineer** (implementing modular solutions).

---

## ✨ Key Features

- **Strict TDD Workflow**: Enforces the verify-first cycle. Tests are generated *before* implementation.
- **Production-Grade Output**:
  - **Modular Architecture**: Automatically splits code into logical files (`models.py`, `exceptions.py`, `utils.py`).
  - **Code Quality**: Enforces Type Hints, Docstrings, PEP 8, and SOLID principles.
  - **Robustness**: Handles edge cases and custom exceptions.
- **Self-Healing Loop**: If tests fail, the agent analyzes the `pytest` output, fixes the specific error, and retries automatically.
- **Visual Feedback**: Runs tests in a separate terminal window so you can watch execution in real-time.
- **Snapshot History**: Every run is saved in a timestamped `runs/` folder for full traceability.

---

## 🏗️ Architecture

The system is built using **LiteLLM** (model agnostic) and the **OpenAI Agent SDK**.

- **`prompts.py`**: Contains strict XML-structured prompts for the "QA Architect" (Test Generator) and "Software Engineer" (Implementer).
- **`tools.py`**: The agent's toolkit:
  - `generate_tests()`: Architects the test suite.
  - `generate_implementation()`: Writes modular code, handling multi-file output.
  - `run_tests()`: Executes pytest in a new window, capturing output for the feedback loop.
- **`agents.py`**: Orchestrates the agent using a ReAct loop.
- **`runner.py`**: The CLI entry point.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A valid API key (Gemini, OpenAI, Anthropic, etc.)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/alikasif/agents.git
   cd agents/test_driven_coding_agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Linux/Mac
   export GEMINI3_FLASH_MODEL=gemini/gemini-2.0-flash
   export GEMINI_API_KEY=your_api_key_here

   # Windows (PowerShell)
   $env:GEMINI3_FLASH_MODEL="gemini/gemini-2.0-flash"
   $env:GEMINI_API_KEY="your_api_key_here"
   ```

---

## 💻 Usage

Run the agent with a problem description. Be specific for better results!

**basic Example:**
```bash
python runner.py "Write a function that calculates the nth Fibonacci number"
```

**Complex Example (Banking System):**
```bash
python runner.py "Implement a banking system with Checker and Savings accounts. Support transfers, overdraft protection, and transaction history. Use custom exceptions for insufficient funds."
```

---

## 📂 Output Structure

For the banking example, the agent generates a folder like `runs/run_202x.../` containing:

```
runs/run_20260207_123000/
├── tests/
│   └── test_banking.py       # Comprehensive pytest suite
├── models.py                 # Account classes
├── exceptions.py             # Custom exceptions
├── utils.py                  # Helper functions
└── main.py                   # Entry point
```

---

## 🧠 The "Shift to Supervisor"

This agent isn't just a code generator; it's a **workflow enforcer**.
- **You** provide the intent and architectural constraints.
- **The Agent** handles the implementation details and verification.
- **You** review the final reliable, tested artifact.

*Built with ❤️ by [Your Name/Team]*