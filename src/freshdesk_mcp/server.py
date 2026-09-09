"""Freshdesk MCP server.

Transport is chosen with TRANSPORT: "stdio" for a local client, or "http"
(the default) for a hosted deployment such as Railway.
"""
from __future__ import annotations

import logging
import os

from mcp.server.mcpserver import MCPServer

from .config import ConfigError, get_api_key, get_domain
from .tools import register_all

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("freshdesk_mcp")


def build_server() -> MCPServer:
    mcp = MCPServer("freshdesk", version="2.0.0")
    register_all(mcp)
    return mcp


def main() -> None:
    transport = os.getenv("TRANSPORT", "http").lower()

    # Fail fast and loudly: a server that starts without credentials only
    # reveals the problem later, one confusing 401 at a time.
    try:
        logger.info("Freshdesk domain: %s", get_domain())
        get_api_key()
    except ConfigError as exc:
        logger.error("%s", exc)
        raise SystemExit(1) from exc

    mcp = build_server()

    if transport == "stdio":
        logger.info("Starting Freshdesk MCP server on stdio")
        mcp.run(transport="stdio")
        return

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    logger.info("Starting Freshdesk MCP server on http://%s:%s/mcp", host, port)
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
        # Stateless keeps every request self-contained, which is what a hosted
        # multi-client deployment behind a load balancer needs.
        stateless_http=True,
        json_response=True,
    )


if __name__ == "__main__":
    main()
