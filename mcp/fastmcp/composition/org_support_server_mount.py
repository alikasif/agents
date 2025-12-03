from fastmcp import FastMCP
import asyncio
from hr_support_server import hr_support_mcp
from tech_support_server import tech_support_mcp

main_mcp = FastMCP(name="MainMCPMount")

main_mcp.mount(hr_support_mcp, prefix="hr")
main_mcp.mount(tech_support_mcp, prefix="tech")


if __name__ == "__main__":    
    main_mcp.run(transport="streamable-http", host="127.0.0.1", port=8282)
