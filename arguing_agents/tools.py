
import time

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import (
    create_sync_playwright_browser,
)
from agents import function_tool

@function_tool
def browse(urls: list[str], goal: str) -> str:
    """
    This tool navigates to web pages and extracts their content using a headless browser.
    It uses Playwright to automate browser interactions and retrieve page elements.
    
    Args:
        urls: A list of URLs to browse and extract content from
        goal: The goal or purpose of browsing (currently not used in implementation)
    
    Returns:
        Combined text content from all browsed pages, joined by newlines
    """
    sync_browser = create_sync_playwright_browser()
    toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
    tools = toolkit.get_tools()

    tools_by_name = {tool.name: tool for tool in tools}
    navigate_tool = tools_by_name["navigate_browser"]
    get_elements_tool = tools_by_name["get_elements"]
    
    responses =[]
    for url in urls:
        print(f"Navigating to {url}")
        navigate_tool.run(url)
        response = get_elements_tool.run("body")
        print(f"Response: {response}")
        responses.append(response)
    
    return "\n".join(responses)

@function_tool
def google_search(queries: list[str]) -> str:

    """
        This tool searches the internet for the query that is being passed.
        This tool can be used for gathering the latest information about the topic.
        This tool uses Google's Search, and returns the context based on the top results obtained.

        Args:
            query: A single search query to execute

        Returns:
            a complete combined context 
    """
    print(f"Searching for {queries}")
    results = []
    for query in queries:
        time.sleep(5)
        search = GoogleSerperAPIWrapper()
        result = search.run(query)
        results.append(result)

    return "\n".join(results)



def execute_tool(tool_name: str, tool_args: dict) -> dict:
    """
    Execute a tool by name with given arguments.
    
    Args:
        tool_name: Name of the tool ('search' or 'browse')
        tool_args: Dictionary of tool arguments
        
    Returns:
        Tool execution results
    """
    if tool_name == "search":
        return google_search(tool_args.get("queries", []))
    elif tool_name == "browse":
        return browse(tool_args.get("urls", []), tool_args.get("goal", ""))
    else:
        return {"error": f"Unknown tool: {tool_name}"}
