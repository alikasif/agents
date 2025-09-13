# Prompt SDK

A modular Python SDK for building structured prompts for LLMs and agentic workflows.

## What is it?
Prompt SDK is a toolkit that helps developers create, validate, and manage prompt templates for advanced AI agents. It enforces best practices, supports extensibility, and makes prompt engineering reproducible and maintainable.

## Why use it?
- **Validation:** Ensures all required fields are present before prompt generation.
- **Extensibility:** Easily add new prompt types for custom agent behaviors.
- **Chainable API:** Fluent, readable code for building prompts.
- **Separation of Concerns:** Each prompt type is a separate class/module.
- **Factory Pattern:** Instantiates the right prompt builder for your use case.

## Features
- Base class with validation and chainable setters
- Specialized prompt types: Chain-of-Thought, Tree-of-Thought, ReAct, Multi-Shot
- Factory for dynamic instantiation
- Easy to add new prompt types
- Example runner and tests for each module

## Usage Example
```python
from prompt_sdk.factory import PromptFactory

prompt = (
    PromptFactory.create("chain_of_thought")
    .set_task("Solve the math problem")
    .set_context("Algebraic equations")
    .add_example("Q: 2+2?\nA: 4")
    .set_format("Plain text answer")
    .set_tone("neutral")
    .set_persona("You are a helpful tutor.")
    .set_thinking_style("step by step")
    .build()
)
print(prompt)
```

## Modules
- `base.py`: Base class and validation
- `chain_of_thought.py`: Chain-of-thought prompt builder
- `tree_of_thought.py`: Tree-of-thought prompt builder
- `react.py`: ReAct prompt builder
- `multi_shot.py`: Multi-shot prompt builder
- `factory.py`: Factory for prompt builders
- `runner.py`: Example runner for SDK usage
- `tests/`: Unit tests for each module

## License
MIT
