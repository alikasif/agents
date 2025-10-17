
from prompts import *
from data_classes import *
import os
from agents import Agent, Runner, OpenAIChatCompletionsModel
from dotenv import load_dotenv
import logging
import time
import asyncio
from openai import AsyncOpenAI


logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO


def get_model(prefix= "OPENAI"):        
        
        if prefix == "OPENAI":
            return os.getenv(prefix+"_MODEL")
        
        external_client = AsyncOpenAI(
            api_key=os.getenv(prefix+"_API_KEY"),
            base_url=os.getenv(prefix+"_BASE_URL")
        )
        return OpenAIChatCompletionsModel(model=os.getenv(prefix+"_MODEL"), openai_client=external_client)


async def generate(state: OptimizerState):
    
    generator_prompt = state["generator_prompt"]
    
    generator_agent = Agent(
        name="AI & LLM application analyst",
        model=get_model(),
        instructions=generator_prompt,
        output_type=GeneratorOutput,        
    )
    
    result = await Runner.run(generator_agent, f"{state["user_input"]}")
    return {"generator_output": result.linkedin_post}


async def reflector(state: OptimizerState):

    improve_prompt = improve_prompt.format(USER_INPUT=state["user_input"], ORIGINAL_PROMPT=state["generator_prompt"], GENERATED_OUTPUT=state["generator_output"])
    
    reflector_agent = Agent(
        name="AI & LLM application analyst",
        model=get_model(),
        instructions=improve_prompt,
        output_type=ReflectorOutput,        
    )
    
    result = await Runner.run(reflector_agent)
    return {"reflector_output": result}


def optimizer(state: OptimizerState):
    pass

def run():
    pass

