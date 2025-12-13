"""Serper.dev API client implementing search protocols."""

from __future__ import annotations

import os
from typing import Any, Literal

import anyenv

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


DateRange = Literal["h", "d", "w", "m", "y"]


class AsyncSerperClient(WebSearchProvider, NewsSearchProvider):
    """Async client for Serper.dev API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://google.serper.dev",
    ):
        """Initialize Serper client.

        Args:
            api_key: Serper.dev API key. Defaults to SERPER_API_KEY env var.
            base_url: Base URL for the Serper API.
        """
        self.api_key = api_key or os.environ.get("SERPER_API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set SERPER_API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.base_url = base_url

    async def web_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        location: str | None = None,
        date_range: DateRange | None = None,
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Execute a web search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Country code for regional results (converted to lowercase).
            language: Language code for results (converted to lowercase).
            location: Geographic location for search.
            date_range: Time range ("h"=hour, "d"=day, "w"=week, "m"=month, "y"=year).
            **kwargs: Additional Serper-specific options.

        Returns:
            Unified web search response.
        """
        payload: dict[str, Any] = {
            "q": query,
            "num": max_results,
            **kwargs,
        }

        if country:
            payload["gl"] = country.lower()
        if language:
            payload["hl"] = language
        if location:
            payload["location"] = location
        if date_range:
            payload["tbs"] = f"qdr:{date_range}"
        assert self.api_key
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        data = await anyenv.post_json(
            f"{self.base_url}/search",
            headers=headers,
            json_data=payload,
            return_type=dict,
        )

        results = [
            WebSearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
            )
            for item in data.get("organic", [])
        ]
        return WebSearchResponse(results=results[:max_results])

    async def news_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        location: str | None = None,
        date_range: DateRange | None = None,
        **kwargs: Any,
    ) -> NewsSearchResponse:
        """Execute a news search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Country code for regional results (converted to lowercase).
            language: Language code for results (converted to lowercase).
            location: Geographic location for search.
            date_range: Time range ("h"=hour, "d"=day, "w"=week, "m"=month, "y"=year).
            **kwargs: Additional Serper-specific options.

        Returns:
            Unified news search response.
        """
        payload: dict[str, Any] = {
            "q": query,
            "num": max_results,
            **kwargs,
        }

        if country:
            payload["gl"] = country.lower()
        if language:
            payload["hl"] = language
        if location:
            payload["location"] = location
        if date_range:
            payload["tbs"] = f"qdr:{date_range}"
        assert self.api_key
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        data = await anyenv.post_json(
            f"{self.base_url}/news",
            headers=headers,
            json_data=payload,
            return_type=dict,
        )

        results = [
            NewsSearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source=item.get("source"),
                published=item.get("date"),
            )
            for item in data.get("news", [])
        ]
        return NewsSearchResponse(results=results[:max_results])


async def example() -> None:
    """Example usage of AsyncSerperClient."""
    client = AsyncSerperClient()

    web_results = await client.web_search("Python programming", max_results=5, language="en")
    print(f"Web results: {len(web_results.results)}")
    for result in web_results.results:
        print(f"  - {result.title}: {result.url}")

    news_results = await client.news_search("Python programming", max_results=5)
    print(f"News results: {len(news_results.results)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
