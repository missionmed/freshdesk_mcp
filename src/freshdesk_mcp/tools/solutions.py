"""Knowledge base: solution categories, folders, subfolders and articles."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact

STATUS = {1: "Draft", 2: "Published"}


def register(mcp) -> None:
    # --- categories -----------------------------------------------------
    @mcp.tool()
    @api_tool
    async def list_solution_categories(page: int = 1, per_page: int = 30,
                                       language: Optional[str] = None) -> Any:
        """List solution categories, optionally in a translated language code."""
        path = f"solutions/categories/{language}" if language else "solutions/categories"
        return await client.get(path, page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def get_solution_category(category_id: int, language: Optional[str] = None) -> Any:
        """Retrieve a category, optionally in a translated language code."""
        path = f"solutions/categories/{category_id}"
        return await client.get(f"{path}/{language}" if language else path)

    @mcp.tool()
    @api_tool
    async def create_solution_category(name: str, description: Optional[str] = None,
                                       visible_in_portals: Optional[list[int]] = None) -> Any:
        """Create a solution category."""
        return await client.post("solutions/categories", compact(
            name=name, description=description, visible_in_portals=visible_in_portals))

    @mcp.tool()
    @api_tool
    async def update_solution_category(category_id: int, fields: JSON,
                                       language: Optional[str] = None) -> Any:
        """Update a category, or its translation when language is given."""
        path = f"solutions/categories/{category_id}"
        return await client.put(f"{path}/{language}" if language else path, fields)

    @mcp.tool()
    @api_tool
    async def delete_solution_category(category_id: int) -> Any:
        """Delete a category and everything in it."""
        return await client.delete(f"solutions/categories/{category_id}")

    # --- folders --------------------------------------------------------
    @mcp.tool()
    @api_tool
    async def list_solution_folders(category_id: int, page: int = 1, per_page: int = 30,
                                    language: Optional[str] = None) -> Any:
        """List folders in a category, optionally translated."""
        path = f"solutions/categories/{category_id}/folders"
        if language:
            path = f"{path}/{language}"
        return await client.get(path, page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def list_solution_subfolders(folder_id: int,
                                       language: Optional[str] = None) -> Any:
        """List subfolders nested inside a folder, optionally translated."""
        path = f"solutions/folders/{folder_id}/subfolders"
        return await client.get(f"{path}/{language}" if language else path)

    @mcp.tool()
    @api_tool
    async def get_solution_folder(folder_id: int, language: Optional[str] = None) -> Any:
        """Retrieve a folder, optionally translated."""
        path = f"solutions/folders/{folder_id}"
        return await client.get(f"{path}/{language}" if language else path)

    @mcp.tool()
    @api_tool
    async def create_solution_folder(category_id: int, name: str,
                                     description: Optional[str] = None,
                                     visibility: Optional[int] = None,
                                     company_ids: Optional[list[int]] = None,
                                     parent_folder_id: Optional[int] = None) -> Any:
        """Create a folder in a category.

        Args:
            visibility: 1 all, 2 logged-in users, 3 agents, 4 select companies,
                5 bots.
        """
        return await client.post(f"solutions/categories/{category_id}/folders", compact(
            name=name, description=description, visibility=visibility,
            company_ids=company_ids, parent_folder_id=parent_folder_id))

    @mcp.tool()
    @api_tool
    async def update_solution_folder(folder_id: int, fields: JSON,
                                     language: Optional[str] = None) -> Any:
        """Update a folder, or its translation when language is given."""
        path = f"solutions/folders/{folder_id}"
        return await client.put(f"{path}/{language}" if language else path, fields)

    @mcp.tool()
    @api_tool
    async def delete_solution_folder(folder_id: int) -> Any:
        """Delete a folder and its articles."""
        return await client.delete(f"solutions/folders/{folder_id}")

    # --- articles -------------------------------------------------------
    @mcp.tool()
    @api_tool
    async def list_solution_articles(folder_id: int, page: int = 1, per_page: int = 30,
                                     fetch_all: bool = False,
                                     language: Optional[str] = None) -> Any:
        """List articles in a folder, optionally translated."""
        path = f"solutions/folders/{folder_id}/articles"
        if language:
            path = f"{path}/{language}"
        if fetch_all:
            rows = await client.paginate(path)
            return {"articles": rows, "count": len(rows)}
        return await client.get(path, page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def get_solution_article(article_id: int, language: Optional[str] = None) -> Any:
        """Retrieve an article, optionally translated."""
        path = f"solutions/articles/{article_id}"
        return await client.get(f"{path}/{language}" if language else path)

    @mcp.tool()
    @api_tool
    async def create_solution_article(folder_id: int, title: str, description: str,
                                      status: int = 1, tags: Optional[list[str]] = None,
                                      seo_data: Optional[JSON] = None) -> Any:
        """Create an article.

        Args:
            description: Article body in HTML.
            status: 1 Draft, 2 Published.
        """
        return await client.post(f"solutions/folders/{folder_id}/articles", compact(
            title=title, description=description, status=status, tags=tags,
            seo_data=seo_data))

    @mcp.tool()
    @api_tool
    async def update_solution_article(article_id: int, fields: JSON,
                                      language: Optional[str] = None) -> Any:
        """Update an article, or its translation when language is given."""
        path = f"solutions/articles/{article_id}"
        return await client.put(f"{path}/{language}" if language else path, fields)

    @mcp.tool()
    @api_tool
    async def delete_solution_article(article_id: int) -> Any:
        """Delete an article."""
        return await client.delete(f"solutions/articles/{article_id}")

    # --- translations ---------------------------------------------------
    @mcp.tool()
    @api_tool
    async def create_solution_category_translation(category_id: int, language: str,
                                                   fields: JSON) -> Any:
        """Create a translation of a category.

        Args:
            language: Language code, e.g. "es", "fr", "de".
            fields: Translated {"name": ..., "description": ...}.
        """
        return await client.post(f"solutions/categories/{category_id}/{language}", fields)

    @mcp.tool()
    @api_tool
    async def create_solution_folder_translation(folder_id: int, language: str,
                                                 fields: JSON) -> Any:
        """Create a translation of a folder."""
        return await client.post(f"solutions/folders/{folder_id}/{language}", fields)

    @mcp.tool()
    @api_tool
    async def create_solution_article_translation(article_id: int, language: str,
                                                  fields: JSON) -> Any:
        """Create a translation of an article.

        Args:
            fields: Translated {"title": ..., "description": ..., "status": 1|2}.
        """
        return await client.post(f"solutions/articles/{article_id}/{language}", fields)

    @mcp.tool()
    @api_tool
    async def search_solution_articles(term: str, page: int = 1, per_page: int = 30) -> Any:
        """Full-text search across published knowledge base articles."""
        return await client.get("search/solutions", term=term, page=page, per_page=per_page)
