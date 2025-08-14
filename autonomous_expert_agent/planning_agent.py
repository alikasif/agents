
from agents import Agent, ModelSettings
from agents import Agent, Runner
from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server
from python_a2a import Message, TextContent, MessageRole
from dotenv import load_dotenv
import os
import asyncio
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
from prompts import WRITE_TODOS_DESCRIPTION

class TaskPlanner:

    def get_model(self):
        """Get the model to be used for the agent."""
        anthropic_client = AsyncOpenAI(base_url=os.getenv("ANTHROPIC_BASE_URL"), api_key=os.getenv("ANTHROPIC_API_KEY"))

        anthropic_model = OpenAIChatCompletionsModel(model=os.getenv("ANTHROPIC_MODEL"), openai_client=anthropic_client)

        return anthropic_model

    def get_agent(self):

        return Agent(
            name="TaskPlanningAgent",
            instructions=WRITE_TODOS_DESCRIPTION,
            model=self.get_model(),
        )

    def run_agent(self, query: str):
            # Create content from user query
            content = {
                "role": "user",
                "parts": [{"text": query}]
            }

            result = asyncio.run(Runner.run(self.get_agent(), query))
            #print(f"Agent response: {str(result)}")
            print(f"Final output: {result.final_output}")
            return result.final_output

if __name__ == "__main__":
    load_dotenv()
    user_input = input("Enter your task query: ")
    planner = TaskPlanner()
    planner.run_agent(user_input)
    