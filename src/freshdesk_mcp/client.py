"""Shared HTTP client for the Freshdesk API.

The upstream server repeated auth, URL building and error handling inside every
tool and handled neither rate limits nor pagination. All of that lives here now,
so tools stay a thin, declarative layer over the API.
"""
from __future__ import annotations

import asyncio
import base64
import logging
from typing import Any, Iterable, Mapping, Sequence

import httpx

from .config import DEFAULT_PER_PAGE, MAX_PAGES, MAX_PER_PAGE, base_url, get_api_key

logger = logging.getLogger(__name__)

TIMEOUT = httpx.Timeout(30.0, connect=10.0)
MAX_RETRIES = 4

JSON = dict[str, Any]


class FreshdeskError(RuntimeError):
    """An API call failed in a way the caller should see."""

    def __init__(self, message: str, status: int | None = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body

    def as_dict(self) -> JSON:
        out: JSON = {"error": str(self)}
        if self.status is not None:
            out["status_code"] = self.status
        if self.body:
            out["details"] = self.body
        return out


def _auth_header() -> str:
    token = base64.b64encode(f"{get_api_key()}:X".encode()).decode()
    return f"Basic {token}"


def _describe(status: int, body: Any) -> str:
    """Turn Freshdesk's error envelope into something actionable."""
    detail = ""
    if isinstance(body, Mapping):
        detail = str(body.get("description") or body.get("message") or "")
        errors = body.get("errors")
        if isinstance(errors, Sequence) and errors:
            parts = [
                f"{e.get('field')}: {e.get('message')}"
                for e in errors
                if isinstance(e, Mapping)
            ]
            if parts:
                detail = f"{detail} ({'; '.join(parts)})" if detail else "; ".join(parts)

    known = {
        400: "Bad request. Check the field names and values.",
        401: "Unauthenticated. Check FRESHDESK_API_KEY.",
        403: "Forbidden. The API key's agent lacks permission, or the plan "
             "does not include this feature.",
        404: "Not found. Check the id, and that FRESHDESK_DOMAIN is correct.",
        405: "Method not allowed.",
        406: "Unsupported Accept header.",
        409: "Conflict / inconsistent state.",
        415: "Content-Type must be application/json.",
        429: "Rate limited, and retries were exhausted.",
    }
    base = known.get(status, f"Freshdesk returned HTTP {status}.")
    return f"{base} {detail}".strip()


async def request(
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any = None,
    expect_json: bool = True,
) -> Any:
    """One API call, with retry on 429 and transient 5xx.

    Freshdesk publishes a per-minute (or per-hour) call budget and returns
    Retry-After when you exceed it. Honouring that is what makes bulk reads
    such as the reporting tools survive.
    """
    url = f"{base_url()}/{path.lstrip('/')}"
    headers = {"Authorization": _auth_header(), "Content-Type": "application/json"}
    clean = {k: v for k, v in (params or {}).items() if v is not None}

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = await client.request(
                    method, url, headers=headers, params=clean or None, json=json
                )
            except httpx.RequestError as exc:
                if attempt >= MAX_RETRIES:
                    raise FreshdeskError(f"Network error calling Freshdesk: {exc}") from exc
                await asyncio.sleep(2**attempt)
                continue

            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt >= MAX_RETRIES:
                    raise FreshdeskError(
                        _describe(resp.status_code, _safe_json(resp)),
                        resp.status_code,
                        _safe_json(resp),
                    )
                delay = float(resp.headers.get("Retry-After") or 2**attempt)
                logger.warning(
                    "Freshdesk %s on %s; retrying in %.0fs", resp.status_code, path, delay
                )
                await asyncio.sleep(min(delay, 60))
                continue

            if resp.status_code >= 400:
                raise FreshdeskError(
                    _describe(resp.status_code, _safe_json(resp)),
                    resp.status_code,
                    _safe_json(resp),
                )

            if resp.status_code == 204 or not resp.content:
                return {"success": True}
            return _safe_json(resp) if expect_json else resp.text

    raise FreshdeskError("Exhausted retries calling Freshdesk.")


def _safe_json(resp: httpx.Response) -> Any:
    try:
        return resp.json()
    except ValueError:
        return resp.text[:500]


async def get(path: str, **params: Any) -> Any:
    return await request("GET", path, params=params)


async def post(path: str, json: Any = None, **params: Any) -> Any:
    return await request("POST", path, json=json, params=params)


async def put(path: str, json: Any = None, **params: Any) -> Any:
    return await request("PUT", path, json=json, params=params)


async def delete(path: str, **params: Any) -> Any:
    return await request("DELETE", path, params=params)


async def paginate(
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    max_items: int | None = None,
    per_page: int = MAX_PER_PAGE,
    results_key: str | None = None,
) -> list[Any]:
    """Walk every page of a list endpoint.

    Freshdesk paginates with `page`/`per_page` and stops at 300 pages. Search
    endpoints instead wrap rows in {"results": [...], "total": n}, which
    `results_key` handles.
    """
    per_page = max(1, min(per_page, MAX_PER_PAGE))
    collected: list[Any] = []
    for page in range(1, MAX_PAGES + 1):
        payload = await request(
            "GET", path, params={**(params or {}), "page": page, "per_page": per_page}
        )
        rows = payload.get(results_key, []) if results_key and isinstance(payload, Mapping) else payload
        if not isinstance(rows, list):
            break
        collected.extend(rows)
        if max_items is not None and len(collected) >= max_items:
            return collected[:max_items]
        if len(rows) < per_page:
            break
    return collected


def chunked(items: Sequence[Any], size: int) -> Iterable[Sequence[Any]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


__all__ = [
    "FreshdeskError",
    "JSON",
    "chunked",
    "delete",
    "get",
    "paginate",
    "post",
    "put",
    "request",
    "DEFAULT_PER_PAGE",
]
