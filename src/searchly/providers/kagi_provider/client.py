"""Kagi API client."""

from __future__ import annotations

from datetime import datetime
import os
from typing import Any, Literal

import anyenv
from pydantic import BaseModel, Field


SearchEngine = Literal["web", "news", "images", "lore", "maps", "videos"]


class Thumbnail(BaseModel):
    """Image thumbnail data."""

    src: str
    width: int
    height: int


class SearchItem(BaseModel):
    """Individual search result item."""

    type: int
    rank: int | None = None
    url: str | None = None
    title: str | None = None
    snippet: str | None = None
    published: datetime | None = None
    thumbnail: Thumbnail | None = None
    list_items: list[str] = Field(default_factory=list, alias="list")


class SearchMeta(BaseModel):
    """Search metadata."""

    id: str
    node: str
    ms: int
    total: int | None = None


class SearchResponse(BaseModel):
    """Kagi search response model."""

    meta: SearchMeta
    data: list[SearchItem] = Field(default_factory=list)
    error: list[dict[str, Any]] = Field(default_factory=list)


class AsyncKagiClient:
    """Async client for Kagi API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://kagi.com/api/v0",
    ):
        """Initialize Kagi client.

        Args:
            api_key: Kagi API key. Defaults to KAGI_API_KEY env var.
            base_url: Base URL for the API.
        """
        self.api_key = api_key or os.getenv("KAGI_API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set KAGI_API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bot {self.api_key}",
            "Content-Type": "application/json",
        }

    async def search(
        self,
        query: str,
        *,
        engine: SearchEngine = "web",
        limit: int = 10,
        region: str | None = None,
        language: str | None = None,
    ) -> SearchResponse:
        """Execute search query using Kagi API.

        Args:
            query: Search query string
            engine: Search engine type to use
            limit: Maximum number of results to return
            region: Region code for search results (e.g., 'us', 'gb')
            language: Language code for results (e.g., 'en', 'es')

        Returns:
            Search results with metadata

        Raises:
            httpx.HTTPError: If API request fails
        """
        params: dict[str, Any] = {"q": query, "engine": engine, "limit": limit}

        if region:
            params["region"] = region
        if language:
            params["language"] = language
        url = f"{self.base_url}/search"
        data = await anyenv.get_json(url, params=params, headers=self.headers, return_type=dict)
        return SearchResponse(**data)

    async def summarize(
        self,
        query: str,
        *,
        target_language: str | None = None,
        summary_type: Literal["summary", "takeaway"] = "summary",
    ) -> str:
        """Get an AI-generated summary using the Kagi Universal Summarizer.

        Args:
            query: URL to summarize or a search query
            target_language: Target language for the summary
            summary_type: Type of summary to generate

        Returns:
            Generated summary text

        Raises:
            httpx.HTTPError: If API request fails
        """
        #  url Can be URL or a search query
        params: dict[str, Any] = {"url": query, "summary_type": summary_type}

        if target_language:
            params["target_language"] = target_language
        url = f"{self.base_url}/summarize"
        data = await anyenv.get_json(url, params=params, headers=self.headers, return_type=dict)
        return data.get("data", {}).get("output", "")  # type: ignore[no-any-return]


async def example() -> None:
    """Example usage of AsyncKagiClient."""
    client = AsyncKagiClient()
    results = await client.search("Python programming", limit=5, language="en")
    print(f"Found {len(results.data)} results")
    summary = await client.summarize("https://python.org", summary_type="takeaway")
    print(f"Summary: {summary}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
