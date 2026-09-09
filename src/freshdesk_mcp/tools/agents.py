"""Agents, their availability, and skills/roles."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def list_agents(email: Optional[str] = None, mobile: Optional[str] = None,
                          phone: Optional[str] = None, state: Optional[str] = None,
                          page: int = 1, per_page: int = 30, fetch_all: bool = False) -> Any:
        """List agents.

        Args:
            state: "fulltime" or "occasional".
        """
        params = compact(email=email, mobile=mobile, phone=phone, state=state)
        if fetch_all:
            rows = await client.paginate("agents", params=params)
            return {"agents": rows, "count": len(rows)}
        return await client.get("agents", page=page, per_page=per_page, **params)

    @mcp.tool()
    @api_tool
    async def get_agent(agent_id: int) -> Any:
        """Retrieve an agent."""
        return await client.get(f"agents/{agent_id}")

    @mcp.tool()
    @api_tool
    async def get_current_agent() -> Any:
        """Details of the agent whose API key is in use. Handy for a config check."""
        return await client.get("agents/me")

    @mcp.tool()
    @api_tool
    async def create_agent(email: str, ticket_scope: int = 1, name: Optional[str] = None,
                           occasional: bool = False, role_ids: Optional[list[int]] = None,
                           group_ids: Optional[list[int]] = None,
                           skill_ids: Optional[list[int]] = None,
                           signature: Optional[str] = None,
                           focus_mode: Optional[bool] = None) -> Any:
        """Create an agent.

        Args:
            ticket_scope: 1 global, 2 group, 3 restricted.
        """
        return await client.post("agents", compact(
            email=email, ticket_scope=ticket_scope, name=name, occasional=occasional,
            role_ids=role_ids, group_ids=group_ids, skill_ids=skill_ids,
            signature=signature, focus_mode=focus_mode))

    @mcp.tool()
    @api_tool
    async def create_multiple_agents(agents: list[JSON]) -> Any:
        """Create several agents at once (async job)."""
        return await client.post("agents/multiple", {"agents": agents})

    @mcp.tool()
    @api_tool
    async def update_agent(agent_id: int, fields: JSON) -> Any:
        """Update an agent."""
        return await client.put(f"agents/{agent_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_agent(agent_id: int) -> Any:
        """Downgrade an agent back to a contact."""
        return await client.delete(f"agents/{agent_id}")

    @mcp.tool()
    @api_tool
    async def search_agents(term: str) -> Any:
        """Find agents by partial name or email."""
        return await client.get("agents/autocomplete", term=term)

    @mcp.tool()
    @api_tool
    async def list_agent_availability(page: int = 1, per_page: int = 30) -> Any:
        """List availability//load for all agents (omnichannel)."""
        return await client.get("agents/availability", page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def get_agent_availability(agent_id: int) -> Any:
        """Availability for a single agent."""
        return await client.get(f"agents/{agent_id}/availability")

    @mcp.tool()
    @api_tool
    async def update_agent_load_settings(agent_id: int, fields: JSON) -> Any:
        """Update an agent's omnichannel load settings."""
        return await client.put(f"agents/{agent_id}/load_settings", fields)

    # --- skills / roles -------------------------------------------------
    @mcp.tool()
    @api_tool
    async def list_skills(page: int = 1, per_page: int = 30) -> Any:
        """List agent skills."""
        return await client.get("skills", page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def get_skill(skill_id: int) -> Any:
        """Retrieve a skill."""
        return await client.get(f"admin/skills/{skill_id}")

    @mcp.tool()
    @api_tool
    async def create_skill(name: str, rank: Optional[int] = None,
                           agent_ids: Optional[list[int]] = None,
                           conditions: Optional[JSON] = None,
                           match_type: Optional[str] = None) -> Any:
        """Create a skill."""
        return await client.post("admin/skills", compact(
            name=name, rank=rank, agent_ids=agent_ids, conditions=conditions,
            match_type=match_type))

    @mcp.tool()
    @api_tool
    async def update_skill(skill_id: int, fields: JSON) -> Any:
        """Update a skill."""
        return await client.put(f"admin/skills/{skill_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_skill(skill_id: int) -> Any:
        """Delete a skill."""
        return await client.delete(f"admin/skills/{skill_id}")

    @mcp.tool()
    @api_tool
    async def list_roles(page: int = 1, per_page: int = 30) -> Any:
        """List agent roles."""
        return await client.get("roles", page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def get_role(role_id: int) -> Any:
        """Retrieve a role."""
        return await client.get(f"roles/{role_id}")
