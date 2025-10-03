"""Search tool using SerpAPI."""

from __future__ import annotations

import os
from typing import Any, Literal

from pydantic import BaseModel


TimePeriod = Literal["d", "w", "m", "y"]


class NewsResult(BaseModel):
    """Individual news search result."""

    title: str
    link: str
    snippet: str
    source: str | None = None
    date: str | None = None
    thumbnail: str | None = None
    position: int | None = None


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


class NewsSearchResponse(BaseModel):
    """SerpAPI news search response."""

    search_parameters: dict[str, Any]
    search_metadata: dict[str, Any]
    news_results: list[NewsResult]
    total_results: int | None = None
    search_information: dict[str, Any] | None = None
    pagination: dict[str, Any] | None = None


class AsyncSerpAPIClient:
    """Async client for SerpAPI."""

    BACKEND = "https://serpapi.com"

    def __init__(self, *, api_key: str | None = None):
        """Initialize SerpAPI client.

        Args:
            api_key: SerpAPI key. Defaults to SERPAPI_KEY env var.
        """
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            msg = "No API key provided. Set SERPAPI_KEY env var or pass api_key"
            raise ValueError(msg)

    async def search(
        self,
        query: str,
        *,
        country: str | None = None,
        language: str | None = None,
        location: str | None = None,
        safe: bool = True,
        max_results: int = 10,
    ) -> SearchResponse:
        """Execute web search query using SerpAPI.

        Args:
            query: Search query string
            country: Country code (e.g. 'us', 'uk')
            language: Language code (e.g. 'en', 'es')
            location: Location string (e.g. 'Austin, Texas')
            safe: Enable safe search
            max_results: Maximum number of results to return

        Returns:
            Structured search results

        Raises:
            Exception: If API request fails
        """
        import anyenv

        # Build search parameters
        params: dict[str, Any] = {
            "q": query,
            "num": max_results,
            "engine": "google",
            "api_key": self.api_key,
            "output": "json",
            "source": "python",
        }

        if country:
            params["gl"] = country.lower()
        if language:
            params["hl"] = language.lower()
        if location:
            params["location"] = location
        if safe:
            params["safe"] = "active"

        # Execute search
        response = await anyenv.get_json(
            f"{self.BACKEND}/search",
            params=params,
            return_type=dict,
        )

        # Transform results into our standard format
        return SearchResponse(
            search_parameters=response.get("search_parameters", {}),
            search_metadata=response.get("search_metadata", {}),
            organic_results=[
                SearchResult(
                    title=result["title"],
                    link=result["link"],
                    snippet=result.get("snippet", ""),
                    position=result.get("position"),
                    source=result.get("source"),
                )
                for result in response.get("organic_results", [])
            ],
            total_results=response.get("search_information", {}).get("total_results"),
            search_information=response.get("search_information", {}),
            pagination=response.get("pagination", {}),
        )

    async def search_news(
        self,
        query: str,
        *,
        country: str | None = None,
        language: str | None = None,
        location: str | None = None,
        safe: bool = True,
        time_period: TimePeriod | None = None,
        max_results: int = 10,
        offset: int = 0,
    ) -> NewsSearchResponse:
        """Execute news search query using SerpAPI.

        Args:
            query: Search query string
            country: Country code (e.g. 'us', 'uk')
            language: Language code (e.g. 'en', 'es')
            location: Location string (e.g. 'Austin, Texas')
            safe: Enable safe search
            time_period: Time period filter (d=day, w=week, m=month, y=year)
            max_results: Maximum number of results to return
            offset: Pagination offset (multiples of max_results)

        Returns:
            Structured news search results

        Raises:
            Exception: If API request fails
        """
        import anyenv

        # Build search parameters
        params: dict[str, Any] = {
            "q": query,
            "tbm": "nws",  # Set to news search
            "num": max_results,
            "api_key": self.api_key,
            "output": "json",
            "source": "python",
            "engine": "google",
        }

        # Apply pagination if requested
        if offset > 0:
            params["start"] = offset * max_results

        # Apply time period filter if provided
        if time_period:
            params["tbs"] = f"qdr:{time_period}"

        if country:
            params["gl"] = country.lower()
        if language:
            params["hl"] = language.lower()
        if location:
            params["location"] = location
        if safe:
            params["safe"] = "active"

        # Execute search
        response = await anyenv.get_json(
            f"{self.BACKEND}/search",
            params=params,
            return_type=dict,
        )

        # Transform results into our standard format
        return NewsSearchResponse(
            search_parameters=response.get("search_parameters", {}),
            search_metadata=response.get("search_metadata", {}),
            news_results=[
                NewsResult(
                    title=result["title"],
                    link=result["link"],
                    snippet=result.get("snippet", ""),
                    source=result.get("source", ""),
                    date=result.get("date", ""),
                    thumbnail=result.get("thumbnail", ""),
                    position=result.get("position"),
                )
                for result in response.get("news_results", [])
            ],
            total_results=response.get("search_information", {}).get("total_results"),
            search_information=response.get("search_information", {}),
            pagination=response.get("pagination", {}),
        )


async def example():
    """Example usage of AsyncSerpAPIClient."""
    client = AsyncSerpAPIClient()

    # Regular web search
    web_results = await client.search(
        "Python programming",
        language="en",
        country="us",
    )
    print("Web results:", len(web_results.organic_results))

    # News search
    news_results = await client.search_news(
        "Python programming",
        language="en",
        country="us",
        time_period="d",  # Last day
    )
    print("News results:", len(news_results.news_results))


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
