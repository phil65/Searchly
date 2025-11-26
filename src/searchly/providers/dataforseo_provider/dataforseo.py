"""Search tool using DataForSEO API."""

from __future__ import annotations

import base64
import os
from typing import Literal

from pydantic import BaseModel, ConfigDict


OSType = Literal["windows", "macos", "android", "ios"]
DeviceType = Literal["desktop", "mobile", "tablet"]


class SearchItem(BaseModel):
    """Individual search result item."""

    model_config = ConfigDict(str_to_lower=True)

    type: str
    rank_group: int
    rank_absolute: int
    domain: str
    title: str
    description: str | None = None
    url: str
    highlighted: list[str] | None = None


class SearchResponse(BaseModel):
    """DataForSEO search response."""

    status_code: int
    status_message: str
    cost: float
    time: str
    results: list[SearchItem]


class ScreenshotResponse(BaseModel):
    """Screenshot response from DataForSEO."""

    status_code: int
    status_message: str
    cost: float
    time: str
    image_url: str


class AsyncDataForSEOClient:
    """Async client for DataForSEO API."""

    def __init__(
        self,
        *,
        login: str | None = None,
        password: str | None = None,
        base_url: str = "https://api.dataforseo.com/v3",
    ):
        """Initialize DataForSEO client.

        Args:
            login: DataForSEO login. Defaults to DATAFORSEO_LOGIN env var.
            password: DataForSEO password. Defaults to DATAFORSEO_PASSWORD env var.
            base_url: Base URL for the API.
        """
        self.login = login or os.getenv("DATAFORSEO_LOGIN")
        self.password = password or os.getenv("DATAFORSEO_PASSWORD")

        if not self.login or not self.password:
            msg = (
                "No credentials provided. Set DATAFORSEO_LOGIN and "
                "DATAFORSEO_PASSWORD env vars or pass login/password"
            )
            raise ValueError(msg)

        self.base_url = base_url
        auth = base64.b64encode(f"{self.login}:{self.password}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        }

    async def search(
        self,
        query: str,
        *,
        country_code: int | None = None,
        language_code: str | None = None,
        device: DeviceType = "desktop",
        os: OSType = "windows",
        depth: int = 100,
    ) -> SearchResponse:
        """Execute organic search query using DataForSEO API.

        Args:
            query: Search query string
            country_code: Location code (e.g. 2826 for UK)
            language_code: Language code (e.g. 'en')
            device: Device type for results
            os: Operating system for results
            depth: Number of results to return (max 100)

        Returns:
            Search results with metadata

        Raises:
            httpx.HTTPError: If API request fails
        """
        import anyenv

        endpoint = "/serp/google/organic/live/advanced"
        payload = [
            {
                "keyword": query,
                "location_code": country_code,
                "language_code": language_code,
                "device": device,
                "os": os,
                "depth": min(depth, 100),
            }
        ]
        url = f"{self.base_url}{endpoint}"
        data = await anyenv.post_json(
            url,
            payload,
            headers=self.headers,
            return_type=dict,
        )

        if not data.get("tasks", []):
            msg = "No results found in response"
            raise ValueError(msg)

        task = data["tasks"][0]
        results = []
        if result := task.get("result"):
            for item in result[0].get("items", []):
                if item.get("type") in {"organic", "featured_snippet"}:
                    results.append(SearchItem(**item))  # noqa: PERF401

        return SearchResponse(
            status_code=data["status_code"],
            status_message=data["status_message"],
            cost=data.get("cost", 0.0),
            time=data.get("time", ""),
            results=results,
        )

    async def search_news(
        self,
        query: str,
        *,
        country_code: int | None = None,
        language_code: str | None = None,
        device: DeviceType = "desktop",
        os: OSType = "windows",
        depth: int = 100,
    ) -> SearchResponse:
        """Execute news search query using DataForSEO API.

        Args:
            query: Search query string
            country_code: Location code (e.g. 2826 for UK)
            language_code: Language code (e.g. 'en')
            device: Device type for results
            os: Operating system for results
            depth: Number of results to return (max 100)

        Returns:
            News search results with metadata

        Raises:
            httpx.HTTPError: If API request fails
        """
        import anyenv

        endpoint = "/serp/google/news/live/advanced"
        payload = [
            {
                "keyword": query,
                "location_code": country_code,
                "language_code": language_code,
                "device": device,
                "os": os,
                "depth": min(depth, 100),
            }
        ]
        url = f"{self.base_url}{endpoint}"
        data = await anyenv.post_json(
            url,
            payload,
            headers=self.headers,
            return_type=dict,
        )

        # Transform response into our format
        if not data.get("tasks", []):
            msg = "No results found in response"
            raise ValueError(msg)

        task = data["tasks"][0]
        results = []
        if result := task.get("result"):
            for item in result[0].get("items", []):
                # For news results, we might want to filter differently
                # but for now we'll keep it similar to the original
                results.append(SearchItem(**item))  # noqa: PERF401

        return SearchResponse(
            status_code=data["status_code"],
            status_message=data["status_message"],
            cost=data.get("cost", 0.0),
            time=data.get("time", ""),
            results=results,
        )

    async def get_screenshot(self, task_id: str, *, scale_factor: float = 1.0) -> str:
        """Get screenshot for a specific search result.

        Args:
            task_id: Task ID from a previous search result
            scale_factor: Scale factor for the screenshot (0.1-1.0)

        Returns:
            URL to the screenshot image

        Raises:
            ValueError: If scale factor is invalid
            httpx.HTTPError: If API request fails
        """
        import anyenv

        if not 0.1 <= scale_factor <= 1.0:  # noqa: PLR2004
            msg = "Scale factor must be between 0.1 and 1.0"
            raise ValueError(msg)

        endpoint = "/serp/screenshot"
        payload = [{"task_id": task_id, "browser_screen_scale_factor": scale_factor}]
        url = f"{self.base_url}{endpoint}"
        data = await anyenv.post_json(
            url,
            payload,
            headers=self.headers,
            return_type=dict,
        )

        if not data.get("tasks", []):
            msg = "No results found in response"
            raise ValueError(msg)

        task = data["tasks"][0]

        if (
            (result := task.get("result"))
            and (items := result[0].get("items"))
            and (image_url := items[0].get("image"))
        ):
            return image_url  # type: ignore[no-any-return]

        msg = "No screenshot URL found in response"
        raise ValueError(msg)


async def example() -> None:
    """Example usage of AsyncDataForSEOClient."""
    client = AsyncDataForSEOClient()
    results = await client.search(
        "Python programming",
        country_code=2826,  # UK
        language_code="en",
    )
    print(results)


if __name__ == "__main__":
    import anyenv

    anyenv.run_sync(example())
