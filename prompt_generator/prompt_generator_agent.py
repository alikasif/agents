from dotenv import load_dotenv
import sys
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
import os
import asyncio
from openai import AsyncOpenAI
from pydantic import BaseModel

PROMPT_GENERATION_INSTRUCTIONS = (
    "You are an expert prompt engineer. Your task is to generate a highly effective, clear, and actionable prompt for a large language model (LLM) to accomplish a given user task."
    "\n\nBest practices for prompt generation:"
    "\n- Be specific and unambiguous about the task."
    "\n- Include all necessary context, constraints, and requirements."
    "\n- Specify the desired format or structure of the output if relevant."
    "\n- Use clear and concise language."
    "\n- If the task involves multiple steps, break them down logically."
    "\n- Avoid vague instructions."
    "\n- If the user input is unclear, make reasonable assumptions and clarify them in the prompt."
    "\n\nGiven a user task, generate a single, expert-level prompt that will maximize the quality and relevance of the LLM's response."
)

GENERATION_MANAGER_INSTRUCTIONS = (
    "You are a prompt generation expert. \
     Given a user input and three prompts generatar tools, your job is to call the tools with user input to get the prompt  \
     Return your answer as a JSON object with keys: 'user_input' (input provided by user), 'prompts' (list of objects with each object having agent name and its generated prompt)."
)


class PromptAgentOutput(BaseModel):
    agent_name: str
    generated_prompt: str

class CallingAgentOutput(BaseModel):
    prompts: list[PromptAgentOutput]


def get_anthropic_sonnet_agent(anthropic_base_url, api_key=None, model="anthropic/claude-3-sonnet", instructions=None):
    """
    Returns an OpenAI Agents SDK Agent configured to use the Anthropic Sonnet model with detailed prompt engineering instructions.
    """
    if instructions is None:
        instructions = PROMPT_GENERATION_INSTRUCTIONS
    
    anthropic_client = AsyncOpenAI(base_url=anthropic_base_url, api_key=api_key)
    anthropic_model = OpenAIChatCompletionsModel(model=model, openai_client=anthropic_client)
    anthropic_agent =  Agent(name="AnthropicPromptGeneratorAgent", instructions=instructions, model=anthropic_model)

    return anthropic_agent


def get_gpt_agent(api_key=None, model="gpt-3.5-turbo", instructions=None):
    """
    Returns an OpenAI Agents SDK Agent configured to use a GPT model with detailed prompt engineering instructions.
    """
    if instructions is None:
        instructions = PROMPT_GENERATION_INSTRUCTIONS
    
    return Agent(
        name="GPTPromptGeneratorAgent",
        instructions=instructions,
        model=model)
  

def get_gemini_agent(gemini_base_url, api_key=None, model="google/gemini-pro", instructions=None):
    """
    Returns an OpenAI Agents SDK Agent configured to use a Google Gemini LLM model with detailed prompt engineering instructions.
    """
    if instructions is None:
        instructions = PROMPT_GENERATION_INSTRUCTIONS
    
    gemini_client = AsyncOpenAI(base_url=gemini_base_url, api_key=api_key)
    gemini_model = OpenAIChatCompletionsModel(model=model, openai_client=gemini_client)
    gemini_agent =  Agent(name="GeminiPromptGeneratorAgent", instructions=instructions, model=gemini_model)

    return gemini_agent


def create_agents_from_env():
    """
    Reads model names and API keys for GPT, Anthropic Sonnet, and Gemini from a .env file,
    then creates and returns the three agents. Exits with an error if any required variable is missing.
    """
    load_dotenv(override=True)

    gpt_model = os.getenv("OPENAI_MODEL")
    gpt_key = os.getenv("OPENAI_API_KEY")

    anthropic_model = os.getenv("ANTHROPIC_MODEL")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL")

    gemini_model = os.getenv("GOOGLE_MODEL")
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_base_url = os.getenv("GEMINI_BASE_URL")

    missing = []
    if not gpt_model:
        missing.append("OPENAI_MODEL")
    if not gpt_key:
        missing.append("OPENAI_API_KEY")
    if not anthropic_model:
        missing.append("ANTHROPIC_MODEL")
    if not anthropic_key:
        missing.append("ANTHROPIC_API_KEY")
    if not gemini_model:
        missing.append("GOOGLE_MODEL")
    if not gemini_key:
        missing.append("GEMINI_API_KEY")

    if missing:
        sys.exit(f"ERROR: The following environment variables are missing in your .env file: {', '.join(missing)}")

    gpt_agent = get_gpt_agent(api_key=gpt_key, model=gpt_model)
    anthropic_agent = get_anthropic_sonnet_agent(anthropic_base_url, api_key=anthropic_key, model=anthropic_model)
    gemini_agent = get_gemini_agent(gemini_base_url, api_key=gemini_key, model=gemini_model)

    #return gpt_agent
    return gpt_agent, anthropic_agent, gemini_agent


async def generate_prompt(agent, user_task):
    """
    Given a user task description, use the agent to generate a high-quality prompt for an LLM.
    """
    # The agent expects a message or input; we pass the user_task as the input.
    response = await Runner.run(agent, user_task)
    # If the response is a dict or object, extract the text; otherwise, return as is.
    if isinstance(response, dict) and "output" in response:
        return response["output"]
    return str(response)

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

def create_prompt_agent_with_tools():
    """
    Creates a GPT agent and uses the agents returned from get_all_prompt_agents as its tools.
    Returns the new GPT agent.
    """    

    agent = Agent(
        name="GPTAgentWithTools",
        instructions=GENERATION_MANAGER_INSTRUCTIONS,
        model=os.getenv("OPENAI_MODEL"),
        tools=get_all_prompt_agents_as_tools(),
        output_type=CallingAgentOutput,
    )
    return agent


async def generate_prompt(user_task):
    """
    Given a user task description, use the agent to generate a high-quality prompt for an LLM.
    """
    # The agent expects a message or input; we pass the user_task as the input.
    response = await Runner.run(create_prompt_agent_with_tools(), user_task)
    # If the response is a dict or object, extract the text; otherwise, return as is.
    if isinstance(response, dict) and "output" in response:
        return response["output"]
    return str(response.final_output)
