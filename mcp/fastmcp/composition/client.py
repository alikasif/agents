import asyncio
from fastmcp import Client, FastMCP


# HTTP server
client = Client("http://127.0.0.1:8282/mcp")


async def main():
    async with client:
        # Basic server interaction
        await client.ping()
        
        # List available operations
        tools = await client.list_tools()
        for tool in tools:
            print(f"\ntool: {tool}")
        
        resources = await client.list_resources()
        print(f"\n\nresources: {resources}")
        
        prompts = await client.list_prompts()
        print(f"\n\nprompts: {prompts}")
        
        # Execute operations
        result = await client.call_tool("hr_get_ticket_status", {"ticket_id": "12345"})
        print(f"\n\nresult: {result}")

        result = await client.call_tool("tech_get_ticket_status", {"ticket_id": "12345"})
        print(f"\n\nresult: {result}")
        
        # fails as the main mcp server has statically imported the hr server
        result = await client.call_tool("hr_get_ticket_sla", {"ticket_id": "12345"})
        print(f"\n\nresult: {result}")
        
        # fails as the main mcp server has statically imported the hr server
        result = await client.call_tool("tech_get_ticket_sla", {"ticket_id": "12345"})
        print(f"\n\nresult: {result}")

asyncio.run(main())