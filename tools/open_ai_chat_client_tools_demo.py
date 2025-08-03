from openai import AsyncOpenAI, OpenAI
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from mcp_tools.web_search_mcp_client import list_tools, call_tool, get_function_tools_openai
import asyncio
from agents.mcp import MCPServerStdio
import os
import re
from utcp_tools.utcp_example import initialize_utcp_client
from utcp.client.utcp_client import UtcpClient
from utcp.shared.tool import Tool


def call_openai_with_tool(search_query, tools):
    """Makes a synchronous call to OpenAI API with specified tools and search query."""

    client = OpenAI()

    # Make an API call to the responses endpoint, enabling the web_search_preview tool
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL"),
        tools=tools,
        #tool_choice="auto",  # Automatically choose the best tool based on the query
        input=search_query,
    )
    return response


async def call_async_openai_with_tool(messages, tools):
    """Makes an asynchronous call to OpenAI chat completion API with tools."""

    client = AsyncOpenAI()

    # Make an API call to the responses endpoint, enabling the web_search_preview tool
    response = await client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        tools=tools,
        #tool_choice="auto",  # Automatically choose the best tool based on the query
        messages=messages,
    )
    return response


def search_function_using_serper(search_query: str):
    """Performs web search using Google Serper API and returns results."""

    # Initialize the Serper API wrapper
    search = GoogleSerperAPIWrapper()
    # Perform the search
    results = search.run(search_query)
    return results


def tool_search_function():
    """Creates OpenAI function tool configuration for Serper web search."""

    tools = [
        {
            "type": "function",
            "name": "search_function_using_serper",
            "description": "Search internet using Serper API",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {"type": "string", "description": "search query to find relevant information"},      
                },
                "required": ["search_query"],
                "additionalProperties": False,
            },                
            "strict": True,
        },
    ]
    return tools


def call_openai_with_hosted_web_search_tool(search_query):
    """Uses OpenAI's built-in web search preview tool to process query."""

    return call_openai_with_tool(search_query, [{"type": "web_search_preview"}])
    

def call_openai_with_function_as_web_search_tool(search_query):
    """Uses custom Serper search function as OpenAI tool to process query."""

    return call_openai_with_tool(search_query, tool_search_function())  
   

async def call_openai_with_mcp_web_search_tool(search_query):
    """Uses MCP-based web search tools with OpenAI to process query."""

    tools = await get_function_tools_openai()
    print(f"Available tools: {str(tools)}")
    return call_openai_with_tool(search_query, tools)


async def invoke_utcp_tool(tool_name: str, args: str):
    """Executes a UTCP tool with specified name and arguments."""

    print(f"Invoking UTCP tool: {tool_name} with args: {args}")
    
    # Initialize the UTCP client
    utcp_client = await initialize_utcp_client()
    
    # Call the tool
    try:
        result = await utcp_client.call_tool(tool_name, {"query": args})
        print(f"UTCP tool {tool_name} invoked.")
        return result
    except Exception as e:
        print(f"Error calling tool {tool_name}: {e}")
        return str(e)


def utcp_tool_async_open_ai_json_schema(utcp_tool: Tool):
    """Converts UTCP tool definition to OpenAI-compatible function schema."""

    openai_tool = {
            "type": "function",
            "function": {
                "name": "invoke_utcp_tool",
                "description": "A tool that performs an asynchronous operation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string", "description": f"{utcp_tool.name}"},
                        "args": {"type": "string", "description": "arguments for the tool call"},
                    },
                    "required": ["tool_name", "args"],
                },
            },
        }
    return openai_tool  


async def call_openai_with_utcp_web_search_tool(search_query):
    """Processes search query using UTCP tools through OpenAI chat completion."""

    print("Initializing UTCP client...")
    utcp_client = await initialize_utcp_client()
    print("UTCP client initialized successfully.")

    print("\nSearching for relevant tools...")
    relevant_tools = await utcp_client.search_tools(search_query, limit=10)
    
    if relevant_tools:
        for tool in relevant_tools:
            print(f"UTCP => {tool.name}")                     
    else:
        print("No relevant tools found.")

    openai_wrapped_utcp_tools = [utcp_tool_async_open_ai_json_schema(tool) for tool in relevant_tools]    

    user_input = f"you are a helpful assistant. you must use he tool invoke_utcp_tool to answer the query: {search_query}"

    messages = [
        {"role": "system", "content": "You are a helpful assistant. You must use tools to answer the user's query."},
        {"role": "user", "content": user_input}
    ]

    print("\nSending request to OpenAI...")

    chat_completion = await call_async_openai_with_tool(messages, openai_wrapped_utcp_tools)
    result=""
    if chat_completion.choices[0].message.tool_calls:
        for tool_call in chat_completion.choices[0].message.tool_calls:
            if tool_call.function.name == "invoke_utcp_tool":
                args = eval(tool_call.function.arguments)  # Caution: Use with trusted input                
                result = await invoke_utcp_tool(**args)
                #print(f"Tool output: {result}")
                # Optionally, send the tool output back to the model for further conversation
    else:
        print(f"Model response: {chat_completion.choices[0].message.content}")

    return result


if __name__ == "__main__":
    load_dotenv(override=True)   

    user_input = input("Enter your query: ")

    response1 = call_openai_with_hosted_web_search_tool(user_input)
    response2 = call_openai_with_function_as_web_search_tool(user_input)
    response3 = asyncio.run(call_openai_with_mcp_web_search_tool(user_input))
    response4 = asyncio.run(call_openai_with_utcp_web_search_tool(user_input))
    
    print(f"\nresponse1: {response1.output_text}")
    print(f"\nresponse2: {response2.output_text}")
    print(f"\nresponse3: {response3.output_text}")
    print(f"\nresponse4: {response4}")