"""Contacts (requesters) and contact imports/exports."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def list_contacts(
        email: Optional[str] = None, mobile: Optional[str] = None,
        phone: Optional[str] = None, company_id: Optional[int] = None,
        state: Optional[str] = None, updated_since: Optional[str] = None,
        page: int = 1, per_page: int = 30, fetch_all: bool = False,
        max_items: Optional[int] = None,
    ) -> Any:
        """List contacts.

        Args:
            state: "verified", "unverified", "blocked" or "deleted".
            updated_since: ISO-8601; only contacts changed since then.
            fetch_all: Page through every match.
        """
        params = compact(email=email, mobile=mobile, phone=phone,
                         company_id=company_id, state=state, updated_since=updated_since)
        if fetch_all:
            rows = await client.paginate("contacts", params=params, max_items=max_items)
            return {"contacts": rows, "count": len(rows)}
        return await client.get("contacts", page=page, per_page=per_page, **params)

    @mcp.tool()
    @api_tool
    async def get_contact(contact_id: int) -> Any:
        """Retrieve a contact."""
        return await client.get(f"contacts/{contact_id}")

    @mcp.tool()
    @api_tool
    async def create_contact(
        name: str, email: Optional[str] = None, phone: Optional[str] = None,
        mobile: Optional[str] = None, company_id: Optional[int] = None,
        unique_external_id: Optional[str] = None, twitter_id: Optional[str] = None,
        address: Optional[str] = None, description: Optional[str] = None,
        job_title: Optional[str] = None, tags: Optional[list[str]] = None,
        time_zone: Optional[str] = None, language: Optional[str] = None,
        other_emails: Optional[list[str]] = None, custom_fields: Optional[JSON] = None,
    ) -> Any:
        """Create a contact. Needs at least one of email, phone, mobile,
        twitter_id or unique_external_id."""
        return await client.post("contacts", compact(
            name=name, email=email, phone=phone, mobile=mobile, company_id=company_id,
            unique_external_id=unique_external_id, twitter_id=twitter_id, address=address,
            description=description, job_title=job_title, tags=tags, time_zone=time_zone,
            language=language, other_emails=other_emails, custom_fields=custom_fields))

    @mcp.tool()
    @api_tool
    async def update_contact(contact_id: int, fields: JSON) -> Any:
        """Update a contact with the given fields."""
        return await client.put(f"contacts/{contact_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_contact(contact_id: int) -> Any:
        """Soft-delete a contact (restorable)."""
        return await client.delete(f"contacts/{contact_id}")

    @mcp.tool()
    @api_tool
    async def hard_delete_contact(contact_id: int, force: bool = False) -> Any:
        """Permanently delete a contact. Irreversible.

        Args:
            force: Also permanently delete a contact that was not soft-deleted first.
        """
        return await client.delete(f"contacts/{contact_id}/hard_delete", force=force or None)

    @mcp.tool()
    @api_tool
    async def restore_contact(contact_id: int) -> Any:
        """Restore a soft-deleted contact."""
        return await client.put(f"contacts/{contact_id}/restore")

    @mcp.tool()
    @api_tool
    async def search_contacts(query: str, page: int = 1) -> Any:
        """Search contacts, e.g. name:'john' OR email:'john@x.com'."""
        return await client.get("search/contacts", query=f'"{query}"', page=page)

    @mcp.tool()
    @api_tool
    async def autocomplete_contacts(term: str) -> Any:
        """Fast contact lookup by partial name or email."""
        return await client.get("contacts/autocomplete", term=term)

    @mcp.tool()
    @api_tool
    async def merge_contacts(primary_contact_id: int, secondary_contact_ids: list[int],
                             contact: Optional[JSON] = None) -> Any:
        """Merge secondary contacts into a primary contact."""
        return await client.post("contacts/merge", compact(
            primary_contact_id=primary_contact_id,
            secondary_contact_ids=secondary_contact_ids, contact=contact))

    @mcp.tool()
    @api_tool
    async def make_contact_an_agent(contact_id: int, occasional: bool = False,
                                    role_ids: Optional[list[int]] = None) -> Any:
        """Convert a contact into an agent."""
        return await client.put(f"contacts/{contact_id}/make_agent",
                                compact(occasional=occasional, role_ids=role_ids))

    @mcp.tool()
    @api_tool
    async def send_contact_invite(contact_id: int) -> Any:
        """Send a portal activation invite to a contact."""
        return await client.put(f"contacts/{contact_id}/send_invite")

    @mcp.tool()
    @api_tool
    async def export_contacts(fields: JSON) -> Any:
        """Start a contact export job.

        Args:
            fields: e.g. {"default_fields": ["name","email"], "custom_fields": []}.
                Poll the returned id with get_export_job.
        """
        return await client.post("contacts/export", {"fields": fields})

    @mcp.tool()
    @api_tool
    async def list_contact_imports() -> Any:
        """List contact import jobs."""
        return await client.get("contacts/imports")

    @mcp.tool()
    @api_tool
    async def get_contact_import(import_id: int) -> Any:
        """Check the status of a contact import."""
        return await client.get(f"contacts/imports/{import_id}")

    @mcp.tool()
    @api_tool
    async def cancel_contact_import(import_id: int) -> Any:
        """Cancel a running contact import."""
        return await client.put(f"contacts/imports/{import_id}/cancel")
