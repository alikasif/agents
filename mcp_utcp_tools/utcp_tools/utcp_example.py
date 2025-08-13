
import asyncio
import os
import json
import sys
import re
from pathlib import Path
from typing import Dict, Any, List
from agents import FunctionTool

import openai
from dotenv import load_dotenv

from utcp.client.utcp_client import UtcpClient
from utcp.client.utcp_client_config import UtcpClientConfig, UtcpDotEnv
from utcp.shared.tool import Tool

# https://github.com/universal-tool-calling-protocol/utcp-examples

async def initialize_utcp_client() -> UtcpClient:
    """Initialize the UTCP client with configuration."""
    # Create a configuration for the UTCP client
    config = UtcpClientConfig(
        providers_file_path=str(Path(__file__).parent / "providers.json"),
        load_variables_from=[
            UtcpDotEnv(env_file_path=str(Path(__file__).parent / ".env"))
        ]
    )
    
    # Create and return the UTCP client
    client = await UtcpClient.create(config)
    return client


def sanitize_tool_name(name: str) -> str:
    """
    Sanitize tool name to match OpenAI's pattern requirement: ^[a-zA-Z0-9_-]+$
    """
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    if not sanitized or not re.match(r'^[a-zA-Z0-9]', sanitized):
        sanitized = 'tool_' + sanitized
    return sanitized


async def utcp_tool_to_open_ai_agent_tool(search_query: str) -> List[Tool]:
    """
    Creates a FunctionTool that wraps a UTCP tool,
    making it compatible with the openai-agents library.
    """
    utcp_client = await initialize_utcp_client()
    
    async def utcp_tool_handler(ctx, args: str) -> str:
        """
        Handler function for the UTCP tool invocation.
        """
        print(f"\nCalling tool: {tool.name} with args: {args}")
        try:
            kwargs = json.loads(args) if args.strip() else {}
            
            result = await utcp_client.call_tool(tool.name, kwargs)
            print(f"Tool {tool.name} executed successfully. Result: {result}")
            
            if isinstance(result, (dict, list)):
                return json.dumps(result)
            else:
                return str(result)
        except Exception as e:
            print(f"Error calling tool {tool.name}: {e}")
            return f"Error: {str(e)}"


    relevant_tools = await utcp_client.search_tools(search_query, limit=10)
    tools=[]
    for tool in relevant_tools:
        params_schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
        
        if tool.inputs and tool.inputs.properties:
            for prop_name, prop_schema in tool.inputs.properties.items():
                params_schema["properties"][prop_name] = prop_schema
            
            if tool.inputs.required:
                params_schema["required"] = tool.inputs.required

        sanitized_name = sanitize_tool_name(tool.name)
        tools.append(FunctionTool(
            name=sanitized_name,
            description=tool.description or f"No description available for {tool.name}.",
            params_json_schema=params_schema,
            on_invoke_tool=utcp_tool_handler,
        ))
    return tools

