"""Search tool using You.com API."""

from __future__ import annotations

import os
from typing import Any, Literal

from pydantic import BaseModel, Field


SafeSearchLevel = Literal["off", "moderate", "strict"]
RecencyFilter = Literal["day", "week", "month", "year"]


class SearchResult(BaseModel):
    """Individual You.com search result."""

    url: str
    title: str
    description: str
    favicon_url: str | None = None
    thumbnail_url: str | None = None
    snippets: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """You.com search response."""

    hits: list[SearchResult] = Field(default_factory=list)
    latency: float = 0.0


class NewsItem(BaseModel):
    """Individual You.com news result."""

    url: str
    title: str
    description: str
    type: str
    age: str
    page_age: str
    breaking: bool = False
    page_fetched: str | None = None
    thumbnail: dict[str, str] | None = None
    meta_url: dict[str, str] | None = None


class NewsResponse(BaseModel):
    """You.com news response."""

    news: dict[str, list[NewsItem]]


class AsyncYouClient:
    """Async client for You.com API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://chat-api.you.com",
    ):
        """Initialize You.com client.

        Args:
            api_key: You.com API key. Defaults to YOU_API_KEY env var.
            base_url: Base URL for the API.
        """
        self.api_key = api_key or os.getenv("YOU_API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set YOU_API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    async def search(
        self,
        query: str,
        *,
        num_results: int = 10,
        offset: int = 0,
        country: str | None = None,
        safesearch: SafeSearchLevel = "moderate",
    ) -> SearchResponse:
        """Execute search query using You.com API.

        Args:
            query: Search query string
            num_results: Number of results to return (1-20)
            offset: Pagination offset (0-9)
            country: Country code (e.g., 'US', 'GB')
            safesearch: Content moderation level

        Returns:
            Search results with metadata

        Raises:
            ValueError: If invalid parameters are provided
            httpx.HTTPError: If API request fails
        """
        import anyenv

        if not 1 <= num_results <= 20:  # noqa: PLR2004
            msg = "num_results must be between 1 and 20"
            raise ValueError(msg)

        if not 0 <= offset <= 9:  # noqa: PLR2004
            msg = "offset must be between 0 and 9"
            raise ValueError(msg)

        params: dict[str, Any] = {
            "query": query,
            "num_web_results": num_results,
            "offset": offset,
            "safesearch": safesearch,
        }

        if country:
            params["country"] = country

        response = await anyenv.get_json(
            f"{self.base_url}/search",
            headers=self.headers,
            params=params,
            return_type=dict,
        )

        return SearchResponse(**response)

    async def news(
        self,
        query: str,
        *,
        count: int = 10,
        offset: int = 0,
        country: str | None = None,
        search_lang: str | None = None,
        ui_lang: str | None = None,
        safesearch: SafeSearchLevel = "moderate",
        spellcheck: bool = True,
        recency: RecencyFilter | None = None,
    ) -> NewsResponse:
        """Execute news search query using You.com API.

        Args:
            query: Search query string
            count: Number of results to return (1-20)
            offset: Pagination offset (0-9)
            country: Country code (e.g., 'US', 'GB')
            search_lang: Language code for search
            ui_lang: Language code for user interface
            safesearch: Content moderation level
            spellcheck: Enable spellcheck
            recency: Filter results by recency

        Returns:
            News results with metadata

        Raises:
            ValueError: If invalid parameters are provided
            httpx.HTTPError: If API request fails
        """
        import anyenv

        if not 1 <= count <= 20:  # noqa: PLR2004
            msg = "count must be between 1 and 20"
            raise ValueError(msg)

        if not 0 <= offset <= 9:  # noqa: PLR2004
            msg = "offset must be between 0 and 9"
            raise ValueError(msg)

        params: dict[str, str | float | bool | None] = {
            "query": query,
            "count": count,
            "offset": offset,
            "safesearch": safesearch,
            "spellcheck": spellcheck,
        }

        if country:
            params["country"] = country
        if search_lang:
            params["search_lang"] = search_lang
        if ui_lang:
            params["ui_lang"] = ui_lang
        if recency:
            params["recency"] = recency

        response = await anyenv.get_json(
            f"{self.base_url}/news",
            headers=self.headers,
            params=params,
            return_type=dict,
        )

        return NewsResponse(**response)


async def example():
    """Example usage of AsyncYouClient."""
    client = AsyncYouClient()

    # Search example
    search_results = await client.search(
        "climate change solutions",
        num_results=5,
        country="US",
    )
    print(f"Search found {len(search_results.hits)} results")

    # News example
    news_results = await client.news(
        "climate change solutions",
        count=5,
        recency="week",
    )
    print(news_results)


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
