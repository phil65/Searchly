"""Tavily API client class."""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
from typing import TYPE_CHECKING, Literal

from searchly.exceptions import (
    BadRequestError,
    InvalidAPIKeyError,
    MissingAPIKeyError,
    UsageLimitExceededError,
)


if TYPE_CHECKING:
    from collections.abc import Sequence

DEFAULT_MODEL_ENCODING = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 4000


def get_total_tokens_from_string(string: str, model: str = DEFAULT_MODEL_ENCODING) -> int:
    """Get total amount of tokens from string using the specified encoding."""
    import tokonomics

    return tokonomics.count_tokens(string, model=model)


def get_max_items_from_list(
    data: Sequence[dict], max_tokens: int = DEFAULT_MAX_TOKENS
) -> list[dict[str, str]]:
    """Get max items from list of items based on defined max tokens."""
    result = []
    current_tokens = 0
    for item in data:
        item_str = json.dumps(item)
        new_total_tokens = current_tokens + get_total_tokens_from_string(item_str)
        if new_total_tokens > max_tokens:
            break
        result.append(item)
        current_tokens = new_total_tokens
    return result


class AsyncTavilyClient:
    """Async Tavily API client class."""

    def __init__(
        self,
        api_key: str | None = None,
        company_info_tags: Sequence[str] = ("news", "general", "finance"),
    ):
        import httpx

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
        self._client_creator = lambda: httpx.AsyncClient(
            headers=self.headers,
            base_url=self.base_url,
            timeout=self.timeout,
        )
        self._company_info_tags = company_info_tags

    async def _search(
        self,
        query: str,
        search_depth: Literal["basic", "advanced"] = "basic",
        topic: str = "general",
        days: int = 3,
        max_results: int = 5,
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        include_answer: bool = False,
        include_raw_content: bool = False,
        include_images: bool = False,
        **kwargs,
    ) -> dict:
        """Internal search method to send the request to the API."""
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
            response = await client.post("/search", content=json.dumps(data))

        if response.status_code == 200:  # noqa: PLR2004
            return response.json()
        if response.status_code == 429:  # noqa: PLR2004
            detail = "Too many requests."
            with contextlib.suppress(Exception):
                detail = response.json()["detail"]["error"]

            raise UsageLimitExceededError(detail)
        if response.status_code == 401:  # noqa: PLR2004
            raise InvalidAPIKeyError
        response.raise_for_status()
        return response.json()

    async def search(
        self,
        query: str,
        search_depth: Literal["basic", "advanced"] = "basic",
        topic: Literal["general", "news"] = "general",
        days: int = 3,
        max_results: int = 5,
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        include_answer: bool = False,
        include_raw_content: bool = False,
        include_images: bool = False,
        **kwargs,  # Accept custom arguments
    ) -> dict:
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

        tavily_results = response_dict.get("results", [])

        response_dict["results"] = tavily_results

        return response_dict

    async def _extract(self, urls: list[str] | str, **kwargs) -> dict:
        """Internal extract method to send the request to the API."""
        data = {
            "urls": urls,
        }
        if kwargs:
            data.update(kwargs)

        async with self._client_creator() as client:
            response = await client.post("/extract", content=json.dumps(data))

        if response.status_code == 200:  # noqa: PLR2004
            return response.json()
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
        return response.json()

    async def extract(
        self,
        urls: list[str] | str,  # Accept a list of URLs or a single URL
        **kwargs,  # Accept custom arguments
    ) -> dict:
        """Combined extract method."""
        response_dict = await self._extract(
            urls,
            **kwargs,
        )

        tavily_results = response_dict.get("results", [])
        failed_results = response_dict.get("failed_results", [])

        response_dict["results"] = tavily_results
        response_dict["failed_results"] = failed_results

        return response_dict

    async def get_search_context(
        self,
        query: str,
        search_depth: Literal["basic", "advanced"] = "basic",
        topic: Literal["general", "news"] = "general",
        days: int = 3,
        max_results: int = 5,
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        max_tokens: int = 4000,
        **kwargs,  # Accept custom arguments
    ) -> str:
        """Get the search context for a query.

        Useful for getting only related content from retrieved websites
        without having to deal with context extraction and limitation yourself.

        max_tokens: The max number of tokens to return (based on openai token compute).
        Defaults to 4000.

        Returns a string of JSON containing the search context up to context limit.
        """
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
        context = [
            {"url": source["url"], "content": source["content"]} for source in sources
        ]
        return json.dumps(get_max_items_from_list(context, max_tokens))

    async def qna_search(
        self,
        query: str,
        search_depth: Literal["basic", "advanced"] = "advanced",
        topic: Literal["general", "news"] = "general",
        days: int = 3,
        max_results: int = 5,
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        **kwargs,  # Accept custom arguments
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
        return response_dict.get("answer", "")

    async def get_company_info(
        self,
        query: str,
        search_depth: Literal["basic", "advanced"] = "advanced",
        max_results: int = 5,
    ) -> Sequence[dict]:
        """Company information search method.

        Search depth is advanced by default to get the best answer.
        """

        async def _perform_search(topic: str):
            return await self._search(
                query,
                search_depth=search_depth,
                topic=topic,
                max_results=max_results,
                include_answer=False,
            )

        all_results = []
        for data in await asyncio.gather(*[
            _perform_search(topic) for topic in self._company_info_tags
        ]):
            if "results" in data:
                all_results.extend(data["results"])

        return sorted(all_results, key=lambda x: x["score"], reverse=True)[:max_results]


async def example():
    """Example usage of SerperTool."""
    client = AsyncTavilyClient()
    results = await client.search("Python programming")
    print(results)


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
