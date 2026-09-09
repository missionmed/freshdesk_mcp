"""Community forums: categories, forums, topics, comments and following."""
from __future__ import annotations

from typing import Any, Optional

from .. import client
from ._util import JSON, api_tool, compact


def register(mcp) -> None:
    @mcp.tool()
    @api_tool
    async def list_forum_categories() -> Any:
        """List forum categories."""
        return await client.get("discussions/categories")

    @mcp.tool()
    @api_tool
    async def get_forum_category(category_id: int) -> Any:
        """Retrieve a forum category."""
        return await client.get(f"discussions/categories/{category_id}")

    @mcp.tool()
    @api_tool
    async def create_forum_category(name: str, description: Optional[str] = None) -> Any:
        """Create a forum category."""
        return await client.post("discussions/categories",
                                 compact(name=name, description=description))

    @mcp.tool()
    @api_tool
    async def update_forum_category(category_id: int, fields: JSON) -> Any:
        """Update a forum category."""
        return await client.put(f"discussions/categories/{category_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_forum_category(category_id: int) -> Any:
        """Delete a forum category."""
        return await client.delete(f"discussions/categories/{category_id}")

    @mcp.tool()
    @api_tool
    async def list_forums_in_category(category_id: int) -> Any:
        """List forums inside a category."""
        return await client.get(f"discussions/categories/{category_id}/forums")

    @mcp.tool()
    @api_tool
    async def create_forum(category_id: int, name: str, forum_type: int = 1,
                           forum_visibility: int = 1,
                           description: Optional[str] = None) -> Any:
        """Create a forum.

        Args:
            forum_type: 1 howto, 2 ideas, 3 problems, 4 announcements.
            forum_visibility: 1 all, 2 logged-in, 3 agents, 4 select companies.
        """
        return await client.post(f"discussions/categories/{category_id}/forums", compact(
            name=name, forum_type=forum_type, forum_visibility=forum_visibility,
            description=description))

    @mcp.tool()
    @api_tool
    async def get_forum(forum_id: int) -> Any:
        """Retrieve a forum."""
        return await client.get(f"discussions/forums/{forum_id}")

    @mcp.tool()
    @api_tool
    async def update_forum(forum_id: int, fields: JSON) -> Any:
        """Update a forum."""
        return await client.put(f"discussions/forums/{forum_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_forum(forum_id: int) -> Any:
        """Delete a forum."""
        return await client.delete(f"discussions/forums/{forum_id}")

    @mcp.tool()
    @api_tool
    async def list_forum_topics(forum_id: int, page: int = 1, per_page: int = 30) -> Any:
        """List topics in a forum."""
        return await client.get(f"discussions/forums/{forum_id}/topics",
                                page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def follow_forum(forum_id: int, user_id: Optional[int] = None) -> Any:
        """Monitor a forum."""
        return await client.post(f"discussions/forums/{forum_id}/follow",
                                 compact(user_id=user_id))

    @mcp.tool()
    @api_tool
    async def unfollow_forum(forum_id: int) -> Any:
        """Stop monitoring a forum."""
        return await client.delete(f"discussions/forums/{forum_id}/follow")

    @mcp.tool()
    @api_tool
    async def get_forum_follow_status(forum_id: int, user_id: Optional[int] = None) -> Any:
        """Check whether a forum is being monitored."""
        return await client.get(f"discussions/forums/{forum_id}/follow",
                                **compact(user_id=user_id))

    @mcp.tool()
    @api_tool
    async def create_topic(forum_id: int, title: str, message: str,
                           sticky: Optional[int] = None, locked: Optional[int] = None) -> Any:
        """Create a topic in a forum."""
        return await client.post(f"discussions/forums/{forum_id}/topics", compact(
            title=title, message=message, sticky=sticky, locked=locked))

    @mcp.tool()
    @api_tool
    async def get_topic(topic_id: int) -> Any:
        """Retrieve a topic."""
        return await client.get(f"discussions/topics/{topic_id}")

    @mcp.tool()
    @api_tool
    async def update_topic(topic_id: int, fields: JSON) -> Any:
        """Update a topic."""
        return await client.put(f"discussions/topics/{topic_id}", fields)

    @mcp.tool()
    @api_tool
    async def delete_topic(topic_id: int) -> Any:
        """Delete a topic."""
        return await client.delete(f"discussions/topics/{topic_id}")

    @mcp.tool()
    @api_tool
    async def list_topic_comments(topic_id: int, page: int = 1, per_page: int = 30) -> Any:
        """List comments on a topic."""
        return await client.get(f"discussions/topics/{topic_id}/comments",
                                page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def create_comment(topic_id: int, body: str, user_id: Optional[int] = None) -> Any:
        """Comment on a topic."""
        return await client.post(f"discussions/topics/{topic_id}/comments",
                                 compact(body=body, user_id=user_id))

    @mcp.tool()
    @api_tool
    async def update_comment(comment_id: int, body: str) -> Any:
        """Edit a comment."""
        return await client.put(f"discussions/comments/{comment_id}", {"body": body})

    @mcp.tool()
    @api_tool
    async def delete_comment(comment_id: int) -> Any:
        """Delete a comment."""
        return await client.delete(f"discussions/comments/{comment_id}")

    @mcp.tool()
    @api_tool
    async def follow_topic(topic_id: int, user_id: Optional[int] = None) -> Any:
        """Monitor a topic."""
        return await client.post(f"discussions/topics/{topic_id}/follow",
                                 compact(user_id=user_id))

    @mcp.tool()
    @api_tool
    async def unfollow_topic(topic_id: int) -> Any:
        """Stop monitoring a topic."""
        return await client.delete(f"discussions/topics/{topic_id}/follow")

    @mcp.tool()
    @api_tool
    async def get_topic_follow_status(topic_id: int, user_id: Optional[int] = None) -> Any:
        """Check whether a user is monitoring a topic."""
        return await client.get(f"discussions/topics/{topic_id}/follow",
                                **compact(user_id=user_id))

    @mcp.tool()
    @api_tool
    async def list_monitored_topics(user_id: int, page: int = 1, per_page: int = 30) -> Any:
        """Topics a user monitors."""
        return await client.get("discussions/topics/followed_by",
                                user_id=user_id, page=page, per_page=per_page)

    @mcp.tool()
    @api_tool
    async def list_participated_topics(user_id: int, page: int = 1, per_page: int = 30) -> Any:
        """Topics a user has participated in."""
        return await client.get("discussions/topics/participated_by",
                                user_id=user_id, page=page, per_page=per_page)
