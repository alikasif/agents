from __future__ import annotations

import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
from tools import google_search, browse
from prompts import get_opponent_system_prompt, get_proponent_system_prompt

load_dotenv(override=True)

"""
collect research from 3 researchers and ask each debater to review them. then pass on each debater output to each other to debat and reach consensus
"""

def get_agent(name: str, model: str, api_key: str, system_prompt: str):
    agent = Agent(
        name=name,
        instructions=system_prompt,
        model=LitellmModel(model=model, api_key=api_key),
        tools=[google_search, browse]
    )
    return agent


async def run_agent(agent: Agent, user_prompt: str):
   
    result = await Runner.run(agent, user_prompt, max_turns=5)
    return result.final_output


if __name__ == "__main__":
    
    model = os.getenv("GEMINI_MODEL")
    gemini_flash3_model = os.getenv("GEMINI3_FLASH_MODEL")
    api_key = os.getenv("GEMINI_API_KEY")
    agent_response_dict = {}
    date = "2026-01-04"

    proponent_prompt = get_proponent_system_prompt(date)
    opponent_prompt = get_opponent_system_prompt(date)
    
    proponent_agent = get_agent("proponent", model, api_key, proponent_prompt)  
    opponent_agent = get_agent("opponent", gemini_flash3_model, api_key, opponent_prompt)

    idea = "Principle of conservation of energy is false. Energy can be created or destroyed."
    opponent_response = ""
    i=0
    while opponent_response != "I AGREE" and i<10:
        i+=1
        
        proponent_input = f"idea: {idea}\n\nopponent_response: {opponent_response}"
        proponent_response = asyncio.run(run_agent(proponent_agent, proponent_input))
        print(f"\n\nPROPOUNDER OUTPUT:\n")
        print(f"proponent: {proponent_response}")
        
        opponent_input = f"idea: {idea}\n\nproponent_response: {proponent_response}"
        opponent_response = asyncio.run(run_agent(opponent_agent, opponent_input))
        print(f"\n\nOPPONENT OUTPUT:\n")
        print(f"opponent: {opponent_response}")
        print("="*150)

    