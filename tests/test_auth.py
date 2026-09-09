"""The bearer gate must reject anything that is not exactly the token."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from freshdesk_mcp.auth import BearerAuthMiddleware  # noqa: E402

TOKEN = "s3cret-token"
failures = []


async def call(path, auth_header):
    """Drive the middleware directly and report (status, reached_inner)."""
    reached = {"v": False}

    async def inner(scope, receive, send):
        reached["v"] = True
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    sent = []
    headers = [(b"authorization", auth_header.encode())] if auth_header is not None else []
    scope = {"type": "http", "path": path, "headers": headers}

    async def send(msg):
        sent.append(msg)

    await BearerAuthMiddleware(inner, TOKEN)(scope, lambda: None, send)
    status = next((m["status"] for m in sent if m["type"] == "http.response.start"), None)
    return status, reached["v"]


def check(label, got, want):
    if got != want:
        failures.append(f"{label}: got {got!r}, want {want!r}")


check("valid token passes", asyncio.run(call("/mcp", f"Bearer {TOKEN}")), (200, True))
check("no header rejected", asyncio.run(call("/mcp", None)), (401, False))
check("wrong token rejected", asyncio.run(call("/mcp", "Bearer nope")), (401, False))
check("bare token rejected", asyncio.run(call("/mcp", TOKEN)), (401, False))
check("prefix of token rejected", asyncio.run(call("/mcp", f"Bearer {TOKEN[:-1]}")), (401, False))
check("wrong scheme rejected", asyncio.run(call("/mcp", f"Basic {TOKEN}")), (401, False))
check("health is public", asyncio.run(call("/health", None)), (200, True))

# A non-HTTP scope (lifespan) must pass straight through, or startup hangs.
async def lifespan_passthrough():
    seen = {"v": False}

    async def inner(scope, receive, send):
        seen["v"] = True

    await BearerAuthMiddleware(inner, TOKEN)({"type": "lifespan"}, lambda: None, lambda m: None)
    return seen["v"]


check("lifespan passes through", asyncio.run(lifespan_passthrough()), True)

if failures:
    print("FAILED:")
    for f in failures:
        print("  -", f)
    raise SystemExit(1)
print("all auth tests passed")
