from langchain_community.utilities import GoogleSerperAPIWrapper
from agents import Agent, FileSearchTool, Runner, WebSearchTool, FunctionTool, RunContextWrapper, function_tool
from mcp_tools.web_search_mcp_client import get_agent_tools_openai
import asyncio
from dotenv import load_dotenv
import os
from utcp_tools.utcp_example import initialize_utcp_client, utcp_tool_to_open_ai_agent_tool
from utcp.client.utcp_client import UtcpClient
from utcp.shared.tool import Tool


def get_gpt_agent(model, instructions, tools):
    """
    Returns an OpenAI Agents SDK Agent configured to use a GPT model with detailed prompt engineering instructions.
    """
   
    return Agent(
        name="GPTToolsAgent",
        instructions=instructions,
        model=model,
        tools=tools)


async def call_agent_with_hosted_web_search_tool(search_query):
    """Uses OpenAI's built-in web search preview tool to process query."""

    tools =[WebSearchTool()]
    agent = get_gpt_agent(
        model= os.getenv("OPENAI_MODEL"),  # Or another suitable model like gpt-4o-mini
        instructions="You are a web search agent. Use the provided tools to search the web.",
        tools=tools
    )

    result = await Runner.run(agent, search_query)
    print(f"\nSearch results from hosted tool: {result}")

@function_tool
async def search_function_using_serper(search_query: str):
    """Performs web search using Google Serper API and returns results."""
    # Initialize the Serper API wrapper
    search = GoogleSerperAPIWrapper()
    # Perform the search
    results = search.run(search_query)
    return results

async def call_agent_with_function_as_tool(search_query):
    """Uses OpenAI's built-in web search preview tool to process query."""
    agent = get_gpt_agent(
        model= os.getenv("OPENAI_MODEL"),  # Or another suitable model like gpt-4o-mini
        instructions="You are a web search agent. Use the provided tools to search the web.",
        tools=[search_function_using_serper]
    )
    result = await Runner.run(agent, search_query)
    print(f"\nSearch results from function tool: {result}")



async def call_agent_with_mcp_tool(search_query):
    """Uses MCP-based web search tools with OpenAI to process query."""

    tools = await get_agent_tools_openai()
    
    agent = get_gpt_agent(
        model= os.getenv("OPENAI_MODEL"),  # Or another suitable model like gpt-4o-mini
        instructions="You are a web search agent. Use the provided tools to search the web.",
        tools=tools
    )
    result = await Runner.run(agent, search_query)
    print(f"\nSearch results from MCP tool: {result}")


async def call_agent_with_utcp_tool(search_query):
    """Uses UTCP-based web search tools with OpenAI to process query."""

    tools = await utcp_tool_to_open_ai_agent_tool(search_query)
    
    agent = get_gpt_agent(
        model= os.getenv("OPENAI_MODEL"),  # Or another suitable model like gpt-4o-mini
        instructions="You are a web search agent. Use the provided tools to search the web.",
        tools=tools
    )
    result = await Runner.run(agent, search_query)
    print(f"\nSearch results from UTCP tool: {result}")


if __name__ == "__main__":
    load_dotenv(override=True)  # Load environment variables from .env file if needed
    search_query = input("Enter your search query: ")
    asyncio.run(call_agent_with_hosted_web_search_tool(search_query))
    asyncio.run(call_agent_with_function_as_tool(search_query))
    asyncio.run(call_agent_with_mcp_tool(search_query))
    asyncio.run(call_agent_with_utcp_tool(search_query))
    
    print("Search completed.")

    