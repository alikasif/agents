from prompt_generator_agent import create_agents_from_env
from dotenv import load_dotenv
import os
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
import asyncio
from openai import AsyncOpenAI
from pydantic import BaseModel


class PromptAgentOutput(BaseModel):
    agent_name: str
    generated_prompt: str

class CallingAgentOutput(BaseModel):
    prompts: list[PromptAgentOutput]
    


# --- Single judging agent instruction ---
JUDGE_INSTRUCTIONS = (
    "You are a prompt evaluation expert. \
     Given a user input and three prompts generatar tools, your job is to call the tools with user input to get the prompt and judge them by \
     assign a score (1-10) to each prompt based on how well it enables an LLM to accomplish the user's task. \
     Consider clarity, completeness, specificity, and alignment with the user input. Then, rank the prompts from best to worst. \
     Return your answer as a JSON object with keys: 'scores' (a dict of agent names to scores) and 'ranking' (a list of agent names in order from best to worst) and the highest ranked prompt."
)

GENERATE_INSTRUCTIONS = (
    "You are a prompt generation expert. \
     Given a user input and three prompts generatar tools, your job is to call the tools with user input to get the prompt  \
     Return your answer as a JSON object with keys: 'user_input' (input provided by user), 'prompts' (list of objects with each object having agent name and its generated prompt)."
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


def create_prompt_agent_with_tools(instructions):
    """
    Creates a GPT agent and uses the agents returned from get_all_prompt_agents as its tools.
    Returns the new GPT agent.
    """    

    agent = Agent(
        name="GPTAgentWithTools",
        instructions=instructions,
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
    response = await Runner.run(create_prompt_agent_with_tools(GENERATE_INSTRUCTIONS), user_task)
    # If the response is a dict or object, extract the text; otherwise, return as is.
    if isinstance(response, dict) and "output" in response:
        return response["output"]
    return str(response.final_output)


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



async def run_judging_agent(user_input, prompt):
    """
    Runs the judging agent with the provided judging input and returns the result.
    """
    agent, judging_input = create_gpt_judging_agent(user_input, prompt)
    response = await Runner.run(agent, str(judging_input))
    # If the response is a dict or object, extract the text; otherwise, return as is.
    if isinstance(response, dict) and "output" in response:
        return response["output"]
    return str(response.final_output)


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
        # instructions = (
        #     "You are a meta-judging agent. Given a user input and a list of prompts, you can call judging agents as tools to evaluate each prompt. "
        #     "Aggregate their ratings and explanations, and provide a summary or consensus judgement. "
        #     "Return your answer as a JSON object with keys: 'user_input', 'prompt_list', 'judgements' (list of objects with agent name, rating, and explanation), and 'consensus' (your overall assessment)."
        # )

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


if __name__ == "__main__":
    load_dotenv(override=True)

    # Ask for user input
    user_task = input("Enter your task description: ")

    gpt_result = asyncio.run(generate_prompt(user_task))
    #print("\n--- Judge Agent 1 (GPT) Evaluation ---\n", gpt_result)

    #judge_result = asyncio.run(run_judging_agent(user_task, gpt_result))
    #print("\n--- Judge Agent 1 (GPT) Evaluation ---\n", judge_result)

    judge_result = asyncio.run(judge_prompts(user_task, gpt_result))
    print("\n--- Final Evaluation ---\n", judge_result)



    
    
