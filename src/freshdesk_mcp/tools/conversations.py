"""Conversations: replies (outbound email), notes, forwards."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import api_tool, compact


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def list_ticket_conversations(
        ticket_id: int, page: int = 1, per_page: int = 30, fetch_all: bool = False
    ) -> Any:
        """List all conversations (replies and notes) on a ticket."""
        if fetch_all:
            rows = await client.paginate(f"tickets/{ticket_id}/conversations")
            return {"conversations": rows, "count": len(rows)}
        return await client.get(
            f"tickets/{ticket_id}/conversations", page=page, per_page=per_page
        )

    @mcp.tool()
    @api_tool
    async def reply_to_ticket(
        ticket_id: int,
        body: str,
        cc_emails: Optional[list[str]] = None,
        bcc_emails: Optional[list[str]] = None,
        from_email: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Any:
        """Reply to a ticket. This sends a real email to the requester.

        Args:
            ticket_id: Ticket to reply on.
            body: Reply content in HTML. Plain newlines are not preserved by
                email clients, so use <p> or <br> for line breaks.
            cc_emails: Extra Cc addresses (the requester is always the To).
            bcc_emails: Extra Bcc addresses.
            from_email: Sending address; defaults to the ticket's email config.
            user_id: Agent the reply is attributed to.
        """
        return await client.post(
            f"tickets/{ticket_id}/reply",
            compact(body=body, cc_emails=cc_emails, bcc_emails=bcc_emails,
                    from_email=from_email, user_id=user_id),
        )

    @mcp.tool()
    @api_tool
    async def add_ticket_note(
        ticket_id: int,
        body: str,
        private: bool = True,
        incoming: Optional[bool] = None,
        user_id: Optional[int] = None,
        notify_emails: Optional[list[str]] = None,
    ) -> Any:
        """Add a note to a ticket.

        Args:
            body: Note content in HTML.
            private: True (default) keeps it internal; False makes it public to
                the requester.
            notify_emails: Addresses to notify about the note.
        """
        return await client.post(
            f"tickets/{ticket_id}/notes",
            compact(body=body, private=private, incoming=incoming,
                    user_id=user_id, notify_emails=notify_emails),
        )

    @mcp.tool()
    @api_tool
    async def update_conversation(conversation_id: int, body: str) -> Any:
        """Edit the body of an existing note (replies cannot be edited)."""
        return await client.put(f"conversations/{conversation_id}", {"body": body})

    @mcp.tool()
    @api_tool
    async def delete_conversation(conversation_id: int) -> Any:
        """Delete a conversation entry."""
        return await client.delete(f"conversations/{conversation_id}")

    @mcp.tool()
    @api_tool
    async def reply_to_forward(
        ticket_id: int, body: str, to_emails: list[str],
        cc_emails: Optional[list[str]] = None, bcc_emails: Optional[list[str]] = None,
        from_email: Optional[str] = None,
    ) -> Any:
        """Reply to a forwarded thread on a ticket."""
        return await client.post(
            f"tickets/{ticket_id}/reply_to_forward",
            compact(body=body, to_emails=to_emails, cc_emails=cc_emails,
                    bcc_emails=bcc_emails, from_email=from_email),
        )
