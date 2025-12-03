from fastmcp import FastMCP
import asyncio

# Define subservers
tech_support_mcp = FastMCP(name="TechSupportService")


@tech_support_mcp.tool
def get_ticket_status(ticket_id: str) -> dict:
    """Get ticket status."""
    return {"ticket_id": ticket_id, "status": "in progress"}


@tech_support_mcp.tool
def get_ticket_sla(ticket_id: str) -> dict:
    """Get ticket SLA."""
    return {"ticket_id": ticket_id, "sla": "4 hours"}
