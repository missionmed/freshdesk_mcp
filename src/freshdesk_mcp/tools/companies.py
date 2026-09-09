"""Companies and company imports/exports."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def list_companies(page: int = 1, per_page: int = 30,
                             updated_since: Optional[str] = None,
                             fetch_all: bool = False) -> Any:
        """List companies."""
        params = compact(updated_since=updated_since)
        if fetch_all:
            rows = await client.paginate("companies", params=params)
            return {"companies": rows, "count": len(rows)}
        return await client.get("companies", page=page, per_page=per_page, **params)

    @mcp.tool()
    @api_tool
    async def get_company(company_id: int) -> Any:
        """Retrieve a company."""
        return await client.get(f"companies/{company_id}")

    @mcp.tool()
    @api_tool
    async def create_company(
        name: str, domains: Optional[list[str]] = None, description: Optional[str] = None,
        note: Optional[str] = None, health_score: Optional[str] = None,
        account_tier: Optional[str] = None, renewal_date: Optional[str] = None,
        industry: Optional[str] = None, lookup_parameter: Optional[str] = None,
        custom_fields: Optional[JSON] = None,
    ) -> Any:
        """Create a company."""
        return await client.post("companies", compact(
            name=name, domains=domains, description=description, note=note,
            health_score=health_score, account_tier=account_tier,
            renewal_date=renewal_date, industry=industry,
            lookup_parameter=lookup_parameter, custom_fields=custom_fields))

    @mcp.tool()
    @api_tool
    async def update_company(company_id: int, fields: JSON) -> Any:
        """Update a company."""
        return await client.put(f"companies/{company_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_company(company_id: int) -> Any:
        """Delete a company. Its contacts are kept but unlinked."""
        return await client.delete(f"companies/{company_id}")

    @mcp.tool()
    @api_tool
    async def search_companies(query: str, page: int = 1) -> Any:
        """Search companies with the filter query language."""
        return await client.get("search/companies", query=f'"{query}"', page=page)

    @mcp.tool()
    @api_tool
    async def autocomplete_companies(name: str) -> Any:
        """Look up companies by partial name."""
        return await client.get("companies/autocomplete", name=name)

    @mcp.tool()
    @api_tool
    async def export_companies(fields: JSON) -> Any:
        """Start a company export job; poll the id with get_export_job."""
        return await client.post("companies/export", {"fields": fields})

    @mcp.tool()
    @api_tool
    async def list_company_imports() -> Any:
        """List company import jobs."""
        return await client.get("companies/imports")

    @mcp.tool()
    @api_tool
    async def get_company_import(import_id: int) -> Any:
        """Check the status of a company import."""
        return await client.get(f"companies/imports/{import_id}")

    @mcp.tool()
    @api_tool
    async def cancel_company_import(import_id: int) -> Any:
        """Cancel a running company import."""
        return await client.put(f"companies/imports/{import_id}/cancel")
