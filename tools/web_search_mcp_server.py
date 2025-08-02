from mcp.server.fastmcp import FastMCP
from langchain_community.utilities import GoogleSerperAPIWrapper

mcp = FastMCP("web_search_server")

@mcp.tool()
async def search_web(search_query: str) -> float:
    
    # Initialize the Serper API wrapper
    search = GoogleSerperAPIWrapper()
    # Perform the search
    results = search.run(search_query)
    return results


if __name__ == "__main__":
    mcp.run(transport='stdio')