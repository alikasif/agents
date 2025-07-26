# Prompt Generator

## Overview
The **Prompt Generator** project enables users to generate expert prompts for any task they wish to accomplish using a large language model (LLM). After generating a prompt, a new agent executes the prompt and returns the result to the user. The result includes:
- The original user input
- The generated prompt
- The output from the LLM using the generated prompt

This project leverages a multi-agent architecture to ensure high-quality prompt generation and result evaluation.

## Workflow
1. **User Input:** The user provides a description of the task they want to achieve.
2. **Prompt Generation:** Three specialized agents generate candidate prompts based on the user's input.
3. **Prompt Judging:** Two judging agents evaluate the generated prompts and select the best one(s).
4. **Result Delivery:** The system returns the user input, the selected/generated prompt, and the final LLM output to the user.

## Agent Roles
- **Prompt Generators (3 agents):** Generate diverse and high-quality prompts for the user's task.
- **Prompt Judges (2 agents):** Evaluate and select the most effective prompt(s) from the generated candidates.

## Features
- Multi-agent collaboration for robust prompt generation and evaluation
- Modular design for easy extension and customization
- Transparent result reporting (user input, prompt, and LLM output)

## Usage
1. Provide your task description as input.
2. The system will generate, judge, and execute prompts automatically.
3. Receive a comprehensive result including your input, the generated prompt, and the LLM's output.

---

*This project is part of a broader agentic AI system. For more details, see the main repository README.* 