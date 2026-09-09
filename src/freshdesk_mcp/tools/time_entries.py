"""Time entries (billable/non-billable agent time)."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import api_tool, compact


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def list_time_entries(
        agent_id: Optional[int] = None, company_id: Optional[int] = None,
        group_id: Optional[int] = None, executed_after: Optional[str] = None,
        executed_before: Optional[str] = None, billable: Optional[bool] = None,
        page: int = 1, per_page: int = 30, fetch_all: bool = False,
    ) -> Any:
        """List time entries, optionally filtered.

        Args:
            executed_after / executed_before: ISO-8601 timestamps bounding when
                the work was done. Use these for period time reporting.
            billable: Restrict to billable (True) or non-billable (False).
        """
        params = compact(
            agent_id=agent_id, company_id=company_id, group_id=group_id,
            executed_after=executed_after, executed_before=executed_before,
            billable=billable,
        )
        if fetch_all:
            rows = await client.paginate("time_entries", params=params)
            return {"time_entries": rows, "count": len(rows)}
        return await client.get("time_entries", page=page, per_page=per_page, **params)

    @mcp.tool()
    @api_tool
    async def create_time_entry(
        ticket_id: int, time_spent: Optional[str] = None, agent_id: Optional[int] = None,
        billable: Optional[bool] = None, note: Optional[str] = None,
        executed_at: Optional[str] = None, timer_running: Optional[bool] = None,
    ) -> Any:
        """Log time against a ticket.

        Args:
            time_spent: "hh:mm", e.g. "01:30".
            timer_running: Start a live timer instead of logging a fixed amount.
        """
        return await client.post(
            f"tickets/{ticket_id}/time_entries",
            compact(time_spent=time_spent, agent_id=agent_id, billable=billable,
                    note=note, executed_at=executed_at, timer_running=timer_running),
        )

    @mcp.tool()
    @api_tool
    async def update_time_entry(time_entry_id: int, fields: dict) -> Any:
        """Update a time entry, e.g. {"time_spent": "02:00", "billable": true}."""
        return await client.put(f"time_entries/{time_entry_id}", fields)

    @mcp.tool()
    @api_tool
    async def toggle_time_entry_timer(time_entry_id: int) -> Any:
        """Start or stop the timer on a time entry."""
        return await client.put(f"time_entries/{time_entry_id}/toggle_timer")

    @mcp.tool()
    @api_tool
    async def delete_time_entry(time_entry_id: int) -> Any:
        """Delete a time entry."""
        return await client.delete(f"time_entries/{time_entry_id}")
