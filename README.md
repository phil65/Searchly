# Searchly

[![PyPI License](https://img.shields.io/pypi/l/searchly.svg)](https://pypi.org/project/searchly/)
[![Package status](https://img.shields.io/pypi/status/searchly.svg)](https://pypi.org/project/searchly/)
[![Monthly downloads](https://img.shields.io/pypi/dm/searchly.svg)](https://pypi.org/project/searchly/)
[![Distribution format](https://img.shields.io/pypi/format/searchly.svg)](https://pypi.org/project/searchly/)
[![Wheel availability](https://img.shields.io/pypi/wheel/searchly.svg)](https://pypi.org/project/searchly/)
[![Python version](https://img.shields.io/pypi/pyversions/searchly.svg)](https://pypi.org/project/searchly/)
[![Implementation](https://img.shields.io/pypi/implementation/searchly.svg)](https://pypi.org/project/searchly/)
[![Releases](https://img.shields.io/github/downloads/phil65/searchly/total.svg)](https://github.com/phil65/searchly/releases)
[![Github Contributors](https://img.shields.io/github/contributors/phil65/searchly)](https://github.com/phil65/searchly/graphs/contributors)
[![Github Discussions](https://img.shields.io/github/discussions/phil65/searchly)](https://github.com/phil65/searchly/discussions)
[![Github Forks](https://img.shields.io/github/forks/phil65/searchly)](https://github.com/phil65/searchly/forks)
[![Github Issues](https://img.shields.io/github/issues/phil65/searchly)](https://github.com/phil65/searchly/issues)
[![Github Issues](https://img.shields.io/github/issues-pr/phil65/searchly)](https://github.com/phil65/searchly/pulls)
[![Github Watchers](https://img.shields.io/github/watchers/phil65/searchly)](https://github.com/phil65/searchly/watchers)
[![Github Stars](https://img.shields.io/github/stars/phil65/searchly)](https://github.com/phil65/searchly/stars)
[![Github Repository size](https://img.shields.io/github/repo-size/phil65/searchly)](https://github.com/phil65/searchly)
[![Github last commit](https://img.shields.io/github/last-commit/phil65/searchly)](https://github.com/phil65/searchly/commits)
[![Github release date](https://img.shields.io/github/release-date/phil65/searchly)](https://github.com/phil65/searchly/releases)
[![Github language count](https://img.shields.io/github/languages/count/phil65/searchly)](https://github.com/phil65/searchly)
[![Github commits this month](https://img.shields.io/github/commit-activity/m/phil65/searchly)](https://github.com/phil65/searchly)
[![Package status](https://codecov.io/gh/phil65/searchly/branch/main/graph/badge.svg)](https://codecov.io/gh/phil65/searchly/)
[![PyUp](https://pyup.io/repos/github/phil65/searchly/shield.svg)](https://pyup.io/repos/github/phil65/searchly/)

[Read the documentation!](https://phil65.github.io/Searchly/)

Searchly gives AI agents (and anyone else) one async interface to many web and news search
APIs. Every provider returns the same pydantic result models, so switching from Serper to
Tavily or Brave is a one-line change.

## Installation

```bash
pip install searchly
# optional SDK-based providers
pip install "searchly[exa]"                         # Exa
pip install "searchly[brave_search_python_client]"  # Brave
pip install "searchly[all]"
```

Requires Python 3.13+.

## Quickstart

```python
import asyncio

from searchly import AsyncSerperClient


async def main() -> None:
    client = AsyncSerperClient()  # reads SERPER_API_KEY, or pass api_key="..."
    response = await client.web_search("python asyncio tutorial", max_results=5, country="US")
    for result in response.results:
        print(result.title, result.url)

    news = await client.news_search("open source AI", max_results=3)
    for item in news.results:
        print(item.published, item.source, item.title)


asyncio.run(main())
```

### Configuration-driven providers

`searchly_config` holds lightweight pydantic configs (a discriminated union on `type`) that
create providers lazily, which makes search backends easy to put into YAML/JSON settings:

```python
from pydantic import TypeAdapter

from searchly import WebSearchProviderConfig

config = TypeAdapter(WebSearchProviderConfig).validate_python({"type": "tavily"})
if config.is_configured():  # api_key field or TAVILY_API_KEY env var
    provider = config.get_provider()
```

## Providers

| Provider | Client | Web | News | API key env var |
| --- | --- | --- | --- | --- |
| Brave | `AsyncBraveSearch` | yes | yes | `BRAVE_API_KEY` |
| DataForSEO | `AsyncDataForSEOClient` | yes | yes | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` |
| Exa | `AsyncExaClient` | yes | | `EXA_API_KEY` |
| JigsawStack | `AsyncJigsawStackClient` | yes | | `JIGSAWSTACK_API_KEY` |
| Kagi | `AsyncKagiClient` | yes | | `KAGI_API_KEY` |
| LinkUp | `AsyncLinkUpClient` | yes | | `LINKUP_API_KEY` |
| Search1API | `AsyncSearch1API` | yes | | `SEARCH1API_KEY` |
| SerpAPI | `AsyncSerpAPIClient` | yes | yes | `SERPAPI_KEY` |
| Serper | `AsyncSerperClient` | yes | yes | `SERPER_API_KEY` |
| Tavily | `AsyncTavilyClient` | yes | yes | `TAVILY_API_KEY` |
| You.com | `AsyncYouClient` | yes | yes | `YOU_API_KEY` |

## Features

- **Common protocols**: `WebSearchProvider.web_search()` and `NewsSearchProvider.news_search()`
  with shared `query`, `max_results`, `country` and `language` arguments; provider-specific
  options are extra keyword arguments.
- **Unified results**: `WebSearchResponse` / `NewsSearchResponse` with `WebSearchResult`
  (`title`, `url`, `snippet`) and `NewsSearchResult` (adds `source`, `published`).
- **Typed**: `CountryCode` and `LanguageCode` literals, full type hints, `py.typed`.
- **Config models**: `WebSearchProviderConfig`, `NewsSearchProviderConfig`, `get_config_class()`
  for building providers from settings, with secrets stored as `SecretStr`.
