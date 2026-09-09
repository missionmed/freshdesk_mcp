"""Collaboration threads and their messages (Freshdesk 'Threads' / discussions on a ticket)."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def create_thread(payload: JSON) -> Any:
        """Create a collaboration thread.

        Args:
            payload: e.g. {"type": "forward", "parent": {"id": 123,
                "type": "ticket"}, "participants": {"agents": [1]},
                "title": "...", "created_by": 1}.
        """
        return await client.post("collaboration/threads", payload)

    @mcp.tool()
    @api_tool
    async def get_thread(thread_id: int) -> Any:
        """Retrieve a collaboration thread."""
        return await client.get(f"collaboration/threads/{thread_id}")

    @mcp.tool()
    @api_tool
    async def update_thread(thread_id: int, fields: JSON) -> Any:
        """Update a collaboration thread."""
        return await client.put(f"collaboration/threads/{thread_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_thread(thread_id: int) -> Any:
        """Delete a collaboration thread."""
        return await client.delete(f"collaboration/threads/{thread_id}")

    @mcp.tool()
    @api_tool
    async def create_thread_message(thread_id: int, payload: JSON) -> Any:
        """Post a message into a thread."""
        return await client.post(f"collaboration/threads/{thread_id}/messages", payload)

    @mcp.tool()
    @api_tool
    async def get_thread_message(message_id: int) -> Any:
        """Retrieve a thread message."""
        return await client.get(f"collaboration/messages/{message_id}")

    @mcp.tool()
    @api_tool
    async def update_thread_message(message_id: int, fields: JSON) -> Any:
        """Update a thread message."""
        return await client.put(f"collaboration/messages/{message_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_thread_message(message_id: int) -> Any:
        """Delete a thread message."""
        return await client.delete(f"collaboration/messages/{message_id}")

    @mcp.tool()
    @api_tool
    async def get_thread_message_quote(message_id: int) -> Any:
        """Get the quoted text for a thread message."""
        return await client.get(f"collaboration/messages/{message_id}/generate-quote")
