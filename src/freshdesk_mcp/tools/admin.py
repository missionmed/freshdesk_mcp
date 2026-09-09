"""Account-level configuration: SLAs, business hours, products, email, automations."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact


def register(mcp) -> None:
    # --- account & jobs -------------------------------------------------
    @mcp.tool()
    @api_tool
    async def get_account() -> Any:
        """View the Freshdesk account (plan, limits, primary language)."""
        return await client.get("account")

    @mcp.tool()
    @api_tool
    async def export_account() -> Any:
        """Start a full account export job."""
        return await client.get("account/export")

    @mcp.tool()
    @api_tool
    async def get_export_job(job_id: str) -> Any:
        """Check an async job (exports, bulk updates, bulk agent creation).

        Bulk and export endpoints return a job id; poll it here for status and
        the download URL when it finishes.
        """
        return await client.get(f"jobs/{job_id}")

    @mcp.tool()
    @api_tool
    async def get_helpdesk_settings() -> Any:
        """View helpdesk settings (portal name, primary language, timezone)."""
        return await client.get("settings/helpdesk")

    # --- SLA ------------------------------------------------------------
    @mcp.tool()
    @api_tool
    async def list_sla_policies() -> Any:
        """List SLA policies and their target response/resolution times."""
        return await client.get("sla_policies")

    @mcp.tool()
    @api_tool
    async def create_sla_policy(payload: JSON) -> Any:
        """Create an SLA policy."""
        return await client.post("sla_policies", payload)

    @mcp.tool()
    @api_tool
    async def update_sla_policy(policy_id: int, fields: JSON) -> Any:
        """Update an SLA policy."""
        return await client.put(f"sla_policies/{policy_id}", fields)

    # --- business hours, products, email --------------------------------
    @mcp.tool()
    @api_tool
    async def list_business_hours() -> Any:
        """List business hour configurations."""
        return await client.get("business_hours")

    @mcp.tool()
    @api_tool
    async def get_business_hour(bh_id: int) -> Any:
        """Retrieve one business hours configuration."""
        return await client.get(f"business_hours/{bh_id}")

    @mcp.tool()
    @api_tool
    async def list_products() -> Any:
        """List products."""
        return await client.get("products")

    @mcp.tool()
    @api_tool
    async def get_product(product_id: int) -> Any:
        """Retrieve a product."""
        return await client.get(f"products/{product_id}")

    @mcp.tool()
    @api_tool
    async def list_email_configs() -> Any:
        """List email configurations (support addresses)."""
        return await client.get("email_configs")

    @mcp.tool()
    @api_tool
    async def get_email_config(config_id: int) -> Any:
        """Retrieve an email configuration."""
        return await client.get(f"email_configs/{config_id}")

    @mcp.tool()
    @api_tool
    async def list_email_mailboxes() -> Any:
        """List email mailboxes."""
        return await client.get("email/mailboxes")

    @mcp.tool()
    @api_tool
    async def get_email_mailbox(mailbox_id: int) -> Any:
        """Retrieve an email mailbox."""
        return await client.get(f"email/mailboxes/{mailbox_id}")

    @mcp.tool()
    @api_tool
    async def create_email_mailbox(payload: JSON) -> Any:
        """Create an email mailbox."""
        return await client.post("email/mailboxes", payload)

    @mcp.tool()
    @api_tool
    async def update_email_mailbox(mailbox_id: int, fields: JSON) -> Any:
        """Update an email mailbox.

        WARNING: this endpoint replaces the whole mailbox, and its validator
        only accepts `plain`, `login` or `cram_md5` for
        incoming/outgoing.authentication. A mailbox connected over OAuth
        (`xoauth2`, e.g. Gmail) therefore CANNOT be round-tripped through here -
        sending its own config back is rejected, and forcing it through would
        drop the OAuth connection. Change OAuth mailboxes in the Freshdesk UI
        (Admin > Email > the mailbox), including the display name.

        Args:
            mailbox_id: Mailbox id, from list_email_mailboxes.
            fields: Full mailbox payload to write.
        """
        return await client.put(f"email/mailboxes/{mailbox_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_email_mailbox(mailbox_id: int) -> Any:
        """Delete an email mailbox."""
        return await client.delete(f"email/mailboxes/{mailbox_id}")

    @mcp.tool()
    @api_tool
    async def update_mailbox_settings(fields: JSON) -> Any:
        """Update global mailbox settings."""
        return await client.put("email/settings", fields)

    @mcp.tool()
    @api_tool
    async def get_automatic_bcc() -> Any:
        """View the automatic Bcc address for outgoing email."""
        return await client.get("notifications/email/bcc")

    @mcp.tool()
    @api_tool
    async def update_automatic_bcc(email: str) -> Any:
        """Set the automatic Bcc address for outgoing email."""
        return await client.put("notifications/email/bcc", {"bcc_email": email})

    # --- outbound messages ----------------------------------------------
    @mcp.tool()
    @api_tool
    async def send_proactive_message(payload: JSON) -> Any:
        """Send a proactive outbound message on a messaging channel.

        Args:
            payload: Channel-specific message body as documented under
                Outbound Messages.
        """
        return await client.post("channels/outbound-messages", payload)

    @mcp.tool()
    @api_tool
    async def get_outbound_message(message_id: str) -> Any:
        """Retrieve a previously sent outbound message by its id."""
        return await client.get(f"channels/outbound-messages/{message_id}")

    # --- automations ----------------------------------------------------
    @mcp.tool()
    @api_tool
    async def list_scenario_automations() -> Any:
        """List scenario automations (one-click agent macros)."""
        return await client.get("scenario_automations")

    @mcp.tool()
    @api_tool
    async def list_automation_rules(automation_type_id: int) -> Any:
        """List automation rules of a type.

        Args:
            automation_type_id: 1 ticket creation, 3 time triggers,
                4 ticket updates.
        """
        return await client.get(f"automations/{automation_type_id}/rules")

    @mcp.tool()
    @api_tool
    async def describe_automation_rule_schema() -> JSON:
        """The payload shape create_automation_rule expects, with an example.

        Call this first when building a rule; the operators and field names are
        not guessable and a malformed rule is rejected without much explanation.
        """
        return {
            "automation_type_id": {
                1: "Ticket creation (runs when a ticket is created)",
                3: "Time triggers (runs on a schedule after an event)",
                4: "Ticket updates (runs when a ticket changes)",
            },
            "structure": {
                "name": "string",
                "position": "int - order the rule runs in",
                "active": "bool",
                "performer": {
                    "type": "1 agent, 2 requester, 3 agent or requester, 4 system",
                    "members": "list of agent ids, when type is 1",
                },
                "events": "[{field_name, from, to}] - only for automation_type_id 4",
                "conditions": [
                    {
                        "name": "condition_set_1",
                        "match_type": "all | any",
                        "properties": [
                            {
                                "resource_type": "ticket | contact | company",
                                "field_name": "status | priority | group_id | ...",
                                "operator": "is | is_not | contains | greater_than | ...",
                                "value": "string or list",
                            }
                        ],
                    }
                ],
                "actions": "[{field_name, value}] - what the rule does",
            },
            "example": {
                "name": "Escalate urgent billing tickets",
                "position": 1,
                "active": True,
                "performer": {"type": 4},
                "conditions": [
                    {
                        "name": "condition_set_1",
                        "match_type": "all",
                        "properties": [
                            {"resource_type": "ticket", "field_name": "priority",
                             "operator": "is", "value": "4"}
                        ],
                    }
                ],
                "actions": [{"field_name": "group_id", "value": "123"}],
            },
        }

    @mcp.tool()
    @api_tool
    async def get_automation_rule(automation_type_id: int, rule_id: int) -> Any:
        """Retrieve one automation rule."""
        return await client.get(f"automations/{automation_type_id}/rules/{rule_id}")

    @mcp.tool()
    @api_tool
    async def create_automation_rule(
        automation_type_id: int,
        name: str,
        conditions: list[JSON],
        actions: list[JSON],
        performer: Optional[JSON] = None,
        events: Optional[list[JSON]] = None,
        position: Optional[int] = None,
        active: bool = True,
    ) -> Any:
        """Create an automation rule.

        Call describe_automation_rule_schema() first for the exact field shapes
        and a worked example.

        Args:
            automation_type_id: 1 ticket creation, 3 time triggers, 4 ticket updates.
            name: Rule name.
            conditions: [{name, match_type, properties: [{resource_type,
                field_name, operator, value}]}].
            actions: [{field_name, value}] - what the rule does when it matches.
            performer: {type, members} - who triggers it. Required for type 4.
            events: [{field_name, from, to}] - required for type 4 (ticket updates).
            position: Order the rule runs in.
            active: Whether the rule is enabled.
        """
        return await client.post(
            f"automations/{automation_type_id}/rules",
            compact(name=name, conditions=conditions, actions=actions,
                    performer=performer, events=events, position=position,
                    active=active),
        )

    @mcp.tool()
    @api_tool
    async def update_automation_rule(automation_type_id: int, rule_id: int,
                                     fields: JSON) -> Any:
        """Update an automation rule."""
        return await client.put(f"automations/{automation_type_id}/rules/{rule_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_automation_rule(automation_type_id: int, rule_id: int) -> Any:
        """Delete an automation rule."""
        return await client.delete(f"automations/{automation_type_id}/rules/{rule_id}")
