"""Ticket/contact/company field definitions, field sections and ticket forms."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact


def register(mcp) -> None:
    # --- ticket fields --------------------------------------------------
    @mcp.tool()
    @api_tool
    async def list_ticket_fields(type: Optional[str] = None,
                                 include: Optional[str] = None) -> Any:
        """List ticket fields, including custom ones and their allowed choices."""
        return await client.get("ticket_fields", **compact(type=type, include=include))

    @mcp.tool()
    @api_tool
    async def list_ticket_fields_admin(include: Optional[str] = None) -> Any:
        """List ticket fields via the admin endpoint.

        Unlike list_ticket_fields this can expand dynamic sections with
        include="section".
        """
        return await client.get("admin/ticket_fields", **compact(include=include))

    @mcp.tool()
    @api_tool
    async def get_ticket_field(field_id: int, include: Optional[str] = None) -> Any:
        """Retrieve one ticket field. Use include="section" for dynamic sections."""
        return await client.get(f"admin/ticket_fields/{field_id}", **compact(include=include))

    @mcp.tool()
    @api_tool
    async def create_ticket_field(label: str, type: str, **kwargs: Any) -> Any:
        """Create a ticket field.

        Args:
            type: e.g. "custom_text", "custom_dropdown", "custom_checkbox",
                "custom_date", "custom_number", "custom_paragraph".
        """
        return await client.post("admin/ticket_fields", {"label": label, "type": type, **kwargs})

    @mcp.tool()
    @api_tool
    async def update_ticket_field(field_id: int, fields: JSON) -> Any:
        """Update a ticket field."""
        return await client.put(f"admin/ticket_fields/{field_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_ticket_field(field_id: int) -> Any:
        """Delete a ticket field."""
        return await client.delete(f"admin/ticket_fields/{field_id}")

    # --- field sections (dynamic sections) ------------------------------
    @mcp.tool()
    @api_tool
    async def list_field_sections(field_id: int) -> Any:
        """List the dynamic sections attached to a ticket field."""
        return await client.get(f"admin/ticket_fields/{field_id}/sections")

    @mcp.tool()
    @api_tool
    async def get_field_section(field_id: int, section_id: int) -> Any:
        """Retrieve one section of a ticket field."""
        return await client.get(f"admin/ticket_fields/{field_id}/sections/{section_id}")

    @mcp.tool()
    @api_tool
    async def create_field_section(field_id: int, payload: JSON) -> Any:
        """Create a dynamic section on a ticket field."""
        return await client.post(f"admin/ticket_fields/{field_id}/sections", payload)

    @mcp.tool()
    @api_tool
    async def update_field_section(field_id: int, section_id: int, fields: JSON) -> Any:
        """Update a ticket field section."""
        return await client.put(f"admin/ticket_fields/{field_id}/sections/{section_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_field_section(field_id: int, section_id: int) -> Any:
        """Delete a ticket field section."""
        return await client.delete(f"admin/ticket_fields/{field_id}/sections/{section_id}")

    # --- ticket forms ---------------------------------------------------
    @mcp.tool()
    @api_tool
    async def list_ticket_forms() -> Any:
        """List ticket forms."""
        return await client.get("ticket-forms")

    @mcp.tool()
    @api_tool
    async def get_ticket_form(form_id: int) -> Any:
        """Retrieve a ticket form."""
        return await client.get(f"ticket-forms/{form_id}")

    @mcp.tool()
    @api_tool
    async def create_ticket_form(payload: JSON) -> Any:
        """Create a ticket form."""
        return await client.post("ticket-forms", payload)

    @mcp.tool()
    @api_tool
    async def update_ticket_form(form_id: int, fields: JSON) -> Any:
        """Update a ticket form."""
        return await client.put(f"ticket-forms/{form_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_ticket_form(form_id: int) -> Any:
        """Delete a ticket form."""
        return await client.delete(f"ticket-forms/{form_id}")

    @mcp.tool()
    @api_tool
    async def clone_ticket_form(form_id: int) -> Any:
        """Clone a ticket form."""
        return await client.get(f"ticket-forms/{form_id}/clone")

    @mcp.tool()
    @api_tool
    async def get_ticket_form_field(form_id: int, field_id: int) -> Any:
        """Retrieve one field on a ticket form."""
        return await client.get(f"ticket-forms/{form_id}/fields/{field_id}")

    @mcp.tool()
    @api_tool
    async def update_ticket_form_field(form_id: int, field_id: int, fields: JSON) -> Any:
        """Update one field on a ticket form."""
        return await client.put(f"ticket-forms/{form_id}/fields/{field_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_ticket_form_field(form_id: int, field_id: int) -> Any:
        """Remove a field from a ticket form."""
        return await client.delete(f"ticket-forms/{form_id}/fields/{field_id}")

    # --- contact & company fields ---------------------------------------
    @mcp.tool()
    @api_tool
    async def list_contact_fields() -> Any:
        """List contact fields."""
        return await client.get("contact_fields")

    @mcp.tool()
    @api_tool
    async def get_contact_field(field_id: int) -> Any:
        """Retrieve a contact field."""
        return await client.get(f"contact_fields/{field_id}")

    @mcp.tool()
    @api_tool
    async def create_contact_field(label: str, type: str, **kwargs: Any) -> Any:
        """Create a contact field."""
        return await client.post("contact_fields", {"label": label, "type": type, **kwargs})

    @mcp.tool()
    @api_tool
    async def update_contact_field(field_id: int, fields: JSON) -> Any:
        """Update a contact field."""
        return await client.put(f"contact_fields/{field_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_contact_field(field_id: int) -> Any:
        """Delete a contact field."""
        return await client.delete(f"contact_fields/{field_id}")

    @mcp.tool()
    @api_tool
    async def list_company_fields() -> Any:
        """List company fields."""
        return await client.get("company_fields")

    @mcp.tool()
    @api_tool
    async def get_company_field(field_id: int) -> Any:
        """Retrieve a company field."""
        return await client.get(f"company_fields/{field_id}")

    @mcp.tool()
    @api_tool
    async def create_company_field(label: str, type: str, **kwargs: Any) -> Any:
        """Create a company field."""
        return await client.post("company_fields", {"label": label, "type": type, **kwargs})

    @mcp.tool()
    @api_tool
    async def update_company_field(field_id: int, fields: JSON) -> Any:
        """Update a company field."""
        return await client.put(f"company_fields/{field_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_company_field(field_id: int) -> Any:
        """Delete a company field."""
        return await client.delete(f"company_fields/{field_id}")
