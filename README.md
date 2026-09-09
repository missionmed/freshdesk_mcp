# Freshdesk MCP Server

An MCP server for the Freshdesk API with **complete endpoint coverage** and a
reporting layer that Freshdesk itself does not provide.

Forked from [effytech/freshdesk_mcp](https://github.com/effytech/freshdesk_mcp)
and substantially rewritten: 59 tools became **248**, every documented endpoint
is now implemented, and a coverage test keeps it that way.

## What changed from upstream

| | Upstream | This fork |
|---|---|---|
| Tools | 59 | 248 |
| Endpoint coverage | partial | all 220 documented endpoints |
| Rate limiting | none | honours `Retry-After`, retries 429 and 5xx |
| Pagination | manual `page`/`per_page` only | `fetch_all` on every list tool |
| Historical tickets | impossible (30-day cap) | `updated_since` on list_tickets |
| Reporting | none | 6 computed report tools |
| CSAT / time entries / SLA | none | full support |
| Automations | none | full CRUD |
| Structure | one 1277-line file | 16 focused modules over a shared client |

### Newly covered areas

Satisfaction (CSAT, new and legacy), time entries, SLA policies, business hours,
products, email configs and mailboxes, automatic Bcc, automation rules,
scenario automations, custom objects, collaboration threads, discussion forums,
ticket forms and field sections, skills, roles, exports and imports, archived
tickets, watchers, ticket merge and forward, bulk update/delete, outbound
messages, and knowledge-base translations.

## Reporting

Freshdesk has **no analytics or reports API** - the Analytics dashboard numbers
are not exposed anywhere. These tools reconstruct the same picture from raw
tickets (`include=stats`), satisfaction ratings and time entries:

- `ticket_volume_report` - counts by status, priority, source, group, agent, type or day
- `response_time_report` - first-response and resolution mean/median/p90/p95, plus SLA breach rates
- `agent_performance_report` - per-agent assigned/resolved and speed
- `csat_report` - rating distribution, positive %, per agent
- `time_tracking_report` - billable vs non-billable hours by agent
- `backlog_report` - live open tickets, age and overdue count

All period reports take `updated_since`, because **Freshdesk returns only the
last 30 days of tickets without it**.

## Configuration

| Variable | Required | Notes |
|---|---|---|
| `FRESHDESK_DOMAIN` | yes | `yourcompany.freshdesk.com`. A bare subdomain or full URL is also accepted. |
| `FRESHDESK_API_KEY` | yes | Freshdesk > profile menu > Profile Settings > Your API Key. |
| `TRANSPORT` | no | `http` (default) or `stdio`. |
| `PORT` / `HOST` | no | Defaults `8080` / `0.0.0.0`. |
| `LOG_LEVEL` | no | Default `INFO`. |

The API key inherits the permissions of the agent it belongs to, so an agent
without admin rights will get 403s on the admin tools.

## Running

Local, over stdio:

```bash
uv venv && . .venv/bin/activate && uv pip install -e .
TRANSPORT=stdio FRESHDESK_DOMAIN=... FRESHDESK_API_KEY=... freshdesk-mcp
```

Hosted (Railway or any container host) - the Dockerfile defaults to HTTP and
serves MCP at `/mcp`:

```bash
docker build -t freshdesk-mcp . && docker run -p 8080:8080 \
  -e FRESHDESK_DOMAIN=... -e FRESHDESK_API_KEY=... freshdesk-mcp
```

Claude Code / Claude Desktop, over stdio:

```json
{
  "mcpServers": {
    "freshdesk": {
      "command": "freshdesk-mcp",
      "env": {
        "FRESHDESK_DOMAIN": "yourcompany.freshdesk.com",
        "FRESHDESK_API_KEY": "your-key",
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

## Tests

```bash
python tests/test_units.py       # config parsing, error shaping, report maths
python tests/check_coverage.py   # every documented endpoint has a tool
```

`tests/freshdesk_endpoints.txt` is extracted from the curl examples in the
[official API docs](https://developers.freshdesk.com/api/). When Freshdesk ships
new endpoints, re-extract it and the coverage test will name what is missing.

## Notes and gotchas

- **The 30-day default.** `GET /tickets` returns only the last 30 days unless
  `updated_since` is set. Every reporting tool requires it for this reason.
- **`include=stats`** is what carries `first_responded_at` and `resolved_at`.
  Without it there is nothing to compute response times from.
- **Search is capped** at 10 pages / 300 results. For bulk reads use
  `list_tickets(fetch_all=True)`, which pages properly.
- **Deep pagination stops at 300 pages** (30,000 tickets) on Freshdesk's side.
  Reports report `truncated: true` when they hit their cap.
- **Numeric enums**: call `describe_ticket_enums()` rather than guessing what
  `status: 3` means.
- **Automation rules** are fiddly; call `describe_automation_rule_schema()`
  before `create_automation_rule`.
