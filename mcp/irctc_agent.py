import asyncio
from dotenv import load_dotenv
import os
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings
from datetime import timedelta
from prompts import IRCTC_AGENT_INSTRUCTIONS

load_dotenv(override=True)

params = {"url": "http://localhost:8282/mcp", "timeout": timedelta(seconds=300), "sse_read_timeout": timedelta(seconds=600)}

async def mcp_agent():
    async with MCPServerStreamableHttp(
        name="Streamable HTTP Python Server",
        params=params,
        cache_tools_list=True,        
        client_session_timeout_seconds=600,
    ) as server:
        agent = Agent(
            name="Assistant",
            instructions=IRCTC_AGENT_INSTRUCTIONS,
            mcp_servers=[server],
            model_settings=ModelSettings(tool_choice="required"),
            model=os.getenv("OPENAI_MODEL"),
        )

        while True:
            
            user_input = input("\n\nEnter your question (or 'exit' to quit): ").strip()
            if user_input.lower() == "exit":
                print("Exiting...")
                break
            if not user_input:
                print("Please enter a valid question.")
                continue
            
            print(f"\nrunning irctc agent")
            result = await Runner.run(agent, user_input)
            print(result)


asyncio.run(mcp_agent())