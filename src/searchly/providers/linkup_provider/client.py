"""Search tool using LinkUp API."""

from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel


OutputType = Literal["sourcedAnswer", "searchResults", "structured"]
SearchDepth = Literal["standard", "deep"]


class Source(BaseModel):
    """Source information for a search result."""

    name: str
    url: str
    snippet: str


class LinkUpResponse(BaseModel):
    """LinkUp API response model."""

    answer: str | None = None
    sources: list[Source]


class AsyncLinkUpClient:
    """Async client for LinkUp API."""

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

    async def search(
        self,
        query: str,
        *,
        depth: SearchDepth = "standard",
        output_type: OutputType = "searchResults",
        include_images: bool = False,
        structured_schema: str | None = None,
    ) -> LinkUpResponse:
        """Execute search query using LinkUp API.

        Args:
            query: Search query string
            depth: Search depth - standard (faster) or deep (more thorough)
            output_type: Type of output format
            include_images: Whether to include images in results
            structured_schema: JSON schema for structured output (if applicable)

        Returns:
            Search results with sources

        Raises:
            httpx.HTTPError: If API request fails
        """
        import anyenv

        payload = {
            "q": query,
            "depth": depth,
            "outputType": output_type,
            "includeImages": include_images,
        }

        if output_type == "structured" and structured_schema:
            payload["structuredOutputSchema"] = structured_schema
        return await anyenv.post_json(
            f"{self.base_url}/search",
            json_data=payload,
            headers=self.headers,
            return_type=LinkUpResponse,
        )


async def example() -> None:
    """Example usage of AsyncLinkUpClient."""
    client = AsyncLinkUpClient()
    results = await client.search(
        "What is Microsoft's 2024 revenue?",
        output_type="sourcedAnswer",
    )
    print(results)


if __name__ == "__main__":
    import anyenv

    anyenv.run_sync(example())
