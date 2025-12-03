from fastmcp import FastMCP
import asyncio
from hr_support_server import hr_support_mcp
from tech_support_server import tech_support_mcp

main_mcp = FastMCP(name="MainMCPImport")

# Import subserver
async def setup():
    await main_mcp.import_server(hr_support_mcp, prefix="hr")
    await main_mcp.import_server(tech_support_mcp, prefix="tech")


if __name__ == "__main__":
    asyncio.run(setup())    
    main_mcp.run(transport="streamable-http", host="127.0.0.1", port=8282)
