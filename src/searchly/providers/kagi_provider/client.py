"""Kagi API client implementing search protocols."""

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


SummaryType = Literal["summary", "takeaway"]


class AsyncKagiClient(WebSearchProvider, NewsSearchProvider):
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
            country: Country code for regional results (converted to lowercase).
            language: Language code for results.
            **kwargs: Additional Kagi-specific options.

        Returns:
            Unified web search response.
        """
        params: dict[str, Any] = {
            "q": query,
            "limit": max_results,
            **kwargs,
        }

        if country:
            params["region"] = country.lower()
        if language:
            params["language"] = language

        url = f"{self.base_url}/search"
        data = await anyenv.get_json(url, params=params, headers=self.headers, return_type=dict)

        results = [
            WebSearchResult(
                title=item.get("title") or "",
                url=item.get("url") or "",
                snippet=item.get("snippet") or "",
            )
            for item in data.get("data", [])
            if item.get("url")  # Filter out items without URLs
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
            country: Country code for regional results (converted to lowercase).
            language: Language code for results.
            **kwargs: Additional Kagi-specific options.

        Returns:
            Unified news search response.
        """
        params: dict[str, Any] = {
            "q": query,
            "limit": max_results,
            "engine": "news",
            **kwargs,
        }

        if country:
            params["region"] = country.lower()
        if language:
            params["language"] = language

        url = f"{self.base_url}/search"
        data = await anyenv.get_json(url, params=params, headers=self.headers, return_type=dict)

        results = [
            NewsSearchResult(
                title=item.get("title") or "",
                url=item.get("url") or "",
                snippet=item.get("snippet") or "",
                published=item.get("published"),
            )
            for item in data.get("data", [])
            if item.get("url")
        ]
        return NewsSearchResponse(results=results[:max_results])

    async def summarize(
        self,
        url: str,
        *,
        target_language: str | None = None,
        summary_type: SummaryType = "summary",
    ) -> str:
        """Get an AI-generated summary using the Kagi Universal Summarizer.

        Args:
            url: URL to summarize.
            target_language: Target language for the summary.
            summary_type: Type of summary to generate.

        Returns:
            Generated summary text.
        """
        params: dict[str, Any] = {"url": url, "summary_type": summary_type}

        if target_language:
            params["target_language"] = target_language

        endpoint = f"{self.base_url}/summarize"
        data = await anyenv.get_json(
            endpoint, params=params, headers=self.headers, return_type=dict
        )
        return data.get("data", {}).get("output", "")


async def example() -> None:
    """Example usage of AsyncKagiClient."""
    client = AsyncKagiClient()

    web_results = await client.web_search("Python programming", max_results=5, language="en")
    print(f"Web results: {len(web_results.results)}")
    for result in web_results.results:
        print(f"  - {result.title}: {result.url}")

    news_results = await client.news_search("Python programming", max_results=5)
    print(f"News results: {len(news_results.results)}")

    summary = await client.summarize("https://python.org", summary_type="takeaway")
    print(f"Summary: {summary}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
