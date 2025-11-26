"""Base protocols and types for search providers."""

from __future__ import annotations

from typing import Any, Literal, Protocol, runtime_checkable

from schemez import Schema


# ISO 3166-1 alpha-2 country codes (common subset)
CountryCode = Literal[
    "AR",  # Argentina
    "AU",  # Australia
    "AT",  # Austria
    "BE",  # Belgium
    "BR",  # Brazil
    "CA",  # Canada
    "CL",  # Chile
    "CN",  # China
    "DK",  # Denmark
    "FI",  # Finland
    "FR",  # France
    "DE",  # Germany
    "HK",  # Hong Kong
    "IN",  # India
    "ID",  # Indonesia
    "IT",  # Italy
    "JP",  # Japan
    "KR",  # Korea
    "MY",  # Malaysia
    "MX",  # Mexico
    "NL",  # Netherlands
    "NZ",  # New Zealand
    "NO",  # Norway
    "PH",  # Philippines
    "PL",  # Poland
    "PT",  # Portugal
    "RU",  # Russia
    "SA",  # Saudi Arabia
    "ZA",  # South Africa
    "ES",  # Spain
    "SE",  # Sweden
    "CH",  # Switzerland
    "TW",  # Taiwan
    "TR",  # Turkey
    "GB",  # United Kingdom
    "US",  # United States
]

# ISO 639-1 language codes (common subset)
LanguageCode = Literal[
    "ar",  # Arabic
    "de",  # German
    "en",  # English
    "es",  # Spanish
    "fr",  # French
    "it",  # Italian
    "ja",  # Japanese
    "ko",  # Korean
    "nl",  # Dutch
    "pl",  # Polish
    "pt",  # Portuguese
    "ru",  # Russian
    "zh",  # Chinese
]

# DataForSEO uses numeric location codes
DATAFORSEO_COUNTRY_MAP: dict[str, int] = {
    "AR": 2032,
    "AU": 2036,
    "AT": 2040,
    "BE": 2056,
    "BR": 2076,
    "CA": 2124,
    "CL": 2152,
    "CN": 2156,
    "DK": 2208,
    "FI": 2246,
    "FR": 2250,
    "DE": 2276,
    "HK": 2344,
    "IN": 2356,
    "ID": 2360,
    "IT": 2380,
    "JP": 2392,
    "KR": 2410,
    "MY": 2458,
    "MX": 2484,
    "NL": 2528,
    "NZ": 2554,
    "NO": 2578,
    "PH": 2608,
    "PL": 2616,
    "PT": 2620,
    "RU": 2643,
    "SA": 2682,
    "ZA": 2710,
    "ES": 2724,
    "SE": 2752,
    "CH": 2756,
    "TW": 2158,
    "TR": 2792,
    "GB": 2826,
    "US": 2840,
}


class WebSearchResult(Schema):
    """Individual web search result."""

    title: str
    url: str
    snippet: str


class NewsSearchResult(Schema):
    """Individual news search result."""

    title: str
    url: str
    snippet: str
    source: str | None = None
    published: str | None = None


class WebSearchResponse(Schema):
    """Unified web search response."""

    results: list[WebSearchResult]


class NewsSearchResponse(Schema):
    """Unified news search response."""

    results: list[NewsSearchResult]


@runtime_checkable
class WebSearchProvider(Protocol):
    """Protocol for web search providers."""

    async def web_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Execute a web search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Country code for regional results.
            language: Language code for results.
            **kwargs: Provider-specific options.

        Returns:
            Unified web search response.
        """
        ...


@runtime_checkable
class NewsSearchProvider(Protocol):
    """Protocol for news search providers."""

    async def news_search(
        self,
        query: str,
        *,
        max_results: int = 10,
        country: CountryCode | None = None,
        language: LanguageCode | None = None,
        **kwargs: Any,
    ) -> NewsSearchResponse:
        """Execute a news search query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            country: Country code for regional results.
            language: Language code for results.
            **kwargs: Provider-specific options.

        Returns:
            Unified news search response.
        """
        ...
