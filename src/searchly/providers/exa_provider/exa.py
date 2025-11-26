"""Exa API client implementing search protocols."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Literal

from searchly.base import WebSearchProvider, WebSearchResponse, WebSearchResult


if TYPE_CHECKING:
    from searchly.base import CountryCode, LanguageCode


class AsyncExaClient(WebSearchProvider):
    """Async client for Exa API.

    Note: Exa does not support country/language filtering. These parameters
    are accepted for protocol compatibility but are ignored.
    """

    def __init__(self, *, api_key: str | None = None):
        """Initialize Exa client.

        Args:
            api_key: Exa API key. Defaults to EXA_API_KEY env var.
        """
        try:
            from exa_py import AsyncExa
        except ImportError as e:
            msg = "Could not import exa_py."
            raise ImportError(msg) from e

        self.api_key = api_key or os.getenv("EXA_API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set EXA_API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.client = AsyncExa(api_key=self.api_key)

    async def web_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        search_type: Literal["auto", "keyword", "neural", "deep"] = "auto",
        max_characters: int | None = None,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        start_published_date: str | None = None,
        end_published_date: str | None = None,
        category: str | None = None,
        summary: bool | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Execute a web search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Ignored (Exa does not support country filtering).
            language: Ignored (Exa does not support language filtering).
            search_type: Type of search ("auto", "keyword", "neural", "deep").
            max_characters: Max characters for text content.
            include_domains: List of domains to include.
            exclude_domains: List of domains to exclude.
            start_published_date: Only include content after this date (ISO 8601).
            end_published_date: Only include content before this date (ISO 8601).
            category: Category to focus search on.
            summary: Whether to include AI summary.
            **kwargs: Additional Exa-specific options.

        Returns:
            Unified web search response.
        """
        text_opts: dict[str, Any] | bool = True
        if max_characters is not None:
            text_opts = {"max_characters": max_characters}

        response = await self.client.search_and_contents(
            query=query,
            text=text_opts,
            summary=summary,
            num_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            start_published_date=start_published_date,
            end_published_date=end_published_date,
            type=search_type,
            category=category,
            **kwargs,
        )

        results = [
            WebSearchResult(
                title=result.title or "",
                url=result.url,
                snippet=result.text or result.summary or "",
            )
            for result in response.results
        ]
        return WebSearchResponse(results=results[:max_results])


async def example() -> None:
    """Example usage of AsyncExaClient."""
    client = AsyncExaClient()

    results = await client.web_search(
        "AI advancements in 2023",
        max_results=5,
        search_type="neural",
    )
    print(f"Found {len(results.results)} results")
    for result in results.results:
        print(f"  - {result.title}: {result.url}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
