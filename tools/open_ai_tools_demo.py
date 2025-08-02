from openai import OpenAI
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from web_search_mcp_client import get_tools_openai, list_tools, call_tool
import asyncio
from agents.mcp import MCPServerStdio
import os

def call_openai_with_tool(search_query, tools):

    client = OpenAI()

    # Make an API call to the responses endpoint, enabling the web_search_preview tool
    response = client.responses.create(
        model="gpt-4o",  # Or another suitable model like gpt-4o-mini
        tools=tools,
        #tool_choice="auto",  # Automatically choose the best tool based on the query
        input=search_query,
    )
    return response


def search_function_using_serper(search_query: str):
    # Initialize the Serper API wrapper
    search = GoogleSerperAPIWrapper()
    # Perform the search
    results = search.run(search_query)
    return results


def tool_search_function():

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
    return call_openai_with_tool(search_query, [{"type": "web_search_preview"}])
    

def call_openai_with_function_as_web_search_tool(search_query):
    return call_openai_with_tool(search_query, tool_search_function())  
   
async def call_openai_with_function_as_mcp(search_query):
   
    server_script = os.path.join(os.path.dirname(__file__), "web_search_mcp_server.py")

    params = {"command": "uv", "args": ["run", "{server_script}"], "env": None}
    async with MCPServerStdio(params=params, client_session_timeout_seconds=60) as server:
        await asyncio.sleep(2)  # Wait for the server to start
        mcp_tools = await server.list_tools()
        print(f"Available tools: {str(mcp_tools)}")

       #tools = await get_tools_openai()
       #print(f"Available tools: {str(tools)}")
       #return call_openai_with_tool(search_query, tools)


if __name__ == "__main__":
    load_dotenv(override=True)

    asyncio.run(call_openai_with_function_as_mcp("test"))

    # user_input = input("Enter your query: ")

    # response1 = call_openai_with_hosted_web_search_tool(user_input)
    # response2 = call_openai_with_function_as_web_search_tool(user_input)
    # response3 = asyncio.run(call_openai_with_function_as_mcp(user_input))
    
    # print(f" response1: {response1.output_text}")
    # print(f" response2: {response2.output_text}")
    # print(f" response3: {response3.output_text}")