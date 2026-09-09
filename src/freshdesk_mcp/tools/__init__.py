"""Tool registration. Each module exposes `register(mcp)`."""
from __future__ import annotations

from . import (
    admin,
    agents,
    canned_responses,
    companies,
    contacts,
    conversations,
    custom_objects,
    discussions,
    fields,
    groups,
    reporting,
    satisfaction,
    solutions,
    threads,
    tickets,
    time_entries,
)

MODULES = [
    tickets,
    conversations,
    contacts,
    companies,
    agents,
    groups,
    fields,
    solutions,
    canned_responses,
    discussions,
    satisfaction,
    time_entries,
    custom_objects,
    threads,
    admin,
    reporting,
]


def register_all(mcp) -> None:
    for module in MODULES:
        module.register(mcp)
