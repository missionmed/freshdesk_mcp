"""Computed reporting.

Freshdesk has no analytics/reports API: the Analytics dashboard numbers are not
exposed anywhere. What it does expose is the raw material -- tickets (with a
`stats` block carrying first_responded_at / resolved_at), satisfaction ratings
and time entries -- so these tools pull that and aggregate it locally.

Every tool here needs `updated_since`, because Freshdesk otherwise returns only
the last 30 days of tickets.
"""
from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable, Optional

from .. import client
from ._util import JSON, api_tool
from .tickets import PRIORITY, SOURCE, STATUS


def _parse(ts: Any) -> Optional[datetime]:
    if not ts or not isinstance(ts, str):
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _hours(start: Any, end: Any) -> Optional[float]:
    a, b = _parse(start), _parse(end)
    if not a or not b:
        return None
    delta = (b - a).total_seconds() / 3600
    return round(delta, 3) if delta >= 0 else None


def _summarise(values: list[float]) -> JSON:
    """Mean/median/p90 for a set of durations. Percentiles beat averages here:
    a handful of week-old stragglers drag the mean somewhere unrepresentative."""
    if not values:
        return {"count": 0}
    ordered = sorted(values)
    def pct(p: float) -> float:
        if len(ordered) == 1:
            return round(ordered[0], 2)
        idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * p))))
        return round(ordered[idx], 2)
    return {
        "count": len(ordered),
        "mean_hours": round(statistics.fmean(ordered), 2),
        "median_hours": round(statistics.median(ordered), 2),
        "p90_hours": pct(0.90),
        "p95_hours": pct(0.95),
        "min_hours": round(ordered[0], 2),
        "max_hours": round(ordered[-1], 2),
    }


def _label(mapping: dict[int, str], key: Any) -> str:
    return mapping.get(key, str(key))


async def _fetch_tickets(updated_since: str, max_items: Optional[int],
                         extra: Optional[JSON] = None) -> list[JSON]:
    params = {"updated_since": updated_since, "include": "stats", **(extra or {})}
    return await client.paginate("tickets", params=params, max_items=max_items, per_page=100)


