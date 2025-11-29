import asyncio
from dotenv import load_dotenv
import os
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings
from datetime import timedelta
from prompts import IRCTC_AGENT_INSTRUCTIONS
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

import asyncio
from dotenv import load_dotenv
import os
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings
from datetime import timedelta
from prompts import IRCTC_AGENT_INSTRUCTIONS
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

load_dotenv(override=True)

params = {"url": "http://localhost:8282/mcp", "timeout": timedelta(seconds=300), "sse_read_timeout": timedelta(seconds=600)}

async def run_mcp_agent(user_input):

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
        result = await Runner.run(agent, user_input)
        logger.info(f"Result type: {type(result)}")
        return result




#asyncio.run(run_mcp_agent("hello"))