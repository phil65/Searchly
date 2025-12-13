"""Tavily API client implementing search protocols."""

from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
import contextlib
import os
from typing import Any, Literal

import anyenv
import httpx

from searchly.base import (
    CountryCode,  # noqa: TC001
    LanguageCode,  # noqa: TC001
    NewsSearchProvider,
    NewsSearchResponse,
    NewsSearchResult,
    WebSearchProvider,
    WebSearchResponse,
    WebSearchResult,
)
from searchly.exceptions import InvalidAPIKeyError, MissingAPIKeyError, UsageLimitExceededError


SearchDepth = Literal["basic", "advanced"]


class AsyncTavilyClient(WebSearchProvider, NewsSearchProvider):
    """Async client for Tavily API.

    Note: Tavily does not support country/language filtering directly.
    These parameters are accepted for protocol compatibility but are ignored.
    News search is implemented via the topic="news" parameter.
    """

    def __init__(self, *, api_key: str | None = None):
        """Initialize Tavily client.

        Args:
            api_key: Tavily API key. Defaults to TAVILY_API_KEY env var.
        """
        api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise MissingAPIKeyError

        self.api_key = api_key
        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        self.base_url = "https://api.tavily.com"
        self.timeout = 180

    def _client_creator(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self.headers, base_url=self.base_url, timeout=self.timeout)

    async def _search(
        self,
        query: str,
        *,
        search_depth: SearchDepth = "basic",
        topic: str = "general",
        days: int = 3,
        max_results: int = 10,
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Internal search method to send the request to the API."""
        data: dict[str, Any] = {
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "days": days,
            "max_results": max_results,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_answer": False,
            "include_raw_content": False,
            "include_images": False,
            **kwargs,
        }

        async with self._client_creator() as client:
            response = await client.post("/search", content=anyenv.dump_json(data))

        if response.status_code == 200:  # noqa: PLR2004
            return response.json()  # type: ignore[no-any-return]
        if response.status_code == 429:  # noqa: PLR2004
            detail = "Too many requests."
            with contextlib.suppress(Exception):
                detail = response.json()["detail"]["error"]
            raise UsageLimitExceededError(detail)
        if response.status_code == 401:  # noqa: PLR2004
            raise InvalidAPIKeyError
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    async def web_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        search_depth: SearchDepth = "basic",
        days: int = 3,
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Execute a web search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Ignored (Tavily does not support country filtering).
            language: Ignored (Tavily does not support language filtering).
            search_depth: Search depth ("basic" or "advanced").
            days: Number of days back to search.
            include_domains: List of domains to include.
            exclude_domains: List of domains to exclude.
            **kwargs: Additional Tavily-specific options.

        Returns:
            Unified web search response.
        """
        response = await self._search(
            query,
            search_depth=search_depth,
            topic="general",
            days=days,
            max_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            **kwargs,
        )

        results = [
            WebSearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
            )
            for item in response.get("results", [])
        ]
        return WebSearchResponse(results=results[:max_results])

    async def news_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        search_depth: SearchDepth = "basic",
        days: int = 3,
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> NewsSearchResponse:
        """Execute a news search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Ignored (Tavily does not support country filtering).
            language: Ignored (Tavily does not support language filtering).
            search_depth: Search depth ("basic" or "advanced").
            days: Number of days back to search.
            include_domains: List of domains to include.
            exclude_domains: List of domains to exclude.
            **kwargs: Additional Tavily-specific options.

        Returns:
            Unified news search response.
        """
        response = await self._search(
            query,
            search_depth=search_depth,
            topic="news",
            days=days,
            max_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            **kwargs,
        )

        results = [
            NewsSearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
                published=item.get("published_date"),
            )
            for item in response.get("results", [])
        ]
        return NewsSearchResponse(results=results[:max_results])


async def example() -> None:
    """Example usage of AsyncTavilyClient."""
    client = AsyncTavilyClient()

    web_results = await client.web_search("Python programming", max_results=5)
    print(f"Web results: {len(web_results.results)}")
    for result in web_results.results:
        print(f"  - {result.title}: {result.url}")

    news_results = await client.news_search("Python programming", max_results=5)
    print(f"News results: {len(news_results.results)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
