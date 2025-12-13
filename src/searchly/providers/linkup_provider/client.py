"""LinkUp API client implementing search protocols."""

from __future__ import annotations

import os
from typing import Any, Literal

import anyenv

from searchly.base import (
    CountryCode,  # noqa: TC001
    LanguageCode,  # noqa: TC001
    WebSearchProvider,
    WebSearchResponse,
    WebSearchResult,
)


OutputType = Literal["sourcedAnswer", "searchResults", "structured"]
SearchDepth = Literal["standard", "deep"]


class AsyncLinkUpClient(WebSearchProvider):
    """Async client for LinkUp API.

    Note: LinkUp does not support country/language/max_results filtering.
    These parameters are accepted for protocol compatibility but are ignored.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.linkup.so/v1",
    ):
        """Initialize LinkUp client.

        Args:
            api_key: LinkUp API key. Defaults to LINKUP_API_KEY env var.
            base_url: Base URL for the API.
        """
        self.api_key = api_key or os.getenv("LINKUP_API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set LINKUP_API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def web_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        depth: SearchDepth = "standard",
        output_type: OutputType = "searchResults",
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Execute a web search query.

        Args:
            query: Search query string.
            max_results: Ignored (LinkUp does not support result count).
            country: Ignored (LinkUp does not support country filtering).
            language: Ignored (LinkUp does not support language filtering).
            depth: Search depth - "standard" (faster) or "deep" (more thorough).
            output_type: Type of output format.
            **kwargs: Additional LinkUp-specific options.

        Returns:
            Unified web search response.
        """
        payload: dict[str, Any] = {"q": query, "depth": depth, "outputType": output_type, **kwargs}
        data = await anyenv.post_json(
            f"{self.base_url}/search",
            json_data=payload,
            headers=self.headers,
            return_type=dict,
        )
        results = [
            WebSearchResult(
                title=item.get("name", ""),
                url=item.get("url", ""),
                snippet=item.get("content", "") if item.get("content") else "",
            )
            for item in data.get("results", [])
            if item.get("url")
        ]
        return WebSearchResponse(results=results[:max_results])


async def example() -> None:
    """Example usage of AsyncLinkUpClient."""
    client = AsyncLinkUpClient()

    results = await client.web_search(
        "What is Microsoft's 2024 revenue?",
        depth="deep",
    )
    print(f"Found {len(results.results)} results")
    for result in results.results:
        print(f"  - {result.title}: {result.url}")


if __name__ == "__main__":
    anyenv.run_sync(example())
