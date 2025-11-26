"""Search tool using Search1API."""

from __future__ import annotations

import os
from typing import Any, Literal

from pydantic import BaseModel


TimeRange = Literal["day", "week", "month", "year"]


class SearchResult(BaseModel):
    """Individual search result."""

    title: str
    """Title of the search result."""

    link: str
    """URL of the search result."""

    snippet: str
    """Text snippet/description of the result."""


class Search1APIResponse(BaseModel):
    """Search1API response model."""

    searchParameters: dict[str, Any]  # noqa: N815
    """Parameters used for the search."""

    results: list[SearchResult]
    """List of search results."""

    images: list[Any]
    """List of image results if requested."""


class AsyncSearch1API:
    """Async client for Search1API."""

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

    async def search(
        self,
        query: str,
        *,
        search_service: Literal["google", "bing"] = "google",
        max_results: int = 5,
        crawl_results: int = 0,
        include_images: bool = False,
        include_sites: list[str] | None = None,
        exclude_sites: list[str] | None = None,
        language: str | None = None,
        time_range: TimeRange | None = None,
    ) -> Search1APIResponse:
        """Execute search query.

        Args:
            query: Search query string
            search_service: Search engine to use
            max_results: Maximum number of results to return
            crawl_results: Number of results to crawl
            include_images: Whether to include image results
            include_sites: List of sites to include in search
            exclude_sites: List of sites to exclude from search
            language: Language code for results
            time_range: Time range for results

        Returns:
            Search results and metadata

        Raises:
            httpx.HTTPError: If API request fails
        """
        import anyenv

        payload = {
            "query": query,
            "search_service": search_service,
            "max_results": max_results,
            "crawl_results": crawl_results,
            "image": include_images,
        }

        if include_sites:
            payload["include_sites"] = include_sites
        if exclude_sites:
            payload["exclude_sites"] = exclude_sites
        if language:
            payload["language"] = language
        if time_range:
            payload["time_range"] = time_range
        data = await anyenv.post_json(
            self.base_url + "/search",
            headers=self.headers,
            json_data=payload,
            return_type=dict,
        )
        return Search1APIResponse(**data)


async def example() -> None:
    """Example usage of AsyncSearch1API."""
    client = AsyncSearch1API()
    results = await client.search(
        "Latest news about OpenAI",
        language="en",
        time_range="day",
    )
    print(results)


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
