"""Unit tests for provider edge cases (no network, no API keys)."""

from typing import Any

import pytest


async def test_brave_clamps_max_results(monkeypatch: pytest.MonkeyPatch):
    """Brave's request models cap `count` (20 web, 50 news): larger values are clamped."""
    pytest.importorskip("brave_search_python_client")
    from searchly.providers.brave_provider.client import AsyncBraveSearch

    client = AsyncBraveSearch(api_key="test")
    seen: dict[str, Any] = {}

    class _Web:
        web = None

    class _News:
        results = ()

    async def fake_web(req: Any, **_: Any) -> _Web:
        seen["web"] = req.count
        return _Web()

    async def fake_news(req: Any, **_: Any) -> _News:
        seen["news"] = req.count
        return _News()

    monkeypatch.setattr(client.client, "web", fake_web)
    monkeypatch.setattr(client.client, "news", fake_news)
    await client.web_search("x", max_results=25)
    await client.news_search("x", max_results=80)
    assert seen == {"web": 20, "news": 50}


@pytest.mark.parametrize(
    "payload",
    [
        # task-level error (HTTP 200, result null)
        {
            "status_code": 20000,
            "status_message": "Ok.",
            "tasks": [
                {"status_code": 40200, "status_message": "Payment Required.", "result": None}
            ],
        },
        # request-level error
        {"status_code": 40100, "status_message": "You are not authorized.", "tasks": None},
    ],
)
@pytest.mark.parametrize("method", ["web_search", "news_search"])
async def test_dataforseo_raises_on_failed_task(
    monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any], method: str
):
    """A DataForSEO error status is raised, not returned as an empty result."""
    import anyenv

    from searchly.exceptions import SearchProviderError
    from searchly.providers.dataforseo_provider.dataforseo import AsyncDataForSEOClient

    async def fake_post_json(*_: Any, **__: Any) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(anyenv, "post_json", fake_post_json)
    client = AsyncDataForSEOClient(login="l", password="p")
    with pytest.raises(SearchProviderError, match=r"40200|40100"):
        await getattr(client, method)("x")


async def test_dataforseo_ok_without_items(monkeypatch: pytest.MonkeyPatch):
    """A successful task with no result still returns an empty response."""
    import anyenv

    from searchly.providers.dataforseo_provider.dataforseo import AsyncDataForSEOClient

    async def fake_post_json(*_: Any, **__: Any) -> dict[str, Any]:
        return {"status_code": 20000, "tasks": [{"status_code": 20000, "result": None}]}

    monkeypatch.setattr(anyenv, "post_json", fake_post_json)
    client = AsyncDataForSEOClient(login="l", password="p")
    assert (await client.web_search("x")).results == []


def test_is_configured_ignores_empty_env(monkeypatch: pytest.MonkeyPatch):
    """An exported but empty key doesn't count as configured (the client would reject it)."""
    from searchly_config.configs import BraveSearchConfig, DataForSEOConfig

    monkeypatch.setenv("BRAVE_API_KEY", "")
    monkeypatch.setenv("DATAFORSEO_LOGIN", "")
    monkeypatch.setenv("DATAFORSEO_PASSWORD", "")
    assert not BraveSearchConfig().is_configured()
    assert not DataForSEOConfig().is_configured()
