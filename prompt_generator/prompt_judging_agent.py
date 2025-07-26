from prompt_generator_agent import create_agents_from_env
from dotenv import load_dotenv
import os
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
import asyncio
from openai import AsyncOpenAI
from pydantic import BaseModel


JUDGE_INSTRUCTIONS = (
        "You are an expert prompt engineer and evaluator. "
        "Given a user input and a list of objects containing generated prompt and agent_name, your job is to critically assess the quality, clarity, and effectiveness of the prompt for accomplishing the user's task. "
        "Consider the following criteria:\n"
        "- Does the prompt fully address the user's intent and requirements?\n"
        "- Is the prompt clear, specific, and unambiguous?\n"
        "- Are all necessary constraints and context included?\n"
        "- Is the language concise and actionable?\n"
        "Provide a rating from 1 (poor) to 10 (excellent), and a brief explanation of your reasoning. "
        "Return your answer as a JSON object with keys: 'user_input' and list of objects containing 'prompt', creator_agent_name, 'rating', and 'explanation'."
    )

class Judgement(BaseModel):
    creator_agent_name: str
    prompt: str
    rating: str
    explanation: str

class FinalJudgement(BaseModel):
    user_input: str
    final_judgements: list[Judgement]

def create_gpt_judging_agent(user_input, prompt):
    """
    Creates an agent that judges the quality of a generated prompt given the user input and the prompt.
    Returns the judging agent.
    """

    # Compose the input for the agent as a dict or formatted string
    judging_input = {
        "user_input": user_input,
        "prompt_list": prompt
    }

    agent = Agent(
        name="PromptJudgingAgent",
        instructions=JUDGE_INSTRUCTIONS,
        model=os.getenv("OPENAI_MODEL"),
        output_type=FinalJudgement,
    )
    return agent, judging_input

def create_gemini_judging_agent(user_input, prompt):
    """
    Creates an agent that judges the quality of a generated prompt given the user input and the prompt.
    Returns the judging agent.
    """

    # Compose the input for the agent as a dict or formatted string
    judging_input = {
        "user_input": user_input,
        "prompt_list": prompt
    }

    gemini_model = os.getenv("GOOGLE_MODEL")
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_base_url = os.getenv("GEMINI_BASE_URL")

    gemini_client = AsyncOpenAI(base_url=gemini_base_url, api_key=gemini_key)
    gemini_model = OpenAIChatCompletionsModel(model=gemini_model, openai_client=gemini_client)
    gemini_agent =  Agent(name="GeminiPromptGeneratorAgent", instructions=JUDGE_INSTRUCTIONS, model=gemini_model)

    return gemini_agent, judging_input


def get_all_judging_agents_as_tools(user_input, prompt):
    """
    Returns a list of judging agents (e.g., GPT and Gemini judging agents) as tools, similar to get_all_prompt_agents_as_tools.
    Each judging agent is wrapped as a tool with a descriptive name and description.
    """
    gpt_agent, gpt_judging_input = create_gpt_judging_agent(user_input, prompt)
    gemini_agent, gemini_judging_input = create_gemini_judging_agent(user_input, prompt)
    description = "Judge the quality of a generated prompt for a user input."
    tools = [
        gpt_agent.as_tool(tool_name="gpt_judging_agent", tool_description=description),
        gemini_agent.as_tool(tool_name="gemini_judging_agent", tool_description=description)
    ]
    return tools


def create_judging_agent_with_tools(user_input, prompt, instructions=None):
    """
    Creates a meta-judging agent that uses other judging agents as tools.
    Returns the new meta-judging agent.
    """
    if instructions is None:
        instructions = "you are a supreme judging agent who looks at the judgement from other agents supplied as tool to judge the prompt. \
                    you must Aggregate their ratings and explanations, and provide a summary or consensus judgement. \
                    you have to defintely choose the best prompt based on the judgements from other agents. \
                    Return your answer as a JSON object with keys: 'user_input', 'prompt_list' contaning the agent name and prompt, 'judgements' (list of objects with agent name, rating, and explanation), and 'consensus' (your overall assessment)."
    
    agent = Agent(
        name="MetaJudgingAgentWithTools",
        instructions=instructions,
        model=os.getenv("OPENAI_MODEL"),
        tools=get_all_judging_agents_as_tools(user_input, prompt),
    )
    return agent


async def judge_prompts(user_input, prompt_list):
    """
    Given a user input and a list of prompts, use the meta-judging agent to evaluate the prompts.
    Returns the consensus judgement and details from all judging agents.
    """
    agent = create_judging_agent_with_tools(user_input, prompt_list)

    judging_input = {
        "user_input": user_input,
        "prompt_list": str(prompt_list)
    }

    #response = await Runner.run(agent, {"user_input": user_input, "prompt_list": str(prompt_list)})
    response = await Runner.run(agent, str(judging_input))
    # Try to extract the final output (reuse logic from generate_prompt)
    if isinstance(response, dict) and "output" in response:
        return response["output"]
    if hasattr(response, "final_output"):
        return response.final_output
    return str(response)


    
