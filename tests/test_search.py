"""Integration tests for search providers."""

from __future__ import annotations

import os

import pytest

from searchly.base import NewsSearchResponse, WebSearchResponse


# Skip all tests in this module if not running integration tests
pytestmark = pytest.mark.integration


def has_env(*vars: str) -> bool:
    """Check if all environment variables are set."""
    return all(os.getenv(v) for v in vars)


# Web search providers with their required env vars
WEB_SEARCH_PROVIDERS = [
    pytest.param(
        "brave",
        marks=pytest.mark.skipif(not has_env("BRAVE_API_KEY"), reason="BRAVE_API_KEY not set"),
    ),
    pytest.param(
        "dataforseo",
        marks=pytest.mark.skipif(
            not has_env("DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD"),
            reason="DATAFORSEO credentials not set",
        ),
    ),
    pytest.param(
        "exa", marks=pytest.mark.skipif(not has_env("EXA_API_KEY"), reason="EXA_API_KEY not set")
    ),
    pytest.param(
        "jigsawstack",
        marks=pytest.mark.skipif(
            not has_env("JIGSAWSTACK_API_KEY"), reason="JIGSAWSTACK_API_KEY not set"
        ),
    ),
    pytest.param(
        "kagi", marks=pytest.mark.skipif(not has_env("KAGI_API_KEY"), reason="KAGI_API_KEY not set")
    ),
    pytest.param(
        "linkup",
        marks=pytest.mark.skipif(not has_env("LINKUP_API_KEY"), reason="LINKUP_API_KEY not set"),
    ),
    pytest.param(
        "search1",
        marks=pytest.mark.skipif(not has_env("SEARCH1API_KEY"), reason="SEARCH1API_KEY not set"),
    ),
    pytest.param(
        "serpapi",
        marks=pytest.mark.skipif(not has_env("SERPAPI_KEY"), reason="SERPAPI_KEY not set"),
    ),
    pytest.param(
        "serper",
        marks=pytest.mark.skipif(not has_env("SERPER_API_KEY"), reason="SERPER_API_KEY not set"),
    ),
    pytest.param(
        "tavily",
        marks=pytest.mark.skipif(not has_env("TAVILY_API_KEY"), reason="TAVILY_API_KEY not set"),
    ),
    pytest.param(
        "you", marks=pytest.mark.skipif(not has_env("YOU_API_KEY"), reason="YOU_API_KEY not set")
    ),
]

# News search providers (subset that supports news)
NEWS_SEARCH_PROVIDERS = [
    pytest.param(
        "brave",
        marks=pytest.mark.skipif(not has_env("BRAVE_API_KEY"), reason="BRAVE_API_KEY not set"),
    ),
    pytest.param(
        "dataforseo",
        marks=pytest.mark.skipif(
            not has_env("DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD"),
            reason="DATAFORSEO credentials not set",
        ),
    ),
    pytest.param(
        "serpapi",
        marks=pytest.mark.skipif(not has_env("SERPAPI_KEY"), reason="SERPAPI_KEY not set"),
    ),
    pytest.param(
        "serper",
        marks=pytest.mark.skipif(not has_env("SERPER_API_KEY"), reason="SERPER_API_KEY not set"),
    ),
    pytest.param(
        "tavily",
        marks=pytest.mark.skipif(not has_env("TAVILY_API_KEY"), reason="TAVILY_API_KEY not set"),
    ),
    pytest.param(
        "you", marks=pytest.mark.skipif(not has_env("YOU_API_KEY"), reason="YOU_API_KEY not set")
    ),
]


def get_web_provider(name: str):
    """Get a web search provider instance by name."""
    match name:
        case "brave":
            from searchly.providers.brave_provider.client import AsyncBraveSearch

            return AsyncBraveSearch()
        case "dataforseo":
            from searchly.providers.dataforseo_provider.dataforseo import AsyncDataForSEOClient

            return AsyncDataForSEOClient()
        case "exa":
            from searchly.providers.exa_provider.exa import AsyncExaClient

            return AsyncExaClient()
        case "jigsawstack":
            from searchly.providers.jigsawstack_provider.jigsawstack import AsyncJigsawStackClient

            return AsyncJigsawStackClient()
        case "kagi":
            from searchly.providers.kagi_provider.client import AsyncKagiClient

            return AsyncKagiClient()
        case "linkup":
            from searchly.providers.linkup_provider.client import AsyncLinkUpClient

            return AsyncLinkUpClient()
        case "search1":
            from searchly.providers.search1_provider.client import AsyncSearch1API

            return AsyncSearch1API()
        case "serpapi":
            from searchly.providers.serpapi_provider.client import AsyncSerpAPIClient

            return AsyncSerpAPIClient()
        case "serper":
            from searchly.providers.serper_provider.client import AsyncSerperClient

            return AsyncSerperClient()
        case "tavily":
            from searchly.providers.tavily_provider.client import AsyncTavilyClient

            return AsyncTavilyClient()
        case "you":
            from searchly.providers.you_provider.you import AsyncYouClient

            return AsyncYouClient()
        case _:
            msg = f"Unknown provider: {name}"
            raise ValueError(msg)


def get_news_provider(name: str):
    """Get a news search provider instance by name."""
    match name:
        case "brave":
            from searchly.providers.brave_provider.client import AsyncBraveSearch

            return AsyncBraveSearch()
        case "dataforseo":
            from searchly.providers.dataforseo_provider.dataforseo import AsyncDataForSEOClient

            return AsyncDataForSEOClient()
        case "serpapi":
            from searchly.providers.serpapi_provider.client import AsyncSerpAPIClient

            return AsyncSerpAPIClient()
        case "serper":
            from searchly.providers.serper_provider.client import AsyncSerperClient

            return AsyncSerperClient()
        case "tavily":
            from searchly.providers.tavily_provider.client import AsyncTavilyClient

            return AsyncTavilyClient()
        case "you":
            from searchly.providers.you_provider.you import AsyncYouClient

            return AsyncYouClient()
        case _:
            msg = f"Unknown provider: {name}"
            raise ValueError(msg)


@pytest.mark.parametrize("provider_name", WEB_SEARCH_PROVIDERS)
async def test_web_search(provider_name: str):
    """Test web search for each provider."""
    provider = get_web_provider(provider_name)
    result = await provider.web_search("Python programming", max_results=3)

    assert isinstance(result, WebSearchResponse)
    assert len(result.results) > 0
    for item in result.results:
        assert item.url
        assert item.title


@pytest.mark.parametrize("provider_name", NEWS_SEARCH_PROVIDERS)
async def test_news_search(provider_name: str):
    """Test news search for each provider."""
    provider = get_news_provider(provider_name)
    result = await provider.news_search("technology", max_results=3)

    assert isinstance(result, NewsSearchResponse)
    assert len(result.results) > 0
    for item in result.results:
        assert item.url
        assert item.title
