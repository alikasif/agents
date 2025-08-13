import os
from google import genai
from google.genai import types
from utcp.client.utcp_client import UtcpClient
from utcp.client.utcp_client_config import UtcpClientConfig, UtcpDotEnv
from pathlib import Path
from dotenv import load_dotenv
import asyncio


async def initialize_utcp_client() -> UtcpClient:
    """Initialize the UTCP client with configuration."""
    # Create a configuration for the UTCP client
    config = UtcpClientConfig(
        providers_file_path=str(Path(__file__).parent / "utcp_tools/providers.json"),
        load_variables_from=[
            UtcpDotEnv(env_file_path=str(Path(__file__).parent / ".env"))
        ]
    )
    
    # Create and return the UTCP client
    client = await UtcpClient.create(config)
    return client


def get_tools(user_input):
    utcp_client = asyncio.run(initialize_utcp_client())
    tools = asyncio.run(utcp_client.search_tools(query=user_input))
    return tools



def llm_utcp(user_input):

    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
    response = client.models.generate_content(
                model='gemini-2.0-flash-001', 
                contents='Why is the sky blue?',
                config=types.GenerateContentConfig(tools=[get_tools],),
        )       

    return response.text


if __name__ == "__main__":
    load_dotenv(override=True)    
    user_input = "What is the weather like in New York?"
    result = llm_utcp(user_input)
    print(result)


