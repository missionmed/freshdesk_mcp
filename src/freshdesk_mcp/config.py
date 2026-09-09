"""Runtime configuration, read once at import."""
from __future__ import annotations

import os


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


def _clean_domain(raw: str) -> str:
    """Accept a bare subdomain, a host, or a full URL and return the API host."""
    domain = raw.strip().rstrip("/")
    for prefix in ("https://", "http://"):
        if domain.startswith(prefix):
            domain = domain[len(prefix) :]
    domain = domain.split("/")[0]
    if "." not in domain:
        domain = f"{domain}.freshdesk.com"
    return domain


def get_domain() -> str:
    raw = os.getenv("FRESHDESK_DOMAIN")
    if not raw:
        raise ConfigError(
            "FRESHDESK_DOMAIN is required (e.g. 'yourcompany.freshdesk.com')."
        )
    return _clean_domain(raw)


def get_api_key() -> str:
    key = os.getenv("FRESHDESK_API_KEY")
    if not key:
        raise ConfigError(
            "FRESHDESK_API_KEY is required. Find it in Freshdesk under "
            "Profile settings > Your API Key."
        )
    return key.strip()


def base_url() -> str:
    return f"https://{get_domain()}/api/v2"


#: Freshdesk caps deep pagination; going past this returns errors rather than data.
MAX_PAGES = 300
MAX_PER_PAGE = 100
DEFAULT_PER_PAGE = 30
