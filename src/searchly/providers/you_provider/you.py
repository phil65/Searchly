"""Search tool using You.com API."""

from __future__ import annotations

import os
from typing import Any, Literal

import anyenv
from pydantic import BaseModel, Field


SafeSearchLevel = Literal["off", "moderate", "strict"]
FreshnessFilter = Literal["day", "week", "month", "year"]
LivecrawlOption = Literal["web", "news", "all"]
LivecrawlFormat = Literal["html", "markdown"]


class WebResult(BaseModel):
    """Individual You.com web search result."""

    url: str
    title: str
    description: str
    snippets: list[str] = Field(default_factory=list)
    thumbnail_url: str | None = None
    page_age: str | None = None
    authors: list[str] = Field(default_factory=list)
    favicon_url: str | None = None


class NewsResult(BaseModel):
    """Individual You.com news result from unified search."""

    url: str
    title: str
    description: str
    thumbnail_url: str | None = None
    page_age: str | None = None


class LiveNewsMetaUrl(BaseModel):
    """URL metadata for live news result."""

    hostname: str | None = None
    netloc: str | None = None
    path: str | None = None
    scheme: str | None = None


class LiveNewsThumbnail(BaseModel):
    """Thumbnail for live news result."""

    src: str | None = None


class LiveNewsItem(BaseModel):
    """Individual live news result."""

    url: str
    title: str
    description: str
    age: str | None = None
    page_age: str | None = None
    source_name: str | None = None
    type: str | None = None
    thumbnail: LiveNewsThumbnail | None = None
    meta_url: LiveNewsMetaUrl | None = None
    article_id: str | None = None


class LiveNewsQuery(BaseModel):
    """Query info from live news response."""

    original: str | None = None
    spellcheck_off: bool | None = None


class LiveNewsMetadata(BaseModel):
    """Metadata from live news response."""

    request_uuid: str | None = None


class LiveNewsData(BaseModel):
    """Live news data container."""

    query: LiveNewsQuery | None = None
    results: list[LiveNewsItem] = Field(default_factory=list)
    type: str | None = None
    metadata: LiveNewsMetadata | None = None


class LiveNewsResponse(BaseModel):
    """You.com live news response."""

    news: LiveNewsData = Field(default_factory=LiveNewsData)


class SearchResults(BaseModel):
    """Container for web and news results."""

    web: list[WebResult] = Field(default_factory=list)
    news: list[NewsResult] = Field(default_factory=list)


class SearchMetadata(BaseModel):
    """Metadata from search response."""

    request_uuid: str | None = None
    query: str | None = None
    latency: float | None = None


class SearchResponse(BaseModel):
    """You.com unified search response."""

    results: SearchResults = Field(default_factory=SearchResults)
    metadata: SearchMetadata = Field(default_factory=SearchMetadata)


class AsyncYouClient:
    """Async client for You.com API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://ydc-index.io",
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
        self.headers = {"X-API-Key": self.api_key}

    async def search(
        self,
        query: str,
        *,
        count: int = 10,
        offset: int = 0,
        country: str | None = None,
        language: str | None = None,
        safesearch: SafeSearchLevel = "moderate",
        freshness: FreshnessFilter | str | None = None,
        livecrawl: LivecrawlOption | None = None,
        livecrawl_formats: LivecrawlFormat | None = None,
    ) -> SearchResponse:
        """Execute unified search query using You.com API.

        Returns web and news results based on query classification.

        Args:
            query: Search query string (supports search operators)
            count: Max results per section (web/news)
            offset: Pagination offset (0-9), results offset = count * offset
            country: Country code (e.g., 'US', 'GB')
            language: Language code in BCP 47 format (e.g., 'EN', 'DE')
            safesearch: Content moderation level
            freshness: Filter by recency ('day', 'week', 'month', 'year')
                       or date range 'YYYY-MM-DDtoYYYY-MM-DD'
            livecrawl: Which sections to livecrawl for full page content
            livecrawl_formats: Format for livecrawled content

        Returns:
            Search results containing web and news sections

        Raises:
            ValueError: If invalid parameters are provided
            httpx.HTTPError: If API request fails
        """
        if not 0 <= offset <= 9:  # noqa: PLR2004
            msg = "offset must be between 0 and 9"
            raise ValueError(msg)

        params: dict[str, Any] = {
            "query": query,
            "count": count,
            "offset": offset,
            "safesearch": safesearch,
        }

        if country:
            params["country"] = country
        if language:
            params["language"] = language
        if freshness:
            params["freshness"] = freshness
        if livecrawl:
            params["livecrawl"] = livecrawl
        if livecrawl_formats:
            params["livecrawl_formats"] = livecrawl_formats

        url = f"{self.base_url}/v1/search"
        response = await anyenv.get_json(url, headers=self.headers, params=params, return_type=dict)
        return SearchResponse(**response)

    async def news(
        self,
        query: str,
        *,
        count: int | None = None,
    ) -> LiveNewsResponse:
        """Execute live news search query.

        Uses separate endpoint at api.ydc-index.io/livenews.

        Args:
            query: News search query string
            count: Max number of news results to return

        Returns:
            Live news results

        Raises:
            httpx.HTTPError: If API request fails
        """
        params: dict[str, Any] = {"q": query}
        if count is not None:
            params["count"] = count

        url = "https://api.ydc-index.io/livenews"
        response = await anyenv.get_json(url, headers=self.headers, params=params, return_type=dict)
        return LiveNewsResponse(**response)


async def example() -> None:
    """Example usage of AsyncYouClient."""
    client = AsyncYouClient()

    # Search example - returns both web and news results
    results = await client.search(
        "climate change solutions", count=5, country="US", freshness="week"
    )
    print(f"Search found {len(results.results.web)} web results")
    print(f"Search found {len(results.results.news)} news results")
    if results.metadata.latency:
        print(f"Latency: {results.metadata.latency}ms")

    # Live news example
    news = await client.news("breaking news today", count=5)
    print(f"Live news found {len(news.news.results)} results")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
