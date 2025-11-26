"""Tavily API client class."""

from __future__ import annotations

import asyncio
import contextlib
import os
from typing import TYPE_CHECKING, Any, Literal

import httpx

from searchly.exceptions import (
    BadRequestError,
    InvalidAPIKeyError,
    MissingAPIKeyError,
    UsageLimitExceededError,
)
from searchly.utils import get_max_items_from_list


if TYPE_CHECKING:
    from collections.abc import Sequence

SearchDepth = Literal["basic", "advanced"]
Topic = Literal["general", "news"]


class AsyncTavilyClient:
    """Async Tavily API client class."""

    def __init__(
        self,
        api_key: str | None = None,
        company_info_tags: Sequence[str] = ("news", "general", "finance"),
    ):

        if api_key is None:
            api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise MissingAPIKeyError

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        self.base_url = "https://api.tavily.com"
        self.timeout = 180
        self._company_info_tags = company_info_tags

    def _client_creator(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            headers=self.headers,
            base_url=self.base_url,
            timeout=self.timeout,
        )

    async def _search(
        self,
        query: str,
        search_depth: SearchDepth = "basic",
        topic: Topic = "general",
        days: int = 3,
        max_results: int = 5,
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        include_answer: bool = False,
        include_raw_content: bool = False,
        include_images: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Internal search method to send the request to the API."""
        import anyenv

        data = {
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "days": days,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "max_results": max_results,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_images": include_images,
        }

        if kwargs:
            data.update(kwargs)

        async with self._client_creator() as client:
            response = await client.post("/search", content=anyenv.dump_json(data))

        if response.status_code == 200:  # noqa: PLR2004
            return response.json()  # type: ignore[no-any-return]
        if response.status_code == 429:  # noqa: PLR2004
            detail = "Too many requests."
            with contextlib.suppress(Exception):
                detail = response.json()["detail"]["error"]

            raise UsageLimitExceededError(detail)
        if response.status_code == 401:  # noqa: PLR2004
            raise InvalidAPIKeyError
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    async def search(
        self,
        query: str,
        search_depth: SearchDepth = "basic",
        topic: Topic = "general",
        days: int = 3,
        max_results: int = 5,
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        include_answer: bool = False,
        include_raw_content: bool = False,
        include_images: bool = False,
        **kwargs: Any,  # Accept custom arguments
    ) -> dict[str, Any]:
        """Combined search method. Set search_depth to either "basic" or "advanced"."""
        response_dict = await self._search(
            query,
            search_depth=search_depth,
            topic=topic,
            days=days,
            max_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            include_images=include_images,
            **kwargs,
        )

        response_dict["results"] = response_dict.get("results", [])

        return response_dict

    async def _extract(self, urls: list[str] | str, **kwargs: Any) -> dict[str, Any]:
        """Internal extract method to send the request to the API."""
        import anyenv

        data = {"urls": urls}
        if kwargs:
            data.update(kwargs)

        async with self._client_creator() as client:
            response = await client.post("/extract", content=anyenv.dump_json(data))

        if response.status_code == 200:  # noqa: PLR2004
            return response.json()  # type: ignore[no-any-return]
        if response.status_code == 400:  # noqa: PLR2004
            detail = "Bad request. The request was invalid or cannot be served."
            with contextlib.suppress(KeyError):
                detail = response.json()["detail"]["error"]
            raise BadRequestError(detail)
        if response.status_code == 401:  # noqa: PLR2004
            raise InvalidAPIKeyError
        if response.status_code == 429:  # noqa: PLR2004
            detail = "Too many requests."
            with contextlib.suppress(Exception):
                detail = response.json()["detail"]["error"]

            raise UsageLimitExceededError(detail)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    async def extract(
        self,
        urls: list[str] | str,  # Accept a list of URLs or a single URL
        **kwargs: Any,  # Accept custom arguments
    ) -> dict[str, Any]:
        """Combined extract method."""
        response_dict = await self._extract(urls, **kwargs)
        response_dict["results"] = response_dict.get("results", [])
        response_dict["failed_results"] = response_dict.get("failed_results", [])
        return response_dict

    async def get_search_context(
        self,
        query: str,
        search_depth: SearchDepth = "basic",
        topic: Topic = "general",
        days: int = 3,
        max_results: int = 5,
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        max_tokens: int = 4000,
        **kwargs: Any,  # Accept custom arguments
    ) -> str:
        """Get the search context for a query.

        Useful for getting only related content from retrieved websites
        without having to deal with context extraction and limitation yourself.

        max_tokens: The max number of tokens to return (based on openai token compute).
        Defaults to 4000.

        Returns a string of JSON containing the search context up to context limit.
        """
        import anyenv

        response_dict = await self._search(
            query,
            search_depth=search_depth,
            topic=topic,
            days=days,
            max_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_answer=False,
            include_raw_content=False,
            include_images=False,
            **kwargs,
        )
        sources = response_dict.get("results", [])
        context = [{"url": s["url"], "content": s["content"]} for s in sources]
        items = get_max_items_from_list(context, max_tokens)
        return anyenv.dump_json(items)

    async def qna_search(
        self,
        query: str,
        search_depth: SearchDepth = "advanced",
        topic: Topic = "general",
        days: int = 3,
        max_results: int = 5,
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        **kwargs: Any,  # Accept custom arguments
    ) -> str:
        """Q&A search. Search depth is advanced by default to get the best answer."""
        response_dict = await self._search(
            query,
            search_depth=search_depth,
            topic=topic,
            days=days,
            max_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_raw_content=False,
            include_images=False,
            include_answer=True,
            **kwargs,
        )
        return response_dict.get("answer", "")  # type: ignore[no-any-return]


if __name__ == "__main__":
    import asyncio

    async def example() -> None:
        """Example usage of SerperTool."""
        client = AsyncTavilyClient()
        results = await client.search("Python programming")
        print(results)

    asyncio.run(example())
