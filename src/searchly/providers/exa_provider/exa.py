"""Exa API client."""

from __future__ import annotations

import os
from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Individual search result."""

    title: str
    url: str
    text: str | None = None
    summary: str | None = None
    author: str | None = None
    published_date: str | None = None
    score: float | None = None


class SearchResponse(BaseModel):
    """Exa search response."""

    results: list[SearchResult] = Field(default_factory=list)
    resolved_search_type: str | None = None
    cost_dollars: float | None = None


class SummaryOptions(TypedDict, total=False):
    """Options for structured summary."""

    schema: dict[str, Any]


class AsyncExaClient:
    """Async client for Exa API."""

    def __init__(self, *, api_key: str | None = None):
        """Initialize Exa client.

        Args:
            api_key: Exa API key. Defaults to EXA_API_KEY env var.
        """
        try:
            from exa_py import AsyncExa
        except ImportError as e:
            msg = "Could not import exa_py. Install it with 'pip install exa_py'"
            raise ImportError(msg) from e

        self.api_key = api_key or os.getenv("EXA_API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set EXA_API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.client = AsyncExa(api_key=self.api_key)

    async def search(
        self,
        query: str,
        *,
        num_results: int = 10,
        max_characters: int | None = None,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        start_published_date: str | None = None,
        end_published_date: str | None = None,
        search_type: Literal["auto", "keyword", "neural", "deep"] = "auto",
        category: str | None = None,
        summary: bool | dict[str, Any] | None = None,
    ) -> SearchResponse:
        """Execute search query using Exa API.

        Args:
            query: Search query string
            num_results: Number of results to return
            max_characters: Max characters for text content (None for full text)
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
            start_published_date: Only include content published after this date (ISO 8601)
            end_published_date: Only include content published before this date (ISO 8601)
            search_type: Type of search to perform
            category: Category to focus search on
            summary: Whether to include AI summary (True, or dict with schema)

        Returns:
            Search results with metadata
        """
        text_opts: dict[str, Any] | bool = True
        if max_characters is not None:
            text_opts = {"max_characters": max_characters}

        results = await self.client.search_and_contents(
            query=query,
            text=text_opts,
            summary=summary,
            num_results=num_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            start_published_date=start_published_date,
            end_published_date=end_published_date,
            type=search_type,
            category=category,
        )

        search_results = [
            SearchResult(
                title=result.title or "",
                url=result.url,
                text=result.text,
                summary=result.summary,
                author=result.author,
                published_date=result.published_date,
                score=result.score,
            )
            for result in results.results
        ]

        return SearchResponse(
            results=search_results,
            resolved_search_type=results.resolved_search_type,
            cost_dollars=results.cost_dollars.total if results.cost_dollars else None,
        )


async def example() -> None:
    """Example usage of AsyncExaClient."""
    client = AsyncExaClient()
    results = await client.search("AI advancements in 2023", num_results=3, max_characters=500)
    print(f"Found {len(results.results)} results")
    for result in results.results:
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Text: {result.text}")
        print("---")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
