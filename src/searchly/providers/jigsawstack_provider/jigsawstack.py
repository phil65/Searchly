"""JigsawStack API client implementing search protocols."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Literal

import anyenv

from searchly.base import WebSearchProvider, WebSearchResponse, WebSearchResult


if TYPE_CHECKING:
    from searchly.base import CountryCode, LanguageCode


SafeSearchSetting = Literal["moderate", "strict", "off"]


class AsyncJigsawStackClient(WebSearchProvider):
    """Async client for JigsawStack API.

    Note: JigsawStack does not support country/language/max_results filtering.
    These parameters are accepted for protocol compatibility but are ignored.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.jigsawstack.com/v1",
    ):
        """Initialize JigsawStack client.

        Args:
            api_key: JigsawStack API key. Defaults to JIGSAWSTACK_API_KEY env var.
            base_url: Base URL for the API.
        """
        self.api_key = api_key or os.getenv("JIGSAWSTACK_API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set JIGSAWSTACK_API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.base_url = base_url
        self.headers = {"Content-Type": "application/json", "x-api-key": self.api_key}

    async def web_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        ai_overview: bool = True,
        safe_search: SafeSearchSetting = "moderate",
        spell_check: bool = True,
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Execute a web search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Ignored (JigsawStack does not support country filtering).
            language: Ignored (JigsawStack does not support language filtering).
            ai_overview: Include AI-powered overview.
            safe_search: Safe search level.
            spell_check: Enable query spell checking.
            **kwargs: Additional JigsawStack-specific options.

        Returns:
            Unified web search response.
        """
        payload: dict[str, Any] = {
            "query": query,
            "ai_overview": ai_overview,
            "safe_search": safe_search,
            "spell_check": spell_check,
            **kwargs,
        }

        data = await anyenv.post_json(
            f"{self.base_url}/web/search",
            payload,
            headers=self.headers,
            return_type=dict,
        )

        results = [
            WebSearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("description", ""),
            )
            for item in data.get("results", [])
        ]
        return WebSearchResponse(results=results[:max_results])


async def example() -> None:
    """Example usage of AsyncJigsawStackClient."""
    client = AsyncJigsawStackClient()

    results = await client.web_search("What is the capital of France?", max_results=5)
    print(f"Found {len(results.results)} results")
    for result in results.results:
        print(f"  - {result.title}: {result.url}")


if __name__ == "__main__":
    anyenv.run_sync(example())
