"""Wrapper for brave_search_python_client."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Literal

import brave_search_python_client as brave


if TYPE_CHECKING:
    from brave_search_python_client import (
        ImageSearchApiResponse,
        NewsSearchApiResponse,
        VideoSearchApiResponse,
        WebSearchApiResponse,
    )


class AsyncBraveSearch:
    """Async wrapper for Brave Search API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        retries: int = 0,
        wait_time: int = 2,
    ):
        """Initialize Brave Search client.

        Args:
            api_key: Brave Search API key. Defaults to BRAVE_API_KEY env var.
            retries: Number of retries for failed requests. Defaults to 0.
            wait_time: Time to wait between retries in seconds. Defaults to 2.
        """
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set BRAVE_API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.client = brave.BraveSearch(api_key=self.api_key)
        self.retries = retries
        self.wait_time = wait_time

    async def search(
        self,
        query: str,
        *,
        search_type: Literal["web", "images", "news", "videos"] = "web",
        country: str | None = None,
        language: str | None = None,
    ) -> (
        WebSearchApiResponse
        | ImageSearchApiResponse
        | NewsSearchApiResponse
        | VideoSearchApiResponse
    ):
        """Execute a search query using Brave Search API.

        Args:
            query: Search query string
            search_type: Type of search to perform
            country: Country code for results (e.g. 'US')
            language: Language code for results (e.g. 'en')

        Returns:
            Search results based on search type

        Raises:
            BraveSearchAPIError: If API request fails
        """
        request = {
            "q": query,
            "text_layout": "paragraph",
        }

        if country:
            request["country"] = country
        if language:
            request["language"] = language

        match search_type:
            case "web":
                return await self.client.web(
                    request,
                    retries=self.retries,
                    wait_time=self.wait_time,
                )
            case "images":
                return await self.client.images(
                    request,
                    retries=self.retries,
                    wait_time=self.wait_time,
                )
            case "news":
                return await self.client.news(
                    request,
                    retries=self.retries,
                    wait_time=self.wait_time,
                )
            case "videos":
                return await self.client.videos(
                    request,
                    retries=self.retries,
                    wait_time=self.wait_time,
                )


async def example():
    """Example usage of AsyncBraveSearch."""
    client = AsyncBraveSearch()
    results = await client.search("Python programming")
    print(results)


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
