"""Kagi API client implementing search protocols."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Literal

import anyenv

from searchly.base import (
    WebSearchProvider,
    WebSearchResponse,
    WebSearchResult,
)


if TYPE_CHECKING:
    from searchly.base import CountryCode, LanguageCode


SummaryType = Literal["summary", "takeaway"]
SummaryEngine = Literal["cecil", "agnes", "muriel"]


class AsyncKagiClient(WebSearchProvider):
    """Async client for Kagi API.

    Note: Kagi Search API requires API billing to be set up at
    https://kagi.com/settings/billing_api
    """

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
        self.headers = {"Authorization": f"Bot {self.api_key}"}

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
            country: Country code (not used - Kagi inherits account settings).
            language: Language code (not used - Kagi inherits account settings).
            **kwargs: Additional Kagi-specific options.

        Returns:
            Unified web search response.

        Note:
            Kagi Search API inherits personalization settings from your account,
            including blocked/promoted sites and regional preferences.
        """
        # country/language not documented in Kagi API - settings inherited from account
        _ = country, language

        params: dict[str, Any] = {"q": query, "limit": max_results, **kwargs}

        url = f"{self.base_url}/search"
        data = await anyenv.get_json(url, params=params, headers=self.headers, return_type=dict)

        # Filter to search results (t=0), excluding related searches (t=1)
        results = [
            WebSearchResult(
                title=item.get("title") or "",
                url=item.get("url") or "",
                snippet=item.get("snippet") or "",
            )
            for item in data.get("data", [])
            if item.get("t") == 0 and item.get("url")
        ]
        return WebSearchResponse(results=results[:max_results])

    async def summarize(
        self,
        url: str | None = None,
        text: str | None = None,
        *,
        engine: SummaryEngine = "cecil",
        summary_type: SummaryType = "summary",
        target_language: str | None = None,
        cache: bool = True,
    ) -> str:
        """Get an AI-generated summary using the Kagi Universal Summarizer.

        Args:
            url: URL to summarize. Exclusive with text.
            text: Text to summarize. Exclusive with url.
            engine: Summarization engine (cecil, agnes, or muriel).
            summary_type: Type of summary (summary or takeaway).
            target_language: Target language code for translation (e.g., "EN", "DE").
            cache: Whether to allow cached requests/responses.

        Returns:
            Generated summary text.

        Raises:
            ValueError: If neither url nor text is provided, or both are provided.
        """
        if url and text:
            msg = "Provide either url or text, not both"
            raise ValueError(msg)
        if not url and not text:
            msg = "Either url or text must be provided"
            raise ValueError(msg)

        params: dict[str, Any] = {
            "engine": engine,
            "summary_type": summary_type,
            "cache": str(cache).lower(),
        }

        if url:
            params["url"] = url
        if text:
            params["text"] = text
        if target_language:
            params["target_language"] = target_language

        endpoint = f"{self.base_url}/summarize"
        data = await anyenv.get_json(
            endpoint, params=params, headers=self.headers, return_type=dict
        )
        return data.get("data", {}).get("output", "")  # type: ignore[no-any-return]


async def example() -> None:
    """Example usage of AsyncKagiClient."""
    client = AsyncKagiClient()

    # Web search
    web_results = await client.web_search("Python programming", max_results=5)
    print(f"Web results: {len(web_results.results)}")
    for result in web_results.results:
        print(f"  - {result.title}: {result.url}")

    # Summarization
    summary = await client.summarize(
        url="https://python.org",
        engine="cecil",
        summary_type="takeaway",
    )
    print(f"Summary: {summary}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
