import asyncio
import json
from typing import Any
import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts.in_memory_artifact_service import (
    InMemoryArtifactService,  # Optional
)
from google.adk.runners import Runner, InMemoryRunner
from google.adk.sessions import InMemorySessionService

from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams, StdioServerParameters,
    SseConnectionParams, StreamableHTTPConnectionParams
)
from google.genai import types
from narwhals import String
from rich import print

load_dotenv(override=True)


async def get_tools_async():
    toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uv",
                    args=[
                        "--directory",
                        "D:/GitHub/gmail-mcp/src/gmail",
                        "run",
                        "server.py",
                        # "run",
                        # "D:/GitHub/gmail-mcp/src/gmail/server.py",
                        "--creds-file-path",
                        "D:/GitHub/gmail-mcp/credentials.json",
                        "--token-path",
                        "D:/GitHub/gmail-mcp/tokens.json"
                    ]
                ),
                timeout=120,
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # tool_filter=['list_directory', 'read_file']
        )
    try:
        tools = await toolset.get_tools()
        print(f"Retrieved {len(tools)} tools from MCP server.")
        for tool in tools:
            print(f"- Tool: {tool.name}, Description: {tool.description}")
        return tools
    except Exception as e:
        # Surface errors with more context so it's easier to debug the stdio client
        print(f"Error while fetching tools from MCP server: {e}")
        raise
    finally:
        # Note: if MCPToolset exposes an explicit shutdown/close API, call it here.
        # Many stdio-based clients need an orderly shutdown; leaving this block
        # in place makes it easy to add a cleanup call if available.
        pass

async def get_tools_sse_async():
    toolset = MCPToolset(
            connection_params=SseConnectionParams(
                url="http://localhost:8000/sse",
                timeout=120,
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # tool_filter=['list_directory', 'read_file']
        )
    try:
        tools = await toolset.get_tools()
        print(f"Retrieved {len(tools)} tools from MCP server.")
        for tool in tools:
            print(f"- Tool: {tool.name}, Description: {tool.description}")
        return tools
    except Exception as e:
        # Surface errors with more context so it's easier to debug the stdio client
        print(f"Error while fetching tools from MCP server: {e}")
        raise
    finally:
        # Note: if MCPToolset exposes an explicit shutdown/close API, call it here.
        # Many stdio-based clients need an orderly shutdown; leaving this block
        # in place makes it easy to add a cleanup call if available.
        pass


async def get_tools_shttp_async():
    toolset = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="http://localhost:8000/mcp",
                timeout=120,
                terminate_on_close=True,
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # tool_filter=['list_directory', 'read_file']
        )
    try:
        tools = await toolset.get_tools()
        print(f"Retrieved {len(tools)} tools from MCP server.")
        for tool in tools:
            print(f"- Tool: {tool.name}, Description: {tool.description}")
        return tools
    except Exception as e:
        # Surface errors with more context so it's easier to debug the stdio client
        print(f"Error while fetching tools from MCP server: {e}")
        raise
    finally:
        # Note: if MCPToolset exposes an explicit shutdown/close API, call it here.
        # Many stdio-based clients need an orderly shutdown; leaving this block
        # in place makes it easy to add a cleanup call if available.
        pass


async def get_agent_async():
    """Creates an ADK Agent equipped with tools from the MCP Server."""

    tools = await get_tools_shttp_async()

    root_agent = LlmAgent(
        model="gemini-2.0-flash",
        name="assistant",
        instruction="""You are a helpful assistant that can use various gmail tools to perform tasks.""",
        tools=tools,
    )
    return root_agent


async def agent_run():
        root_agent = await get_agent_async()
        print("\n\nAgent created successfully.\n\n")

        USER_ID = "123"
        SESSION_ID = "chat123"
        prompt = "show me latest emails from medium"
        message = types.Content(role="user", parts=[types.Part(text=prompt)])     

        session_service = InMemorySessionService()
        await session_service.create_session(app_name="GmailChatbotApp", user_id=USER_ID, session_id=SESSION_ID)
        runner = Runner(agent=root_agent, app_name="GmailChatbotApp", session_service=session_service)

        print("\n\nAgent runner created successfully.\n\n")

        events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=message)
        print(f"\n\nAgent executed successfully.\n\n")
        
        for event in events:
            print(f" response: {event.get_function_responses()}")
            print(f" function call: {event.get_function_calls()}")
        print("\n\Results extracted successfully.\n\n")
        

def main():
    # Run the async startup inside the __main__ guard to avoid running
    # event loop work at import time. Running async code at module import
    # can cause generators used by stdio clients to be closed unexpectedly
    # (raising GeneratorExit) when the import or shutdown happens.

    try:
        asyncio.run(agent_run())
        
    except Exception as e:
        # Catch broad exceptions and show a helpful message. Avoid catching
        # BaseException here (e.g., KeyboardInterrupt/GeneratorExit) unless
        # you intentionally want to swallow those signals.
        print(f"Failed to create or run agent: {e}")


if __name__ == "__main__":
    main()