async def _name_maps() -> tuple[dict[int, str], dict[int, str]]:
    """Resolve group and agent ids to names so reports read like reports."""
    agents: dict[int, str] = {}
    groups: dict[int, str] = {}
    try:
        for a in await client.paginate("agents"):
            contact = a.get("contact") or {}
            agents[a.get("id")] = contact.get("name") or contact.get("email") or str(a.get("id"))
    except Exception:  # noqa: BLE001 - names are a nicety, not the report
        pass
    try:
        for g in await client.paginate("groups"):
            groups[g.get("id")] = g.get("name") or str(g.get("id"))
    except Exception:  # noqa: BLE001
        pass
    return agents, groups


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def ticket_volume_report(
        updated_since: str,
        max_tickets: int = 5000,
        group_by: str = "status",
    ) -> Any:
        """Count tickets over a period, broken down by a dimension.

        Args:
            updated_since: ISO-8601 start, e.g. "2026-08-01". Required -- without
                it Freshdesk only returns the last 30 days.
            max_tickets: Safety cap on how many tickets to pull.
            group_by: "status", "priority", "source", "group", "agent", "type",
                "company" or "day".
        """
        tickets = await _fetch_tickets(updated_since, max_tickets)
        agents, groups = await _name_maps() if group_by in {"agent", "group"} else ({}, {})

        counts: Counter = Counter()
        for t in tickets:
            if group_by == "status":
                key = _label(STATUS, t.get("status"))
            elif group_by == "priority":
                key = _label(PRIORITY, t.get("priority"))
            elif group_by == "source":
                key = _label(SOURCE, t.get("source"))
            elif group_by == "group":
                key = groups.get(t.get("group_id"), "Unassigned")
            elif group_by == "agent":
                key = agents.get(t.get("responder_id"), "Unassigned")
            elif group_by == "type":
                key = t.get("type") or "None"
            elif group_by == "company":
                key = str(t.get("company_id") or "None")
            elif group_by == "day":
                created = _parse(t.get("created_at"))
                key = created.date().isoformat() if created else "unknown"
            else:
                return {"error": f"Unsupported group_by: {group_by}"}
            counts[key] += 1

        return {
            "period_start": updated_since,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_tickets": len(tickets),
            "group_by": group_by,
            "breakdown": dict(counts.most_common()),
            "truncated": len(tickets) >= max_tickets,
        }

    @mcp.tool()
    @api_tool
    async def response_time_report(
        updated_since: str,
        max_tickets: int = 5000,
        group_by: Optional[str] = None,
    ) -> Any:
        """First-response and resolution times, plus SLA breach rates.

        Reconstructs what the Analytics dashboard shows, from ticket `stats`.

        Args:
            updated_since: ISO-8601 start of the period. Required.
            max_tickets: Safety cap on tickets pulled.
            group_by: Optionally also break the same metrics down by "group",
                "agent" or "priority".
        """
        tickets = await _fetch_tickets(updated_since, max_tickets)
        agents, groups = await _name_maps() if group_by in {"agent", "group"} else ({}, {})

        first: list[float] = []
        resolve: list[float] = []
        fr_breach = res_breach = fr_target = res_target = 0
        buckets: dict[str, dict[str, list[float]]] = defaultdict(
            lambda: {"first_response": [], "resolution": []}
        )

        for t in tickets:
            stats = t.get("stats") or {}
            created = t.get("created_at")
            fr = _hours(created, stats.get("first_responded_at"))
            rs = _hours(created, stats.get("resolved_at"))

            if group_by == "group":
                key = groups.get(t.get("group_id"), "Unassigned")
            elif group_by == "agent":
                key = agents.get(t.get("responder_id"), "Unassigned")
            elif group_by == "priority":
                key = _label(PRIORITY, t.get("priority"))
            else:
                key = None

            if fr is not None:
                first.append(fr)
                if key:
                    buckets[key]["first_response"].append(fr)
            if rs is not None:
                resolve.append(rs)
                if key:
                    buckets[key]["resolution"].append(rs)

            # SLA: compare the target Freshdesk set against what actually happened.
            fr_due, responded = _parse(t.get("fr_due_by")), _parse(stats.get("first_responded_at"))
            if fr_due:
                fr_target += 1
                if not responded or responded > fr_due:
                    fr_breach += 1
            due, resolved = _parse(t.get("due_by")), _parse(stats.get("resolved_at"))
            if due:
                res_target += 1
                if not resolved or resolved > due:
                    res_breach += 1

        def rate(breached: int, total: int) -> Optional[float]:
            return round(100 * breached / total, 1) if total else None

        report: JSON = {
            "period_start": updated_since,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tickets_analysed": len(tickets),
            "first_response": _summarise(first),
            "resolution": _summarise(resolve),
            "sla": {
                "first_response_targets": fr_target,
                "first_response_breaches": fr_breach,
                "first_response_breach_pct": rate(fr_breach, fr_target),
                "resolution_targets": res_target,
                "resolution_breaches": res_breach,
                "resolution_breach_pct": rate(res_breach, res_target),
            },
            "truncated": len(tickets) >= max_tickets,
        }
        if group_by:
            report["group_by"] = group_by
            report["breakdown"] = {
                k: {
                    "first_response": _summarise(v["first_response"]),
                    "resolution": _summarise(v["resolution"]),
                }
                for k, v in sorted(buckets.items())
            }
        return report

    @mcp.tool()
    @api_tool
    async def agent_performance_report(
        updated_since: str, max_tickets: int = 5000
    ) -> Any:
        """Per-agent workload: assigned, resolved, and response/resolution speed.

        Args:
            updated_since: ISO-8601 start of the period. Required.
        """
        tickets = await _fetch_tickets(updated_since, max_tickets)
        agents, _ = await _name_maps()

        rows: dict[str, JSON] = defaultdict(
            lambda: {"assigned": 0, "resolved": 0, "open": 0,
                     "_fr": [], "_res": []}
        )
        for t in tickets:
            name = agents.get(t.get("responder_id"), "Unassigned")
            row = rows[name]
            row["assigned"] += 1
            if t.get("status") in (4, 5):
                row["resolved"] += 1
            else:
                row["open"] += 1
            stats = t.get("stats") or {}
            fr = _hours(t.get("created_at"), stats.get("first_responded_at"))
            rs = _hours(t.get("created_at"), stats.get("resolved_at"))
            if fr is not None:
                row["_fr"].append(fr)
            if rs is not None:
                row["_res"].append(rs)

        out = {}
        for name, row in rows.items():
            out[name] = {
                "assigned": row["assigned"],
                "resolved": row["resolved"],
                "open": row["open"],
                "first_response": _summarise(row["_fr"]),
                "resolution": _summarise(row["_res"]),
            }
        return {
            "period_start": updated_since,
            "tickets_analysed": len(tickets),
            "agents": dict(sorted(out.items(), key=lambda kv: -kv[1]["assigned"])),
            "truncated": len(tickets) >= max_tickets,
        }

    @mcp.tool()
    @api_tool
    async def csat_report(created_since: Optional[str] = None,
                          max_ratings: int = 5000) -> Any:
        """Summarise satisfaction ratings over a period.

        Args:
            created_since: ISO-8601 start. Omit for everything available.
        """
        params = {"created_since": created_since} if created_since else {}
        ratings = await client.paginate(
            "surveys/satisfaction_ratings", params=params, max_items=max_ratings
        )

        buckets: Counter = Counter()
        per_agent: dict[Any, Counter] = defaultdict(Counter)
        scores: list[float] = []
        for r in ratings:
            values = (r.get("ratings") or {})
            for value in values.values():
                buckets[value] += 1
                if isinstance(value, (int, float)):
                    scores.append(float(value))
                if r.get("agent_id"):
                    per_agent[r["agent_id"]][value] += 1

        positive = sum(c for v, c in buckets.items() if isinstance(v, int) and v > 0)
        total = sum(buckets.values())
        return {
            "period_start": created_since,
            "responses": len(ratings),
            "rating_distribution": {str(k): v for k, v in sorted(buckets.items(), key=lambda x: str(x[0]))},
            "positive_pct": round(100 * positive / total, 1) if total else None,
            "mean_score": round(statistics.fmean(scores), 2) if scores else None,
            "by_agent": {str(a): dict(c) for a, c in per_agent.items()},
            "truncated": len(ratings) >= max_ratings,
        }

    @mcp.tool()
    @api_tool
    async def time_tracking_report(
        executed_after: Optional[str] = None,
        executed_before: Optional[str] = None,
        max_entries: int = 5000,
    ) -> Any:
        """Total logged time, split billable vs non-billable and by agent.

        Args:
            executed_after / executed_before: ISO-8601 bounds on when work was done.
        """
        params = {k: v for k, v in
                  {"executed_after": executed_after, "executed_before": executed_before}.items()
                  if v}
        entries = await client.paginate("time_entries", params=params, max_items=max_entries)
        agents, _ = await _name_maps()

        def to_hours(spent: Any) -> float:
            if not isinstance(spent, str) or ":" not in spent:
                return 0.0
            hh, _, mm = spent.partition(":")
            try:
                return int(hh) + int(mm) / 60
            except ValueError:
                return 0.0

        billable = nonbillable = 0.0
        per_agent: dict[str, float] = defaultdict(float)
        for e in entries:
            hours = to_hours(e.get("time_spent"))
            if e.get("billable"):
                billable += hours
            else:
                nonbillable += hours
            per_agent[agents.get(e.get("agent_id"), str(e.get("agent_id")))] += hours

        return {
            "period": {"from": executed_after, "to": executed_before},
            "entries": len(entries),
            "billable_hours": round(billable, 2),
            "non_billable_hours": round(nonbillable, 2),
            "total_hours": round(billable + nonbillable, 2),
            "by_agent_hours": {k: round(v, 2) for k, v in
                               sorted(per_agent.items(), key=lambda kv: -kv[1])},
            "truncated": len(entries) >= max_entries,
        }

    @mcp.tool()
    @api_tool
    async def backlog_report(max_tickets: int = 5000) -> Any:
        """Current open/pending backlog and how old it is.

        Unlike the other reports this looks at live state, not a period.
        """
        tickets = await client.paginate(
            "tickets", params={"include": "stats"}, max_items=max_tickets, per_page=100
        )
        agents, groups = await _name_maps()
        now = datetime.now(timezone.utc)

        ages: list[float] = []
        by_status: Counter = Counter()
        by_group: Counter = Counter()
        overdue = 0
        for t in tickets:
            if t.get("status") in (4, 5):
                continue
            by_status[_label(STATUS, t.get("status"))] += 1
            by_group[groups.get(t.get("group_id"), "Unassigned")] += 1
            created = _parse(t.get("created_at"))
            if created:
                ages.append((now - created).total_seconds() / 3600)
            due = _parse(t.get("due_by"))
            if due and due < now:
                overdue += 1

        return {
            "generated_at": now.isoformat(),
            "open_tickets": sum(by_status.values()),
            "overdue": overdue,
            "age_hours": _summarise(ages),
            "by_status": dict(by_status),
            "by_group": dict(by_group.most_common()),
            "truncated": len(tickets) >= max_tickets,
        }
