import mcp
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from agents import FunctionTool
import json

params = StdioServerParameters(command="uv", args=["run", "tools/web_search_mcp_server.py"], env=None)


async def list_tools():
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            return tools_result.tools


async def call_tool(tool_name, tool_args):
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, tool_args)
            return result
            

async def get_tools_openai():
    openai_tools = []
    for tool in await list_tools():
        schema = {**tool.inputSchema, "additionalProperties": False}
        openai_tool = FunctionTool(
            name=tool.name,
            description=tool.description,
            params_json_schema=schema,
            on_invoke_tool=lambda ctx, args, toolname=tool.name: call_tool(toolname, json.loads(args))                
        )
        openai_tools.append(openai_tool)
    return openai_tools


async def get_function_tools_openai():
    openai_tools = []
    for tool in await list_tools():
        print(f"Tool: {str(tool)}")
        schema = {**tool.inputSchema, "additionalProperties": False}
        openai_tool = {
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": schema,    
            "strict": True,        
        }
        openai_tools.append(openai_tool)
    return openai_tools
