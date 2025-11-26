"""Brave Search API client implementing search protocols."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, cast

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


class AsyncBraveSearch(WebSearchProvider, NewsSearchProvider):
    """Async client for Brave Search API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        retries: int = 0,
        wait_time: int = 2,
    ):
        """Initialize Brave Search client.

        Args:
            api_key: Brave Search API key. Defaults to BRAVE_API_KEY env var.
            retries: Number of retries for failed requests.
            wait_time: Time to wait between retries in seconds.
        """
        import brave_search_python_client as brave  # type: ignore[import-untyped]

        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set BRAVE_API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.client = brave.BraveSearch(api_key=self.api_key)
        self.retries = retries
        self.wait_time = wait_time

    async def web_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Execute a web search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Country code for regional results (ISO 3166-1 alpha-2).
            language: Language code for results (ISO 639-1).
            **kwargs: Additional Brave-specific options.

        Returns:
            Unified web search response.
        """
        import brave_search_python_client as brave

        req = brave.WebSearchRequest(
            q=query,
            count=max_results,
            country=cast("brave.CountryCode | None", country),
            search_lang=language,
            **kwargs,
        )
        response = await self.client.web(req, retries=self.retries, wait_time=self.wait_time)

        results = [
            WebSearchResult(
                title=item.title,
                url=str(item.url),
                snippet=item.description or "",
            )
            for item in (response.web.results if response.web else [])
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
            country: Country code for regional results (ISO 3166-1 alpha-2).
            language: Language code for results (ISO 639-1).
            **kwargs: Additional Brave-specific options.

        Returns:
            Unified news search response.
        """
        import brave_search_python_client as brave

        req = brave.NewsSearchRequest(
            q=query,
            count=max_results,
            country=cast("brave.CountryCode | None", country),
            search_lang=language,
            **kwargs,
        )
        response = await self.client.news(req, retries=self.retries, wait_time=self.wait_time)

        results = [
            NewsSearchResult(
                title=item.title,
                url=str(item.url),
                snippet=item.description,
                source=item.meta_url.hostname if item.meta_url else None,
                published=item.age,
            )
            for item in response.results
        ]
        return NewsSearchResponse(results=results[:max_results])


async def example() -> None:
    """Example usage of AsyncBraveSearch."""
    client = AsyncBraveSearch()

    web_results = await client.web_search("Python programming", max_results=5)
    print(f"Web results: {len(web_results.results)}")

    news_results = await client.news_search("Python programming", max_results=5)
    print(f"News results: {len(news_results.results)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
