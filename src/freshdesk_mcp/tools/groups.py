"""Groups (support queues) including the omnichannel admin variants."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def list_groups(page: int = 1, per_page: int = 30, fetch_all: bool = False) -> Any:
        """List groups."""
        if fetch_all:
            rows = await client.paginate("groups")
            return {"groups": rows, "count": len(rows)}
        return await client.get("groups", page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def get_group(group_id: int) -> Any:
        """Retrieve a group."""
        return await client.get(f"groups/{group_id}")

    @mcp.tool()
    @api_tool
    async def create_group(name: str, description: Optional[str] = None,
                           agent_ids: Optional[list[int]] = None,
                           auto_ticket_assign: Optional[int] = None,
                           escalate_to: Optional[int] = None,
                           unassigned_for: Optional[str] = None,
                           business_hours_id: Optional[int] = None) -> Any:
        """Create a group.

        Args:
            unassigned_for: e.g. "30m", "1h", "12h".
        """
        return await client.post("groups", compact(
            name=name, description=description, agent_ids=agent_ids,
            auto_ticket_assign=auto_ticket_assign, escalate_to=escalate_to,
            unassigned_for=unassigned_for, business_hours_id=business_hours_id))

    @mcp.tool()
    @api_tool
    async def update_group(group_id: int, fields: JSON) -> Any:
        """Update a group."""
        return await client.put(f"groups/{group_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_group(group_id: int) -> Any:
        """Delete a group."""
        return await client.delete(f"groups/{group_id}")

    @mcp.tool()
    @api_tool
    async def list_omnichannel_groups(page: int = 1, per_page: int = 30) -> Any:
        """List omnichannel (admin) groups."""
        return await client.get("admin/groups", page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def get_omnichannel_group(group_id: int) -> Any:
        """Retrieve an omnichannel group."""
        return await client.get(f"admin/groups/{group_id}")

    @mcp.tool()
    @api_tool
    async def create_omnichannel_group(payload: JSON) -> Any:
        """Create an omnichannel group."""
        return await client.post("admin/groups", payload)

    @mcp.tool()
    @api_tool
    async def update_omnichannel_group(group_id: int, fields: JSON) -> Any:
        """Update an omnichannel group."""
        return await client.put(f"admin/groups/{group_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_omnichannel_group(group_id: int) -> Any:
        """Delete an omnichannel group."""
        return await client.delete(f"admin/groups/{group_id}")

    @mcp.tool()
    @api_tool
    async def list_group_agents(group_id: int) -> Any:
        """List agents in an omnichannel group."""
        return await client.get(f"admin/groups/{group_id}/agents")

    @mcp.tool()
    @api_tool
    async def update_group_agents(group_id: int, agents: list[JSON]) -> Any:
        """Add or remove agents in an omnichannel group."""
        return await client.put(f"admin/groups/{group_id}/agents", {"agents": agents})
