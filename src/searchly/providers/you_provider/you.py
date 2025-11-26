"""You.com API client implementing search protocols."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Literal

import anyenv

from searchly.base import (
    NewsSearchProvider,
    NewsSearchResponse,
    NewsSearchResult,
    WebSearchProvider,
    WebSearchResponse,
    WebSearchResult,
)


if TYPE_CHECKING:
    from searchly.base import CountryCode, LanguageCode


SafeSearchLevel = Literal["off", "moderate", "strict"]
FreshnessFilter = Literal["day", "week", "month", "year"]


class AsyncYouClient(WebSearchProvider, NewsSearchProvider):
    """Async client for You.com API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.ydc-index.io",
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

    async def web_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        safesearch: SafeSearchLevel = "moderate",
        freshness: FreshnessFilter | str | None = None,
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Execute a web search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Country code for regional results (uppercase).
            language: Language code for results (converted to uppercase).
            safesearch: Content moderation level.
            freshness: Filter by recency ("day", "week", "month", "year").
            **kwargs: Additional You.com-specific options.

        Returns:
            Unified web search response.
        """
        params: dict[str, Any] = {
            "query": query,
            "count": max_results,
            "safesearch": safesearch,
            **kwargs,
        }

        if country:
            params["country"] = country
        if language:
            params["language"] = language.upper()
        if freshness:
            params["freshness"] = freshness

        url = f"{self.base_url}/search"
        response = await anyenv.get_json(url, headers=self.headers, params=params, return_type=dict)

        results = [
            WebSearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("description", ""),
            )
            for item in response.get("hits", [])
        ]
        return WebSearchResponse(results=results[:max_results])

    async def news_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        **kwargs: Any,
    ) -> NewsSearchResponse:
        """Execute a news search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Ignored (news endpoint does not support country filtering).
            language: Ignored (news endpoint does not support language filtering).
            **kwargs: Additional You.com-specific options.

        Returns:
            Unified news search response.
        """
        params: dict[str, Any] = {
            "q": query,
            **kwargs,
        }

        if max_results:
            params["count"] = max_results

        url = f"{self.base_url}/news"
        response = await anyenv.get_json(url, headers=self.headers, params=params, return_type=dict)

        news_data = response.get("news", {})
        results = [
            NewsSearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("description", ""),
                source=item.get("source_name"),
                published=item.get("age") or item.get("page_age"),
            )
            for item in news_data.get("results", [])
        ]
        return NewsSearchResponse(results=results[:max_results])


async def example() -> None:
    """Example usage of AsyncYouClient."""
    client = AsyncYouClient()

    web_results = await client.web_search(
        "Python programming",
        max_results=5,
        country="US",
        freshness="week",
    )
    print(f"Web results: {len(web_results.results)}")
    for result in web_results.results:
        print(f"  - {result.title}: {result.url}")

    news_results = await client.news_search("Python programming", max_results=5)
    print(f"News results: {len(news_results.results)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
