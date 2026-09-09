"""Customer satisfaction: the new surveys API and the legacy ratings API."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import api_tool, compact


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def list_csat_surveys() -> Any:
        """List CSAT surveys (current customer-satisfaction API)."""
        return await client.get("customer-satisfaction/surveys")

    @mcp.tool()
    @api_tool
    async def list_csat_responses(
        survey_id: int, created_after: Optional[str] = None,
        created_before: Optional[str] = None, page: int = 1, per_page: int = 30,
        fetch_all: bool = False,
    ) -> Any:
        """List responses to a CSAT survey.

        Args:
            survey_id: From list_csat_surveys.
            created_after / created_before: ISO-8601 bounds for period reporting.
        """
        path = f"customer-satisfaction/surveys/{survey_id}/responses"
        params = compact(created_after=created_after, created_before=created_before)
        if fetch_all:
            rows = await client.paginate(path, params=params)
            return {"responses": rows, "count": len(rows)}
        return await client.get(path, page=page, per_page=per_page, **params)

    @mcp.tool()
    @api_tool
    async def create_csat_response(survey_id: int, payload: dict) -> Any:
        """Submit a survey response."""
        return await client.post(f"customer-satisfaction/surveys/{survey_id}/responses", payload)

    @mcp.tool()
    @api_tool
    async def list_legacy_surveys() -> Any:
        """List surveys via the legacy satisfaction API."""
        return await client.get("surveys")

    @mcp.tool()
    @api_tool
    async def list_satisfaction_ratings(
        created_since: Optional[str] = None, user_id: Optional[int] = None,
        page: int = 1, per_page: int = 30, fetch_all: bool = False,
    ) -> Any:
        """List all satisfaction ratings (legacy API). Feeds CSAT reporting."""
        params = compact(created_since=created_since, user_id=user_id)
        if fetch_all:
            rows = await client.paginate("surveys/satisfaction_ratings", params=params)
            return {"ratings": rows, "count": len(rows)}
        return await client.get(
            "surveys/satisfaction_ratings", page=page, per_page=per_page, **params
        )

    @mcp.tool()
    @api_tool
    async def list_ticket_satisfaction_ratings(ticket_id: int) -> Any:
        """List satisfaction ratings left on one ticket."""
        return await client.get(f"tickets/{ticket_id}/satisfaction_ratings")

    @mcp.tool()
    @api_tool
    async def create_satisfaction_rating(ticket_id: int, ratings: dict, feedback: Optional[str] = None) -> Any:
        """Create a satisfaction rating on a ticket (legacy API)."""
        return await client.post(
            f"tickets/{ticket_id}/satisfaction_ratings",
            compact(ratings=ratings, feedback=feedback),
        )
