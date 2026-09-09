"""Custom objects: schemas and records."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def list_custom_object_schemas() -> Any:
        """List custom object schemas."""
        return await client.get("custom_objects/schemas")

    @mcp.tool()
    @api_tool
    async def get_custom_object_schema(schema_id: str) -> Any:
        """Retrieve one custom object schema, including its fields."""
        return await client.get(f"custom_objects/schemas/{schema_id}")

    @mcp.tool()
    @api_tool
    async def create_custom_object_schema(payload: JSON) -> Any:
        """Create a custom object schema."""
        return await client.post("custom_objects/schemas", payload)

    @mcp.tool()
    @api_tool
    async def list_custom_object_records(schema_id: str, page: int = 1,
                                         per_page: int = 30) -> Any:
        """List records of a custom object."""
        return await client.get(f"custom_objects/schemas/{schema_id}/records",
                                page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def get_custom_object_record(schema_id: str, record_id: str) -> Any:
        """Retrieve one custom object record."""
        return await client.get(f"custom_objects/schemas/{schema_id}/records/{record_id}")

    @mcp.tool()
    @api_tool
    async def create_custom_object_record(schema_id: str, data: JSON) -> Any:
        """Create a custom object record."""
        return await client.post(f"custom_objects/schemas/{schema_id}/records", {"data": data})

    @mcp.tool()
    @api_tool
    async def update_custom_object_record(schema_id: str, record_id: str, data: JSON) -> Any:
        """Update a custom object record."""
        return await client.put(f"custom_objects/schemas/{schema_id}/records/{record_id}",
                                {"data": data})

    @mcp.tool()
    @api_tool
    async def delete_custom_object_record(schema_id: str, record_id: str) -> Any:
        """Delete a custom object record."""
        return await client.delete(f"custom_objects/schemas/{schema_id}/records/{record_id}")

    @mcp.tool()
    @api_tool
    async def count_custom_object_records(schema_id: str) -> Any:
        """Count records in a custom object."""
        return await client.get(f"custom_objects/schemas/{schema_id}/records/count")

    @mcp.tool()
    @api_tool
    async def filter_custom_object_records(schema_id: str, query: str,
                                           page: int = 1, per_page: int = 30) -> Any:
        """Filter custom object records with a query expression."""
        return await client.get(f"custom_objects/schemas/{schema_id}/records",
                                query=query, page=page, per_page=per_page)
