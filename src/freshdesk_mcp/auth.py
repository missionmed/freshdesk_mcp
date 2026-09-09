"""Bearer-token gate for the HTTP transport.

The MCP endpoint exposes destructive tools (deleting tickets, sending email as
the helpdesk), so a public URL is not an acceptable boundary on its own. When
MCP_AUTH_TOKEN is set every request must present it as `Authorization: Bearer
<token>`.

This is a pure ASGI middleware rather than a Starlette BaseHTTPMiddleware so it
never buffers a streaming response.
"""
from __future__ import annotations

import json
import secrets
from typing import Any, Awaitable, Callable

Scope = dict[str, Any]
Receive = Callable[[], Awaitable[dict[str, Any]]]
Send = Callable[[dict[str, Any]], Awaitable[None]]

#: Reachable without a token, so platform health checks keep working.
PUBLIC_PATHS = frozenset({"/health"})


class BearerAuthMiddleware:
    def __init__(self, app: Any, token: str) -> None:
        self.app = app
        self._expected = f"Bearer {token}"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http" or scope.get("path") in PUBLIC_PATHS:
            await self.app(scope, receive, send)
            return

        presented = ""
        for name, value in scope.get("headers") or []:
            if name == b"authorization":
                presented = value.decode("latin-1")
                break

        # Constant-time compare so the token cannot be recovered by timing.
        if not secrets.compare_digest(presented, self._expected):
            await self._unauthorized(send)
            return

        await self.app(scope, receive, send)

    @staticmethod
    async def _unauthorized(send: Send) -> None:
        body = json.dumps(
            {"error": "unauthorized",
             "detail": "Send 'Authorization: Bearer <MCP_AUTH_TOKEN>'."}
        ).encode()
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
                (b"www-authenticate", b'Bearer realm="freshdesk-mcp"'),
            ],
        })
        await send({"type": "http.response.body", "body": body})
