"""Search tool using SerpAPI."""

from __future__ import annotations

import os
from typing import Any, Literal

from pydantic import BaseModel


class SearchResult(BaseModel):
    """Individual search result."""

    title: str
    link: str
    snippet: str
    position: int | None = None
    source: str | None = None


class SearchResponse(BaseModel):
    """SerpAPI search response."""

    search_parameters: dict[str, Any]
    search_metadata: dict[str, Any]
    organic_results: list[SearchResult]
    total_results: int | None = None
    search_information: dict[str, Any] | None = None
    pagination: dict[str, Any] | None = None


class AsyncSerpAPIClient:
    """Async wrapper for SerpAPI client."""

    def __init__(self, *, api_key: str | None = None):
        """Initialize SerpAPI client.

        Args:
            api_key: SerpAPI key. Defaults to SERPAPI_KEY env var.
        """
        import serpapi

        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            msg = "No API key provided. Set SERPAPI_KEY env var or pass api_key"
            raise ValueError(msg)

        self.client = serpapi.Client(api_key=self.api_key)

    async def search(
        self,
        query: str,
        *,
        search_type: Literal["search", "news", "images", "videos"] = "search",
        country: str | None = None,
        language: str | None = None,
        location: str | None = None,
        safe: bool = True,
        max_results: int = 10,
    ) -> SearchResponse:
        """Execute search query using SerpAPI.

        Args:
            query: Search query string
            search_type: Type of search to perform
            country: Country code (e.g. 'us', 'uk')
            language: Language code (e.g. 'en', 'es')
            location: Location string (e.g. 'Austin, Texas')
            safe: Enable safe search
            max_results: Maximum number of results to return

        Returns:
            Structured search results

        Raises:
            serpapi.HTTPError: If API request fails
        """
        # Build search parameters
        params: dict[str, Any] = {"q": query, "num": max_results}

        if country:
            params["gl"] = country.lower()
        if language:
            params["hl"] = language.lower()
        if location:
            params["location"] = location
        if safe:
            params["safe"] = "active"

        # Add search type specific parameters
        match search_type:
            case "search":
                params["engine"] = "google"
            case "news":
                params["engine"] = "google_news"
            case "images":
                params["engine"] = "google_images"
            case "videos":
                params["engine"] = "google_videos"

        # Execute search
        results = await self.client.search(**params)

        # Transform results into our standard format
        return SearchResponse(
            search_parameters=results["search_parameters"],
            search_metadata=results["search_metadata"],
            organic_results=[
                SearchResult(
                    title=result["title"],
                    link=result["link"],
                    snippet=result.get("snippet", ""),
                    position=result.get("position"),
                    source=result.get("source"),
                )
                for result in results.get("organic_results", [])
            ],
            total_results=results.get("search_information", {}).get("total_results"),
            search_information=results.get("search_information"),
            pagination=results.get("pagination"),
        )


async def example():
    """Example usage of AsyncSerpAPIClient."""
    client = AsyncSerpAPIClient()
    results = await client.search(
        "Python programming",
        language="en",
        country="us",
    )
    print(results)


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
