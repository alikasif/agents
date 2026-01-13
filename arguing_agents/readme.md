# Arguing Agents

This project implements a multi-agent system where two agents—a **Proponent** and an **Opponent**—debate a specific idea. The Proponent tries to convince the Opponent of the idea, while the Opponent critically evaluates it. The debate continues until the Opponent agrees or a maximum number of turns is reached.

## Features

- **Multi-Agent Debate**: Uses two distinct agents with specialized roles to explore a topic deeply.
- **Tool Integration**: Agents are equipped with tools to gather information:
  - `google_search`: To find latest information and evidence.
  - `browse`: To read web page content for in-depth verification.
- **Dynamic Prompts**: System prompts are updated with the current date to ensure temporal relevance.
- **Consensus Building**: The loop terminates when the Opponent explicitly agrees ("I AGREE").

## Agents

1.  **Proponent**:
    - Role: Persuasive and logical debater.
    - Goal: Convince the Opponent to accept the idea.
    - Behavior: Presents arguments, addresses counter-arguments with evidence, and remains persistent.

2.  **Opponent**:
    - Role: Skeptical and critical thinker.
    - Goal: Challenge the idea and find flaws.
    - Behavior: Rejects initial ideas, scrutinizes logic/evidence, but remains intellectually honest and agrees if convinced.

## Setup

1.  **Environment Variables**:
    Ensure you have a `.env` file with the following keys:
    ```env
    GEMINI_MODEL=gemini-2.0-flash-exp  # Or your preferred model
    GEMINI3_FLASH_MODEL=gemini-2.0-flash-exp # For the opponent
    GEMINI_API_KEY=your_api_key_here
    SERPER_API_KEY=your_serper_api_key  # For Google Search
    ```
    (Note: The code uses `LitellmModel`, so ensure your API keys match the provider requirements.)

2.  **Dependencies**:
    Install the required packages. This project relies on `agents`, `langchain`, `playwright`, and `google-serper`.
    ```bash
    pip install -r requirements.txt
    playwright install  # For the browse tool
    ```

## Usage

Run the main script to start the debate:

```bash
python arg_agents.py
```

The script currently debates the idea: *"Principle of conservation of energy is false. Energy can be created or destroyed."*

### Output

The conversation will be printed to the console, showing the turn-by-turn arguments from both the Proponent and the Opponent.

## File Structure

- `arg_agents.py`: Main entry point. Initializes agents and runs the debate loop.
- `prompts.py`: strict system prompts for Proponent and Opponent roles.
- `tools.py`: Implementation of `google_search` and `browse` tools.
