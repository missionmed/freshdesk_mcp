"""Tickets: CRUD, search/filter, bulk actions, watchers, merge, archive, access."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact

#: Freshdesk encodes these as integers; spelled out so callers need not guess.
STATUS = {2: "Open", 3: "Pending", 4: "Resolved", 5: "Closed"}
PRIORITY = {1: "Low", 2: "Medium", 3: "High", 4: "Urgent"}
SOURCE = {
    1: "Email", 2: "Portal", 3: "Phone", 7: "Chat", 9: "Feedback Widget",
    10: "Outbound Email",
}


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def list_tickets(
        updated_since: Optional[str] = None,
        filter: Optional[str] = None,
        include: Optional[str] = None,
        order_by: Optional[str] = None,
        order_type: Optional[str] = None,
        requester_id: Optional[int] = None,
        email: Optional[str] = None,
        company_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 30,
        fetch_all: bool = False,
        max_items: Optional[int] = None,
    ) -> Any:
        """List tickets.

        IMPORTANT: Freshdesk only returns tickets created in the last 30 days
        unless you pass `updated_since`. For anything historical you must set it.

        Args:
            updated_since: ISO-8601 date/time, e.g. "2026-01-01" or
                "2026-01-01T00:00:00Z". Required to see beyond the last 30 days.
            filter: One of "new_and_my_open", "watching", "spam", "deleted".
            include: Comma-separated extras: "stats", "requester", "description",
                "company". Use "stats" to get first_responded_at / resolved_at,
                which response-time and resolution reporting depend on.
            order_by: "created_at", "due_by", "updated_at" or "status".
            order_type: "asc" or "desc" (default desc).
            requester_id: Only tickets from this requester.
            email: Only tickets from this requester email.
            company_id: Only tickets for this company.
            page: Page number when fetch_all is False.
            per_page: 1-100 (default 30).
            fetch_all: Page through everything (capped at 300 pages by Freshdesk).
            max_items: Stop after this many when fetch_all is True.
        """
        params = compact(
            updated_since=updated_since, filter=filter, include=include,
            order_by=order_by, order_type=order_type, requester_id=requester_id,
            email=email, company_id=company_id,
        )
        if fetch_all:
            rows = await client.paginate(
                "tickets", params=params, max_items=max_items, per_page=min(per_page, 100)
            )
            return {"tickets": rows, "count": len(rows)}
        return await client.get("tickets", page=page, per_page=per_page, **params)

    @mcp.tool()
    @api_tool
    async def get_ticket(ticket_id: int, include: Optional[str] = None) -> Any:
        """Retrieve a single ticket.

        Args:
            ticket_id: Ticket id.
            include: Extras such as "conversations", "requester", "company",
                "stats", "sla_policy".
        """
        return await client.get(f"tickets/{ticket_id}", **compact(include=include))

    @mcp.tool()
    @api_tool
    async def create_ticket(
        subject: str,
        description: str,
        status: int = 2,
        priority: int = 1,
        email: Optional[str] = None,
        requester_id: Optional[int] = None,
        phone: Optional[str] = None,
        name: Optional[str] = None,
        source: int = 2,
        group_id: Optional[int] = None,
        responder_id: Optional[int] = None,
        company_id: Optional[int] = None,
        product_id: Optional[int] = None,
        email_config_id: Optional[int] = None,
        type: Optional[str] = None,
        tags: Optional[list[str]] = None,
        cc_emails: Optional[list[str]] = None,
        due_by: Optional[str] = None,
        fr_due_by: Optional[str] = None,
        parent_id: Optional[int] = None,
        custom_fields: Optional[JSON] = None,
        additional_fields: Optional[JSON] = None,
    ) -> Any:
        """Create a ticket. One of email, requester_id or phone is required.

        Args:
            status: 2 Open, 3 Pending, 4 Resolved, 5 Closed.
            priority: 1 Low, 2 Medium, 3 High, 4 Urgent.
            source: 1 Email, 2 Portal, 3 Phone, 7 Chat, 9 Feedback Widget,
                10 Outbound Email.
            name: Requester name, required when creating via an unknown phone.
            due_by / fr_due_by: ISO-8601 timestamps.
            additional_fields: Any other documented top-level field.
        """
        body = compact(
            subject=subject, description=description, status=status, priority=priority,
            email=email, requester_id=requester_id, phone=phone, name=name,
            source=source, group_id=group_id, responder_id=responder_id,
            company_id=company_id, product_id=product_id,
            email_config_id=email_config_id, type=type, tags=tags,
            cc_emails=cc_emails, due_by=due_by, fr_due_by=fr_due_by,
            parent_id=parent_id, custom_fields=custom_fields,
        )
        body.update(additional_fields or {})
        return await client.post("tickets", body)

    @mcp.tool()
    @api_tool
    async def update_ticket(ticket_id: int, fields: JSON) -> Any:
        """Update a ticket.

        Args:
            ticket_id: Ticket id.
            fields: Fields to change, e.g. {"status": 4, "priority": 3,
                "tags": ["billing"], "custom_fields": {"cf_x": "y"}}.
        """
        return await client.put(f"tickets/{ticket_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_ticket(ticket_id: int) -> Any:
        """Move a ticket to trash (recoverable with restore_ticket)."""
        return await client.delete(f"tickets/{ticket_id}")

    @mcp.tool()
    @api_tool
    async def restore_ticket(ticket_id: int) -> Any:
        """Restore a previously deleted ticket."""
        return await client.put(f"tickets/{ticket_id}/restore")

    @mcp.tool()
    @api_tool
    async def search_tickets(query: str, page: int = 1) -> Any:
        """Search tickets with Freshdesk's query language.

        Capped by Freshdesk at 10 pages / 300 results. For large pulls use
        list_tickets(updated_since=..., fetch_all=True) instead.

        Args:
            query: Lucene-ish filter WITHOUT the surrounding quotes, e.g.
                status:2 AND priority:4
                created_at:>'2026-01-01' AND group_id:123
            page: 1-10.
        """
        return await client.get("search/tickets", query=f'"{query}"', page=page)

    @mcp.tool()
    @api_tool
    async def filter_tickets(query: str, page: int = 1) -> Any:
        """Alias of search_tickets, matching the docs' "Filter Tickets" section."""
        return await client.get("search/tickets", query=f'"{query}"', page=page)

    @mcp.tool()
    @api_tool
    async def bulk_update_tickets(ticket_ids: list[int], properties: JSON) -> Any:
        """Update many tickets in one call (async job).

        Args:
            ticket_ids: Tickets to change.
            properties: e.g. {"status": 4, "responder_id": 1}.
        """
        return await client.post(
            "tickets/bulk_update", {"bulk_action": {"ids": ticket_ids, "properties": properties}}
        )

    @mcp.tool()
    @api_tool
    async def bulk_delete_tickets(ticket_ids: list[int]) -> Any:
        """Delete many tickets in one call (async job)."""
        return await client.post("tickets/bulk_delete", {"bulk_action": {"ids": ticket_ids}})

    @mcp.tool()
    @api_tool
    async def merge_tickets(
        primary_id: int, ticket_ids: list[int], note_in_primary: Optional[str] = None,
        note_in_secondary: Optional[str] = None, convert_recepients_to_cc: bool = False,
    ) -> Any:
        """Merge secondary tickets into a primary ticket."""
        body = {
            "primary_id": primary_id,
            "ticket_ids": ticket_ids,
            "convert_recepients_to_cc": convert_recepients_to_cc,
        }
        if note_in_primary:
            body["note_in_primary"] = {"body": note_in_primary}
        if note_in_secondary:
            body["note_in_secondary"] = {"body": note_in_secondary}
        return await client.put("tickets/merge", body)

    @mcp.tool()
    @api_tool
    async def forward_ticket(
        ticket_id: int, to_emails: list[str], body: str,
        cc_emails: Optional[list[str]] = None, bcc_emails: Optional[list[str]] = None,
        from_email: Optional[str] = None,
    ) -> Any:
        """Forward a ticket by email."""
        return await client.post(
            f"tickets/{ticket_id}/forward",
            compact(to_emails=to_emails, body=body, cc_emails=cc_emails,
                    bcc_emails=bcc_emails, from_email=from_email),
        )

    @mcp.tool()
    @api_tool
    async def create_outbound_email(
        subject: str, description: str, email: str, status: int = 5,
        priority: int = 1, email_config_id: Optional[int] = None,
        group_id: Optional[int] = None, responder_id: Optional[int] = None,
        tags: Optional[list[str]] = None, custom_fields: Optional[JSON] = None,
    ) -> Any:
        """Start a new outbound email thread (creates a ticket with source 10)."""
        return await client.post(
            "tickets/outbound_email",
            compact(subject=subject, description=description, email=email,
                    status=status, priority=priority, email_config_id=email_config_id,
                    group_id=group_id, responder_id=responder_id, tags=tags,
                    custom_fields=custom_fields),
        )

    # --- watchers -------------------------------------------------------
    @mcp.tool()
    @api_tool
    async def list_ticket_watchers(ticket_id: int) -> Any:
        """List agents watching a ticket."""
        return await client.get(f"tickets/{ticket_id}/watchers")

    @mcp.tool()
    @api_tool
    async def add_ticket_watcher(ticket_id: int, user_ids: list[int]) -> Any:
        """Add watchers to a ticket."""
        return await client.post(f"tickets/{ticket_id}/watch", {"user_ids": user_ids})

    @mcp.tool()
    @api_tool
    async def remove_ticket_watcher(ticket_id: int) -> Any:
        """Stop the authenticated agent watching a ticket."""
        return await client.put(f"tickets/{ticket_id}/unwatch")

    @mcp.tool()
    @api_tool
    async def bulk_watch_tickets(ticket_ids: list[int], user_ids: list[int]) -> Any:
        """Add watchers across many tickets."""
        return await client.put("tickets/bulk_watch", {"ids": ticket_ids, "user_ids": user_ids})

    @mcp.tool()
    @api_tool
    async def bulk_unwatch_tickets(ticket_ids: list[int]) -> Any:
        """Remove the authenticated agent as watcher across many tickets."""
        return await client.put("tickets/bulk_unwatch", {"ids": ticket_ids})

    # --- associations, archive, access ----------------------------------
    @mcp.tool()
    @api_tool
    async def get_associated_tickets(ticket_id: int) -> Any:
        """List tickets associated with a tracker/parent ticket."""
        return await client.get(f"tickets/{ticket_id}/associated_tickets")

    @mcp.tool()
    @api_tool
    async def get_prime_association(ticket_id: int) -> Any:
        """Get the prime (tracker/parent) association of a ticket."""
        return await client.get(f"tickets/{ticket_id}/prime_association")

    @mcp.tool()
    @api_tool
    async def get_archived_ticket(ticket_id: int) -> Any:
        """View an archived ticket."""
        return await client.get(f"tickets/archived/{ticket_id}")

    @mcp.tool()
    @api_tool
    async def delete_archived_ticket(ticket_id: int) -> Any:
        """Delete an archived ticket."""
        return await client.delete(f"tickets/archived/{ticket_id}")

    @mcp.tool()
    @api_tool
    async def list_archived_ticket_conversations(ticket_id: int, page: int = 1, per_page: int = 30) -> Any:
        """List conversations on an archived ticket."""
        return await client.get(
            f"tickets/archived/{ticket_id}/conversations", page=page, per_page=per_page
        )

    @mcp.tool()
    @api_tool
    async def get_ticket_access(ticket_id: int) -> Any:
        """Show which users have explicit access to a ticket."""
        return await client.get(f"tickets/{ticket_id}/accesses")

    @mcp.tool()
    @api_tool
    async def add_ticket_access(ticket_id: int, user_ids: list[int]) -> Any:
        """Grant users access to a ticket."""
        return await client.post(f"tickets/{ticket_id}/accesses", {"user_ids": user_ids})

    @mcp.tool()
    @api_tool
    async def remove_ticket_access(ticket_id: int, user_ids: list[int]) -> Any:
        """Revoke users' access to a ticket."""
        return await client.request(
            "DELETE", f"tickets/{ticket_id}/accesses", json={"user_ids": user_ids}
        )

    @mcp.tool()
    @api_tool
    async def delete_ticket_attachment(attachment_id: int) -> Any:
        """Delete an attachment from a ticket."""
        return await client.delete(f"attachments/{attachment_id}")

    # --- summary --------------------------------------------------------
    @mcp.tool()
    @api_tool
    async def get_ticket_summary(ticket_id: int) -> Any:
        """View a ticket's summary field."""
        return await client.get(f"tickets/{ticket_id}/summary")

    @mcp.tool()
    @api_tool
    async def update_ticket_summary(ticket_id: int, body: str) -> Any:
        """Create or update a ticket's summary."""
        return await client.put(f"tickets/{ticket_id}/summary", {"body": body})

    @mcp.tool()
    @api_tool
    async def delete_ticket_summary(ticket_id: int) -> Any:
        """Delete a ticket's summary."""
        return await client.delete(f"tickets/{ticket_id}/summary")

    @mcp.tool()
    @api_tool
    async def list_ticket_time_entries(ticket_id: int) -> Any:
        """List time entries logged against a ticket."""
        return await client.get(f"tickets/{ticket_id}/time_entries")

    @mcp.tool()
    @api_tool
    async def describe_ticket_enums() -> JSON:
        """Explain Freshdesk's numeric status / priority / source codes."""
        return {"status": STATUS, "priority": PRIORITY, "source": SOURCE}
