"""Canned responses and their folders."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def list_canned_response_folders() -> Any:
        """List canned response folders."""
        return await client.get("canned_response_folders")

    @mcp.tool()
    @api_tool
    async def get_canned_response_folder(folder_id: int) -> Any:
        """Retrieve a canned response folder."""
        return await client.get(f"canned_response_folders/{folder_id}")

    @mcp.tool()
    @api_tool
    async def list_canned_responses_in_folder(folder_id: int) -> Any:
        """List the canned responses inside a folder."""
        return await client.get(f"canned_response_folders/{folder_id}/responses")

    @mcp.tool()
    @api_tool
    async def create_canned_response_folder(name: str) -> Any:
        """Create a canned response folder."""
        return await client.post("canned_response_folders", {"name": name})

    @mcp.tool()
    @api_tool
    async def update_canned_response_folder(folder_id: int, name: str) -> Any:
        """Rename a canned response folder."""
        return await client.put(f"canned_response_folders/{folder_id}", {"name": name})

    @mcp.tool()
    @api_tool
    async def get_canned_response(response_id: int) -> Any:
        """Retrieve a canned response."""
        return await client.get(f"canned_responses/{response_id}")

    @mcp.tool()
    @api_tool
    async def create_canned_response(title: str, content_html: str, folder_id: int,
                                     visibility: Optional[int] = None,
                                     group_ids: Optional[list[int]] = None) -> Any:
        """Create a canned response.

        Args:
            visibility: 0 all agents, 1 personal, 2 select groups.
        """
        return await client.post("canned_responses", compact(
            title=title, content_html=content_html, folder_id=folder_id,
            visibility=visibility, group_ids=group_ids))

    @mcp.tool()
    @api_tool
    async def update_canned_response(response_id: int, fields: JSON) -> Any:
        """Update a canned response."""
        return await client.put(f"canned_responses/{response_id}", fields)

    @mcp.tool()
    @api_tool
    async def bulk_create_canned_responses(folder_id: int, responses: list[JSON]) -> Any:
        """Create several canned responses in one call."""
        return await client.post("canned_responses/create_multiple",
                                 {"folder_id": folder_id, "canned_responses": responses})
