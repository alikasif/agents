from prompt_generator_agent import create_agents_from_env
from dotenv import load_dotenv
import os
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
import asyncio
from openai import AsyncOpenAI


# --- Single judging agent instruction ---
JUDGE_INSTRUCTIONS = (
    "You are a prompt evaluation expert. Given a user task and three prompts generatar tools, your job is to call the tools to get the prompt and judge them by \
      assign a score (1-10) to each prompt based on how well it enables an LLM to accomplish the user's task. \
      Consider clarity, completeness, specificity, and alignment with the user input. Then, rank the prompts from best to worst. \
      Return your answer as a JSON object with keys: 'scores' (a dict of agent names to scores) and 'ranking' (a list of agent names in order from best to worst)."
)

def get_all_prompt_agents_as_tools():
    """
    Returns the three prompt generator agents (gpt_agent, anthropic_agent, gemini_agent) using create_agents_from_env from prompt_generator_agent.py
    """
    gpt_agent, anthropic_agent, gemini_agent =  create_agents_from_env()
    description = "generate prompt for user input"
    # The tools are the three agents
    tools = [
        gpt_agent.as_tool(tool_name="gpt_agent", tool_description=description), 
        anthropic_agent.as_tool(tool_name="anthropic_agent", tool_description=description),
        gemini_agent.as_tool(tool_name="gemini_agent", tool_description=description)
    ]

    return tools


def create_gpt_agent_with_tools():
    """
    Creates a GPT agent and uses the agents returned from get_all_prompt_agents as its tools.
    Returns the new GPT agent.
    """    

    agent = Agent(
        name="GPT Agent with Tools",
        instructions=JUDGE_INSTRUCTIONS,
        model=os.getenv("OPENAI_MODEL"),
        tools=get_all_prompt_agents_as_tools()
    )
    return agent

async def generate_and_judge_prompt(user_task):
    """
    Given a user task description, use the agent to generate a high-quality prompt for an LLM.
    """
    # The agent expects a message or input; we pass the user_task as the input.
    response = await Runner.run(create_gpt_agent_with_tools(), user_task)
    # If the response is a dict or object, extract the text; otherwise, return as is.
    if isinstance(response, dict) and "output" in response:
        return response["output"]
    return str(response)


if __name__ == "__main__":
    load_dotenv(override=True)

    # Ask for user input
    user_task = input("Enter your task description: ")

    gpt_result = asyncio.run(generate_and_judge_prompt(user_task))

    # gpt_prompt = gpt_agent.run(user_task)
    # anthropic_prompt = anthropic_agent.run(user_task)
    # gemini_prompt = gemini_agent.run(user_task)

    # print("\n--- GPT Prompt ---\n", gpt_prompt)
    # print("\n--- Anthropic Sonnet Prompt ---\n", anthropic_prompt)
    # print("\n--- Gemini Prompt ---\n", gemini_prompt)

    # # Prepare input for judging agents
    # judge_input = (
    #     f"User Task: {user_task}\n"
    #     f"\nPrompt 1 (GPT):\n{gpt_prompt}\n"
    #     f"\nPrompt 2 (Anthropic Sonnet):\n{anthropic_prompt}\n"
    #     f"\nPrompt 3 (Gemini):\n{gemini_prompt}\n"
    # )

    # judge_agent_1 = gpt_agent  # For demonstration, use the GPT agent as a judge
    # judge_agent_2 = anthropic_agent  # Use the Anthropic agent as a judge

    # judge1_result = judge_agent_1.run(judge_input)
    # judge2_result = judge_agent_2.run(judge_input)

    print("\n--- Judge Agent 1 (GPT) Evaluation ---\n", gpt_result)
    
