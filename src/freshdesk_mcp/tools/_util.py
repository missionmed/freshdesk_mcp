"""Helpers shared by every tool module."""
from __future__ import annotations

import functools
from typing import Any, Awaitable, Callable

from ..client import FreshdeskError

JSON = dict[str, Any]


def api_tool(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """Return Freshdesk failures as data instead of raising.

    An MCP client copes far better with {"error": "..."} it can read and act on
    than with a stack trace, and callers keep the tool's normal shape.
    """

    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await fn(*args, **kwargs)
        except FreshdeskError as exc:
            return exc.as_dict()
        except Exception as exc:  # noqa: BLE001 - surfaced to the model, not swallowed
            return {"error": f"{type(exc).__name__}: {exc}"}

    return wrapper


def compact(**fields: Any) -> JSON:
    """Drop unset optional arguments so we never send nulls Freshdesk rejects."""
    return {k: v for k, v in fields.items() if v is not None}
