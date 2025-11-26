"""SerpAPI client implementing search protocols."""

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


TimePeriod = Literal["d", "w", "m", "y"]


class AsyncSerpAPIClient(WebSearchProvider, NewsSearchProvider):
    """Async client for SerpAPI."""

    BACKEND = "https://serpapi.com"

    def __init__(self, *, api_key: str | None = None):
        """Initialize SerpAPI client.

        Args:
            api_key: SerpAPI key. Defaults to SERPAPI_KEY env var.
        """
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            msg = "No API key provided. Set SERPAPI_KEY env var or pass api_key"
            raise ValueError(msg)

    async def web_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        location: str | None = None,
        safe: bool = True,
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Execute a web search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Country code for regional results (converted to lowercase).
            language: Language code for results (converted to lowercase).
            location: Location string (e.g. "Austin, Texas").
            safe: Enable safe search.
            **kwargs: Additional SerpAPI-specific options.

        Returns:
            Unified web search response.
        """
        params: dict[str, Any] = {
            "q": query,
            "num": max_results,
            "engine": "google",
            "api_key": self.api_key,
            "output": "json",
            "source": "python",
            **kwargs,
        }

        if country:
            params["gl"] = country.lower()
        if language:
            params["hl"] = language.lower()
        if location:
            params["location"] = location
        if safe:
            params["safe"] = "active"

        response = await anyenv.get_json(f"{self.BACKEND}/search", params=params, return_type=dict)

        results = [
            WebSearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
            )
            for item in response.get("organic_results", [])
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
        safe: bool = True,
        time_period: TimePeriod | None = None,
        **kwargs: Any,
    ) -> NewsSearchResponse:
        """Execute a news search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Country code for regional results (converted to lowercase).
            language: Language code for results (converted to lowercase).
            location: Location string (e.g. "Austin, Texas").
            safe: Enable safe search.
            time_period: Time period filter ("d"=day, "w"=week, "m"=month, "y"=year).
            **kwargs: Additional SerpAPI-specific options.

        Returns:
            Unified news search response.
        """
        params: dict[str, Any] = {
            "q": query,
            "tbm": "nws",
            "num": max_results,
            "engine": "google",
            "api_key": self.api_key,
            "output": "json",
            "source": "python",
            **kwargs,
        }

        if country:
            params["gl"] = country.lower()
        if language:
            params["hl"] = language.lower()
        if location:
            params["location"] = location
        if safe:
            params["safe"] = "active"
        if time_period:
            params["tbs"] = f"qdr:{time_period}"

        response = await anyenv.get_json(f"{self.BACKEND}/search", params=params, return_type=dict)

        results = [
            NewsSearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source=item.get("source"),
                published=item.get("date"),
            )
            for item in response.get("news_results", [])
        ]
        return NewsSearchResponse(results=results[:max_results])


async def example() -> None:
    """Example usage of AsyncSerpAPIClient."""
    client = AsyncSerpAPIClient()

    web_results = await client.web_search("Python programming", max_results=5, language="en")
    print(f"Web results: {len(web_results.results)}")
    for result in web_results.results:
        print(f"  - {result.title}: {result.url}")

    news_results = await client.news_search("Python programming", max_results=5, time_period="d")
    print(f"News results: {len(news_results.results)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
