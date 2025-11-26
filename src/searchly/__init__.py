"""Searchly: Search tools for agents.

Provides unified search interfaces across multiple search providers.
"""

from __future__ import annotations

from importlib.metadata import version

from searchly.base import (
    CountryCode,
    LanguageCode,
    NewsSearchProvider,
    NewsSearchResponse,
    NewsSearchResult,
    WebSearchProvider,
    WebSearchResponse,
    WebSearchResult,
)
from searchly.config import (
    BaseSearchProviderConfig,
    BraveSearchConfig,
    DataForSEOConfig,
    ExaConfig,
    JigsawStackConfig,
    KagiConfig,
    LinkUpConfig,
    NewsSearchProviderConfig,
    NewsSearchProviderName,
    Search1Config,
    SerperConfig,
    SerpAPIConfig,
    TavilyConfig,
    WebSearchProviderConfig,
    WebSearchProviderName,
    YouConfig,
)
from searchly.providers.brave_provider.client import AsyncBraveSearch
from searchly.providers.dataforseo_provider.dataforseo import AsyncDataForSEOClient
from searchly.providers.exa_provider.exa import AsyncExaClient
from searchly.providers.jigsawstack_provider.jigsawstack import AsyncJigsawStackClient
from searchly.providers.kagi_provider.client import AsyncKagiClient
from searchly.providers.linkup_provider.client import AsyncLinkUpClient
from searchly.providers.search1_provider.client import AsyncSearch1API
from searchly.providers.serpapi_provider.client import AsyncSerpAPIClient
from searchly.providers.serper_provider.client import AsyncSerperClient
from searchly.providers.tavily_provider.client import AsyncTavilyClient
from searchly.providers.you_provider.you import AsyncYouClient


__version__ = version("searchly")
__title__ = "Searchly"

__author__ = "Philipp Temminghoff"
__author_email__ = "philipptemminghoff@googlemail.com"
__copyright__ = "Copyright (c) 2025 Philipp Temminghoff"
__license__ = "MIT"
__url__ = "https://github.com/phil65/searchly"

__all__ = [
    # Version
    "__version__",
    # Protocols
    "NewsSearchProvider",
    "WebSearchProvider",
    # Response models
    "NewsSearchResponse",
    "NewsSearchResult",
    "WebSearchResponse",
    "WebSearchResult",
    # Type literals
    "CountryCode",
    "LanguageCode",
    # Config base
    "BaseSearchProviderConfig",
    # Provider configs
    "BraveSearchConfig",
    "DataForSEOConfig",
    "ExaConfig",
    "JigsawStackConfig",
    "KagiConfig",
    "LinkUpConfig",
    "Search1Config",
    "SerperConfig",
    "SerpAPIConfig",
    "TavilyConfig",
    "YouConfig",
    # Config unions
    "NewsSearchProviderConfig",
    "WebSearchProviderConfig",
    # Provider name literals
    "NewsSearchProviderName",
    "WebSearchProviderName",
    # Clients
    "AsyncBraveSearch",
    "AsyncDataForSEOClient",
    "AsyncExaClient",
    "AsyncJigsawStackClient",
    "AsyncKagiClient",
    "AsyncLinkUpClient",
    "AsyncSearch1API",
    "AsyncSerpAPIClient",
    "AsyncSerperClient",
    "AsyncTavilyClient",
    "AsyncYouClient",
]
