"""
TDD Agent

Test-Driven Development agent using OpenAI Agent SDK with LiteLLM.
"""

import os
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv

from prompts import tdd_agent_prompt
from tools import generate_tests, run_tests, generate_implementation

load_dotenv(override=True)

MAX_TURNS = 3


def get_model(prefix="GEMINI"):
    """Get LitellmModel configured from environment variables."""
    model = os.getenv(f"{prefix}_MODEL", "gemini/gemini-2.0-flash")
    api_key = os.getenv(f"{prefix}_API_KEY")
    return LitellmModel(model=model, api_key=api_key)


class TDDAgent:
    """Test-Driven Development Agent."""
    
    def __init__(self, model_prefix="GEMINI"):
        print(f"TDD Agent using {model_prefix} model")
        self.agent = Agent(
            name="TDD Agent",
            model=get_model(model_prefix),
            instructions=tdd_agent_prompt,
            tools=[generate_tests, run_tests, generate_implementation]
        )
    
    def run(self, problem: str) -> str:
        """
        Run TDD workflow for the given problem.
        
        Args:
            problem: Natural language description of the coding problem
            
        Returns:
            Final output from the agent
        """
        result = Runner.run_sync(
            self.agent,
            f"Solve this problem using TDD:\n\n{problem}",
            max_turns=MAX_TURNS
        )
        return result.final_output
