"""Exa API client."""

from __future__ import annotations

import asyncio
import os
from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field


SearchMode = Literal["basic", "detailed"]


class SearchResult(BaseModel):
    """Individual search result."""

    title: str
    url: str
    snippet: str | None = None
    author: str | None = None
    published_date: str | None = None
    score: float | None = None


class SearchResponse(BaseModel):
    """Exa search response."""

    results: list[SearchResult] = Field(default_factory=list)
    autoprompt_string: str | None = None
    request_id: str | None = None


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
            from exa_py import Exa
        except ImportError as e:
            msg = "Could not import exa_py. Install it with 'pip install exa_py'"
            raise ImportError(msg) from e

        self.api_key = api_key or os.getenv("EXA_API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set EXA_API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.client = Exa(api_key=self.api_key)

    async def search(
        self,
        query: str,
        *,
        mode: SearchMode = "basic",
        num_results: int = 10,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        start_published_date: str | None = None,
        end_published_date: str | None = None,
        use_autoprompt: bool = True,
        search_type: Literal["auto", "keyword", "neural"] = "auto",
        category: str | None = None,
    ) -> SearchResponse:
        """Execute search query using Exa API.

        Args:
            query: Search query string
            mode: Search mode (basic=highlights, detailed=full text)
            num_results: Number of results to return
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
            start_published_date: Only include content published after this date
            end_published_date: Only include content published before this date
            use_autoprompt: Use AI to improve query
            search_type: Type of search to perform
            category: Category to focus search on

        Returns:
            Search results with metadata

        Raises:
            Exception: If API request fails
        """
        # Convert sync to async for consistency with other providers
        loop = asyncio.get_event_loop()

        results: Any
        if mode == "basic":
            # Use highlights mode
            results = await loop.run_in_executor(
                None,
                lambda: self.client.search_and_contents(
                    query=query,
                    highlights=True,
                    num_results=num_results,
                    include_domains=include_domains,
                    exclude_domains=exclude_domains,
                    start_published_date=start_published_date,
                    end_published_date=end_published_date,
                    use_autoprompt=use_autoprompt,
                    type=search_type,
                    category=category,
                ),
            )
        else:
            # Use full text mode
            results = await loop.run_in_executor(
                None,
                lambda: self.client.search_and_contents(
                    query=query,
                    text=True,
                    num_results=num_results,
                    include_domains=include_domains,
                    exclude_domains=exclude_domains,
                    start_published_date=start_published_date,
                    end_published_date=end_published_date,
                    use_autoprompt=use_autoprompt,
                    type=search_type,
                    category=category,
                ),
            )

        # Transform the results into our standard format
        search_results = []
        for result in results.results:
            snippet = None
            if mode == "basic" and (highlights := getattr(result, "highlights", None)):
                snippet = " ".join(highlights)
            elif mode == "detailed" and (text := getattr(result, "text", None)):
                snippet = text[:500] + "..." if len(text) > 500 else text  # noqa: PLR2004

            search_results.append(
                SearchResult(
                    title=result.title or "",
                    url=result.url,
                    snippet=snippet,
                    author=result.author,
                    published_date=result.published_date,
                    score=result.score,
                )
            )

        return SearchResponse(
            results=search_results,
            autoprompt_string=getattr(results, "autoprompt_string", None),
            request_id=getattr(results, "request_id", None),
        )


async def example():
    """Example usage of AsyncExaClient."""
    client = AsyncExaClient()
    results = await client.search(
        "AI advancements in 2023",
        mode="basic",
        num_results=3,
    )
    print(f"Found {len(results.results)} results")
    for result in results.results:
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet}")
        print("---")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
