"""Search provider configuration.

This is a lightweight config-only package for fast imports.
For the actual search providers, use `from searchly import ...`.
"""

from __future__ import annotations

from searchly_config.configs import (
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
    SerpAPIConfig,
    SerperConfig,
    TavilyConfig,
    WebSearchProviderConfig,
    WebSearchProviderName,
    YouConfig,
    get_config_class,
)


__all__ = [
    "BaseSearchProviderConfig",
    "BraveSearchConfig",
    "DataForSEOConfig",
    "ExaConfig",
    "JigsawStackConfig",
    "KagiConfig",
    "LinkUpConfig",
    "NewsSearchProviderConfig",
    "NewsSearchProviderName",
    "Search1Config",
    "SerpAPIConfig",
    "SerperConfig",
    "TavilyConfig",
    "WebSearchProviderConfig",
    "WebSearchProviderName",
    "YouConfig",
    "get_config_class",
]
