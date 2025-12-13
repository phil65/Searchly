"""DataForSEO API client implementing search protocols."""

from __future__ import annotations

import base64
import os
from typing import Any, Literal

import anyenv

from searchly.base import (
    DATAFORSEO_COUNTRY_MAP,
    CountryCode,  # noqa: TC001
    LanguageCode,  # noqa: TC001
    NewsSearchProvider,
    NewsSearchResponse,
    NewsSearchResult,
    WebSearchProvider,
    WebSearchResponse,
    WebSearchResult,
)


OSType = Literal["windows", "macos", "android", "ios"]
DeviceType = Literal["desktop", "mobile", "tablet"]


class AsyncDataForSEOClient(WebSearchProvider, NewsSearchProvider):
    """Async client for DataForSEO API."""

    def __init__(
        self,
        *,
        login: str | None = None,
        password: str | None = None,
        base_url: str = "https://api.dataforseo.com/v3",
    ):
        """Initialize DataForSEO client.

        Args:
            login: DataForSEO login. Defaults to DATAFORSEO_LOGIN env var.
            password: DataForSEO password. Defaults to DATAFORSEO_PASSWORD env var.
            base_url: Base URL for the API.
        """
        self.login = login or os.getenv("DATAFORSEO_LOGIN")
        self.password = password or os.getenv("DATAFORSEO_PASSWORD")

        if not self.login or not self.password:
            msg = (
                "No credentials provided. Set DATAFORSEO_LOGIN and "
                "DATAFORSEO_PASSWORD env vars or pass login/password"
            )
            raise ValueError(msg)

        self.base_url = base_url
        auth = base64.b64encode(f"{self.login}:{self.password}".encode()).decode()
        self.headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

    async def web_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        device: DeviceType = "desktop",
        os: OSType = "windows",
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Execute a web search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return (max 100).
            country: Country code for regional results (ISO 3166-1 alpha-2).
            language: Language code for results (ISO 639-1).
            device: Device type for results.
            os: Operating system for results.
            **kwargs: Additional DataForSEO-specific options.

        Returns:
            Unified web search response.
        """
        # Default to US (2840) if no country specified
        location_code = DATAFORSEO_COUNTRY_MAP.get(country, 2840) if country else 2840

        endpoint = "/serp/google/organic/live/advanced"
        task: dict[str, Any] = {
            "keyword": query,
            "location_code": location_code,
            "language_code": language or "en",
            "device": device,
            "os": os,
            "depth": min(max_results, 100),
            **kwargs,
        }

        url = f"{self.base_url}{endpoint}"
        data = await anyenv.post_json(url, [task], headers=self.headers, return_type=dict)

        items = []
        if (tasks := data.get("tasks")) and (task_result := tasks[0].get("result")):
            items = task_result[0].get("items", [])

        results = [
            WebSearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("description") or "",
            )
            for item in items
            if item.get("type") in {"organic", "featured_snippet"}
        ]
        return WebSearchResponse(results=results[:max_results])

    async def news_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        device: DeviceType = "desktop",
        os: OSType = "windows",
        **kwargs: Any,
    ) -> NewsSearchResponse:
        """Execute a news search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return (max 100).
            country: Country code for regional results (ISO 3166-1 alpha-2).
            language: Language code for results (ISO 639-1).
            device: Device type for results.
            os: Operating system for results.
            **kwargs: Additional DataForSEO-specific options.

        Returns:
            Unified news search response.
        """
        # Default to US (2840) if no country specified
        location_code = DATAFORSEO_COUNTRY_MAP.get(country, 2840) if country else 2840

        endpoint = "/serp/google/news/live/advanced"
        task: dict[str, Any] = {
            "keyword": query,
            "location_code": location_code,
            "language_code": language or "en",
            "device": device,
            "os": os,
            "depth": min(max_results, 100),
            **kwargs,
        }

        url = f"{self.base_url}{endpoint}"
        data = await anyenv.post_json(url, [task], headers=self.headers, return_type=dict)

        items = []
        if (tasks := data.get("tasks")) and (task_result := tasks[0].get("result")):
            items = task_result[0].get("items", [])

        results = [
            NewsSearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet") or "",
                source=item.get("domain"),
                published=item.get("timestamp"),
            )
            for item in items
            if item.get("type") in {"news_search", "top_stories"}
        ]
        return NewsSearchResponse(results=results[:max_results])


async def example() -> None:
    """Example usage of AsyncDataForSEOClient."""
    client = AsyncDataForSEOClient()

    web_results = await client.web_search("Python programming", max_results=5)
    print(f"Web results: {len(web_results.results)}")
    for r in web_results.results:
        print(f"  - {r.title}: {r.url}")

    news_results = await client.news_search("Python programming", max_results=5)
    print(f"News results: {len(news_results.results)}")
    for news_result in news_results.results:
        print(f"  - {news_result.title}: {news_result.url}")


if __name__ == "__main__":
    anyenv.run_sync(example())
