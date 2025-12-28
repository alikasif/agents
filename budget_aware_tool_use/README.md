# Budget-Aware ReAct Agent

A lightweight implementation of a budget-aware AI agent that dynamically adapts its tool usage strategy based on remaining computational resources. Built using Google's Gemini models and the ReAct (Reasoning and Acting) framework.

## Overview

This project implements an intelligent agent that tracks and manages its tool usage budget in real-time, adapting its search and browsing strategies to maximize effectiveness within resource constraints.

### Key Features

- **Real-time Budget Tracking**: Monitors query and URL budgets during execution
- **Dynamic Strategy Adaptation**: Automatically adjusts behavior based on budget levels (HIGH/MEDIUM/LOW/CRITICAL)
- **Google Gemini Integration**: Powered by Gemini 2.0 Flash for reasoning
- **ReAct Framework**: Follows the Reasoning + Acting pattern for transparent decision-making
- **Web Search & Browse Tools**: Integrated Google search and Playwright-based web browsing

## Architecture

```
budget_aware_tool_use/
├── react_agent_openai.py  # Main ReAct agent implementation
├── budget_tracker.py       # Budget monitoring and strategy guidance
├── tools.py               # Search and browse tool implementations
├── prompts.py             # System prompts for the agent
├── config.py              # Configuration and budget thresholds
├── example_usage.py       # Usage examples
└── __init__.py            # Package initialization
```

## How It Works

### Budget Levels

The agent adapts its strategy based on remaining budget percentage:

| Level | Remaining Budget | Search Strategy | Browse Strategy | Goal |
|-------|-----------------|-----------------|-----------------|------|
| **HIGH** | ≥ 70% | 3-5 diverse queries | 2-3 URLs | Broad exploration |
| **MEDIUM** | 30-70% | 2-3 precise queries | 1-2 URLs | Efficient convergence |
| **LOW** | 10-30% | 1 focused query | 0-1 URL | Verify critical facts |
| **CRITICAL** | < 10% | Minimal usage only | Minimal usage only | Finalize or return None |

### ReAct Loop

The agent follows this iterative cycle:

```
<think>
  → Analyze current state, budget level, and information needs
  → Decide on tool usage strategy

<tool_code>
  → Execute search or browse with budget-aware parameters
  ↓
Tool Execution + Budget Update
  ↓
<tool_response>
  → Receive results and updated budget information
  ↓
Repeat until answer found or budget depleted
  ↓
<answer>
  → Provide final answer
```

## Installation

### Prerequisites

- Python 3.8+
- Google Gemini API key
- Serper API key (for Google search)

### Setup

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Configure environment variables**

Create a `.env` file in the project directory:

```bash
GEMINI_API_KEY=your-gemini-api-key-here
SERPER_API_KEY=your-serper-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp  # Optional: defaults to this
```

## Usage

### Basic Example

```python
from react_agent_openai import OpenAIReActAgent

# Create agent with default configuration
agent = OpenAIReActAgent(verbose=True)

# Run on a question
question = "What is the capital of France?"
result = agent.run(question)

print(f"Answer: {result['answer']}")
print(f"Steps: {len(result['steps'])}")
print(f"Budget Used: {result['budget_used']}")
```

### Custom Budget Configuration

```python
from react_agent_openai import OpenAIReActAgent
from config import BudgetConfig

# Create custom budget limits
budget_config = BudgetConfig(
    query_budget=20,  # Maximum 20 search queries
    url_budget=10     # Maximum 10 URLs to browse
)

agent = OpenAIReActAgent(
    budget_config=budget_config,
    max_iterations=15,
    verbose=True
)

result = agent.run("How does machine learning work?")
```

### Low Budget Scenario

```python
from config import BudgetConfig
from react_agent_openai import OpenAIReActAgent

# Test with very limited budget
budget_config = BudgetConfig(
    query_budget=5,
    url_budget=2
)

agent = OpenAIReActAgent(
    budget_config=budget_config,
    max_steps=10,
    verbose=True
)

result = agent.run("Your complex question here")
```

### Run Examples

```bash
cd d:\GitHub\agents\budget_aware_tool_use
python example_usage.py
```

## Configuration

### BudgetConfig

Controls budget limits and thresholds:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query_budget` | int | 5 | Maximum number of search queries |
| `url_budget` | int | 5 | Maximum number of URLs to browse |
| `high_threshold` | float | 0.70 | Threshold for HIGH budget level |
| `medium_threshold` | float | 0.30 | Threshold for MEDIUM budget level |
| `low_threshold` | float | 0.10 | Threshold for LOW budget level |

### ModelConfig

Controls Gemini model configuration:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | str | "gemini-2.0-flash-exp" | Gemini model to use |
| `temperature` | float | 0.7 | Sampling temperature |
| `max_output_tokens` | int | 8192 | Maximum output length |
| `verification_model` | str | "gemini-3.0-flash" | Model for verification |

## Tools

### Search Tool

Performs batched web searches using Google Serper API:

```python
google_search(queries: list[str]) -> str
```

- **Input**: Array of query strings
- **Output**: Combined search results
- **Budget**: Each query consumes 1 unit of query budget

### Browse Tool

Navigates to web pages and extracts content using Playwright:

```python
browse(urls: list[str], goal: str) -> str
```

- **Input**: Array of URLs and extraction goal
- **Output**: Combined page content
- **Budget**: Each URL consumes 1 unit of URL budget

## Result Format

The `run()` method returns a dictionary with:

```python
{
    'answer': str,              # Final answer
    'steps': List[ReActStep],   # All reasoning steps
    'budget_used': {            # Budget consumption
        'queries': int,
        'urls': int
    },
    'success': bool,            # Whether answer was found
    'reason': str              # Completion reason
}
```

## Development

### Project Structure

- **react_agent_openai.py**: Core agent logic with ReAct loop implementation
- **budget_tracker.py**: Budget monitoring, level classification, and strategy recommendations
- **tools.py**: Web search and browsing tool implementations
- **prompts.py**: Dynamic prompt generation with budget-aware instructions
- **config.py**: Dataclasses for configuration management
- **example_usage.py**: Comprehensive usage examples

### Extending the Agent

To add new tools:

1. Implement the tool function in `tools.py`
2. Add budget tracking logic in `budget_tracker.py`
3. Update the prompt in `prompts.py` to include the tool
4. Modify `execute_tool()` to handle the new tool

## License

MIT License

## References

https://arxiv.org/pdf/2511.17006