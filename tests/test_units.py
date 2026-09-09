"""Unit tests for the pure logic: config parsing, error shaping, report maths."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from freshdesk_mcp.client import FreshdeskError, _describe  # noqa: E402
from freshdesk_mcp.config import _clean_domain  # noqa: E402
from freshdesk_mcp.tools.reporting import _hours, _parse, _summarise  # noqa: E402

failures = []


def check(label, got, want):
    if got != want:
        failures.append(f"{label}: got {got!r}, want {want!r}")


# --- domain normalisation: users paste all of these ------------------------
check("bare subdomain", _clean_domain("missionmedorg"), "missionmedorg.freshdesk.com")
check("host", _clean_domain("missionmedorg.freshdesk.com"), "missionmedorg.freshdesk.com")
check("https url", _clean_domain("https://missionmedorg.freshdesk.com/"), "missionmedorg.freshdesk.com")
check("url with path", _clean_domain("https://missionmedorg.freshdesk.com/a/tickets"), "missionmedorg.freshdesk.com")

# --- error messages carry Freshdesk's field-level detail -------------------
msg = _describe(400, {"description": "Validation failed",
                      "errors": [{"field": "email", "message": "is invalid"}]})
check("400 detail", "email: is invalid" in msg, True)
check("401 hint", "FRESHDESK_API_KEY" in _describe(401, {}), True)
check("error dict", FreshdeskError("boom", 404).as_dict()["status_code"], 404)

# --- duration maths --------------------------------------------------------
check("hours", _hours("2026-01-01T00:00:00Z", "2026-01-01T06:00:00Z"), 6.0)
check("hours missing", _hours("2026-01-01T00:00:00Z", None), None)
check("hours negative", _hours("2026-01-02T00:00:00Z", "2026-01-01T00:00:00Z"), None)
check("parse none", _parse(None), None)

s = _summarise([1.0, 2.0, 3.0, 4.0, 100.0])
check("count", s["count"], 5)
check("median beats mean for outliers", s["median_hours"], 3.0)
check("mean", s["mean_hours"], 22.0)
check("empty summary", _summarise([]), {"count": 0})

if failures:
    print("FAILED:")
    for f in failures:
        print("  -", f)
    raise SystemExit(1)
print("all unit tests passed")
