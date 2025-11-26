"""Search1API client implementing search protocols."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Literal

import anyenv

from searchly.base import WebSearchProvider, WebSearchResponse, WebSearchResult


if TYPE_CHECKING:
    from searchly.base import CountryCode, LanguageCode


TimeRange = Literal["day", "week", "month", "year"]
SearchService = Literal["google", "bing"]


class AsyncSearch1API(WebSearchProvider):
    """Async client for Search1API.

    Note: Search1API does not support country filtering.
    The country parameter is accepted for protocol compatibility but is ignored.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.search1api.com",
    ):
        """Initialize Search1API client.

        Args:
            api_key: API key for Search1API. Defaults to SEARCH1API_KEY env var.
            base_url: Base URL for the API.
        """
        self.api_key = api_key or os.getenv("SEARCH1API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set SEARCH1API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def web_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        search_service: SearchService = "google",
        time_range: TimeRange | None = None,
        include_sites: list[str] | None = None,
        exclude_sites: list[str] | None = None,
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Execute a web search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Ignored (Search1API does not support country filtering).
            language: Language code for results.
            search_service: Search engine to use ("google" or "bing").
            time_range: Time range filter ("day", "week", "month", "year").
            include_sites: List of sites to include in search.
            exclude_sites: List of sites to exclude from search.
            **kwargs: Additional Search1API-specific options.

        Returns:
            Unified web search response.
        """
        payload: dict[str, Any] = {
            "query": query,
            "search_service": search_service,
            "max_results": max_results,
            **kwargs,
        }

        if language:
            payload["language"] = language
        if time_range:
            payload["time_range"] = time_range
        if include_sites:
            payload["include_sites"] = include_sites
        if exclude_sites:
            payload["exclude_sites"] = exclude_sites

        data = await anyenv.post_json(
            f"{self.base_url}/search",
            headers=self.headers,
            json_data=payload,
            return_type=dict,
        )

        results = [
            WebSearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
            )
            for item in data.get("results", [])
        ]
        return WebSearchResponse(results=results[:max_results])


async def example() -> None:
    """Example usage of AsyncSearch1API."""
    client = AsyncSearch1API()

    results = await client.web_search(
        "Latest news about OpenAI",
        max_results=5,
        language="en",
        time_range="day",
    )
    print(f"Found {len(results.results)} results")
    for result in results.results:
        print(f"  - {result.title}: {result.url}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
