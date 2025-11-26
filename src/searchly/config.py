"""Search provider configuration."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import ConfigDict, Field, SecretStr
from schemez import Schema


if TYPE_CHECKING:
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


class BaseSearchProviderConfig(Schema):
    """Base search provider configuration."""

    type: str = Field(init=False)
    """Search provider type."""

    model_config = ConfigDict(use_attribute_docstrings=True, extra="forbid")

    def is_configured(self) -> bool:
        """Check if the provider has required credentials configured.

        Returns:
            True if credentials are set via field or environment variable.
        """
        raise NotImplementedError


class BraveSearchConfig(BaseSearchProviderConfig):
    """Brave Search provider configuration.

    Uses the Brave Search API for web and news search.
    Supports country and language filtering.
    """

    type: Literal["brave"] = Field("brave", init=False)

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="Brave Search API key. Defaults to BRAVE_API_KEY env var.",
    )
    """Brave Search API key."""

    retries: int = Field(
        default=0,
        ge=0,
        title="Retries",
        examples=[0, 3, 5],
    )
    """Number of retries for failed requests."""

    wait_time: int = Field(
        default=2,
        ge=0,
        title="Wait Time",
        examples=[1, 2, 5],
    )
    """Time to wait between retries in seconds."""

    def is_configured(self) -> bool:
        """Check if Brave Search credentials are configured."""
        return self.api_key is not None or os.getenv("BRAVE_API_KEY") is not None

    def get_provider(self) -> AsyncBraveSearch:
        """Create Brave Search provider instance."""
        from searchly.providers.brave_provider.client import AsyncBraveSearch

        api_key = self.api_key.get_secret_value() if self.api_key else None
        return AsyncBraveSearch(
            api_key=api_key,
            retries=self.retries,
            wait_time=self.wait_time,
        )


class DataForSEOConfig(BaseSearchProviderConfig):
    """DataForSEO provider configuration.

    Uses the DataForSEO API for web and news search.
    Supports country and language filtering with device/OS options.
    """

    type: Literal["dataforseo"] = Field("dataforseo", init=False)

    login: SecretStr | None = Field(
        default=None,
        title="Login",
        description="DataForSEO login. Defaults to DATAFORSEO_LOGIN env var.",
    )
    """DataForSEO login."""

    password: SecretStr | None = Field(
        default=None,
        title="Password",
        description="DataForSEO password. Defaults to DATAFORSEO_PASSWORD env var.",
    )
    """DataForSEO password."""

    base_url: str = Field(
        default="https://api.dataforseo.com/v3",
        title="Base URL",
    )
    """Base URL for the API."""

    def is_configured(self) -> bool:
        """Check if DataForSEO credentials are configured."""
        has_login = self.login is not None or os.getenv("DATAFORSEO_LOGIN") is not None
        has_password = self.password is not None or os.getenv("DATAFORSEO_PASSWORD") is not None
        return has_login and has_password

    def get_provider(self) -> AsyncDataForSEOClient:
        """Create DataForSEO provider instance."""
        from searchly.providers.dataforseo_provider.dataforseo import AsyncDataForSEOClient

        login = self.login.get_secret_value() if self.login else None
        password = self.password.get_secret_value() if self.password else None
        return AsyncDataForSEOClient(
            login=login,
            password=password,
            base_url=self.base_url,
        )


class ExaConfig(BaseSearchProviderConfig):
    """Exa provider configuration.

    Uses the Exa API for neural/semantic web search.
    Supports domain filtering and date ranges but not country/language.
    """

    type: Literal["exa"] = Field("exa", init=False)

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="Exa API key. Defaults to EXA_API_KEY env var.",
    )
    """Exa API key."""

    def is_configured(self) -> bool:
        """Check if Exa credentials are configured."""
        return self.api_key is not None or os.getenv("EXA_API_KEY") is not None

    def get_provider(self) -> AsyncExaClient:
        """Create Exa provider instance."""
        from searchly.providers.exa_provider.exa import AsyncExaClient

        api_key = self.api_key.get_secret_value() if self.api_key else None
        return AsyncExaClient(api_key=api_key)


class JigsawStackConfig(BaseSearchProviderConfig):
    """JigsawStack provider configuration.

    Uses the JigsawStack API for web search with AI overview.
    Limited filtering options.
    """

    type: Literal["jigsawstack"] = Field("jigsawstack", init=False)

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="JigsawStack API key. Defaults to JIGSAWSTACK_API_KEY env var.",
    )
    """JigsawStack API key."""

    base_url: str = Field(
        default="https://api.jigsawstack.com/v1",
        title="Base URL",
    )
    """Base URL for the API."""

    def is_configured(self) -> bool:
        """Check if JigsawStack credentials are configured."""
        return self.api_key is not None or os.getenv("JIGSAWSTACK_API_KEY") is not None

    def get_provider(self) -> AsyncJigsawStackClient:
        """Create JigsawStack provider instance."""
        from searchly.providers.jigsawstack_provider.jigsawstack import AsyncJigsawStackClient

        api_key = self.api_key.get_secret_value() if self.api_key else None
        return AsyncJigsawStackClient(api_key=api_key, base_url=self.base_url)


class KagiConfig(BaseSearchProviderConfig):
    """Kagi provider configuration.

    Uses the Kagi API for web and news search.
    Also supports summarization.
    """

    type: Literal["kagi"] = Field("kagi", init=False)

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="Kagi API key. Defaults to KAGI_API_KEY env var.",
    )
    """Kagi API key."""

    base_url: str = Field(
        default="https://kagi.com/api/v0",
        title="Base URL",
    )
    """Base URL for the API."""

    def is_configured(self) -> bool:
        """Check if Kagi credentials are configured."""
        return self.api_key is not None or os.getenv("KAGI_API_KEY") is not None

    def get_provider(self) -> AsyncKagiClient:
        """Create Kagi provider instance."""
        from searchly.providers.kagi_provider.client import AsyncKagiClient

        api_key = self.api_key.get_secret_value() if self.api_key else None
        return AsyncKagiClient(api_key=api_key, base_url=self.base_url)


class LinkUpConfig(BaseSearchProviderConfig):
    """LinkUp provider configuration.

    Uses the LinkUp API for web search with sourced answers.
    Limited filtering options.
    """

    type: Literal["linkup"] = Field("linkup", init=False)

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="LinkUp API key. Defaults to LINKUP_API_KEY env var.",
    )
    """LinkUp API key."""

    base_url: str = Field(
        default="https://api.linkup.so/v1",
        title="Base URL",
    )
    """Base URL for the API."""

    def is_configured(self) -> bool:
        """Check if LinkUp credentials are configured."""
        return self.api_key is not None or os.getenv("LINKUP_API_KEY") is not None

    def get_provider(self) -> AsyncLinkUpClient:
        """Create LinkUp provider instance."""
        from searchly.providers.linkup_provider.client import AsyncLinkUpClient

        api_key = self.api_key.get_secret_value() if self.api_key else None
        return AsyncLinkUpClient(api_key=api_key, base_url=self.base_url)


class Search1Config(BaseSearchProviderConfig):
    """Search1API provider configuration.

    Uses the Search1API for web search via Google or Bing.
    Supports language filtering and time ranges.
    """

    type: Literal["search1"] = Field("search1", init=False)

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="Search1API key. Defaults to SEARCH1API_KEY env var.",
    )
    """Search1API key."""

    base_url: str = Field(
        default="https://api.search1api.com",
        title="Base URL",
    )
    """Base URL for the API."""

    def is_configured(self) -> bool:
        """Check if Search1API credentials are configured."""
        return self.api_key is not None or os.getenv("SEARCH1API_KEY") is not None

    def get_provider(self) -> AsyncSearch1API:
        """Create Search1API provider instance."""
        from searchly.providers.search1_provider.client import AsyncSearch1API

        api_key = self.api_key.get_secret_value() if self.api_key else None
        return AsyncSearch1API(api_key=api_key, base_url=self.base_url)


class SerpAPIConfig(BaseSearchProviderConfig):
    """SerpAPI provider configuration.

    Uses SerpAPI for web and news search via Google.
    Full support for country, language, and location filtering.
    """

    type: Literal["serpapi"] = Field("serpapi", init=False)

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="SerpAPI key. Defaults to SERPAPI_KEY env var.",
    )
    """SerpAPI key."""

    def is_configured(self) -> bool:
        """Check if SerpAPI credentials are configured."""
        return self.api_key is not None or os.getenv("SERPAPI_KEY") is not None

    def get_provider(self) -> AsyncSerpAPIClient:
        """Create SerpAPI provider instance."""
        from searchly.providers.serpapi_provider.client import AsyncSerpAPIClient

        api_key = self.api_key.get_secret_value() if self.api_key else None
        return AsyncSerpAPIClient(api_key=api_key)


class SerperConfig(BaseSearchProviderConfig):
    """Serper provider configuration.

    Uses the Serper.dev API for web and news search via Google.
    Supports country, language, and location filtering.
    """

    type: Literal["serper"] = Field("serper", init=False)

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="Serper.dev API key. Defaults to SERPER_API_KEY env var.",
    )
    """Serper.dev API key."""

    base_url: str = Field(
        default="https://google.serper.dev",
        title="Base URL",
    )
    """Base URL for the API."""

    def is_configured(self) -> bool:
        """Check if Serper credentials are configured."""
        return self.api_key is not None or os.getenv("SERPER_API_KEY") is not None

    def get_provider(self) -> AsyncSerperClient:
        """Create Serper provider instance."""
        from searchly.providers.serper_provider.client import AsyncSerperClient

        api_key = self.api_key.get_secret_value() if self.api_key else None
        return AsyncSerperClient(api_key=api_key, base_url=self.base_url)


class TavilyConfig(BaseSearchProviderConfig):
    """Tavily provider configuration.

    Uses the Tavily API for web and news search.
    Supports domain filtering and search depth options.
    """

    type: Literal["tavily"] = Field("tavily", init=False)

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="Tavily API key. Defaults to TAVILY_API_KEY env var.",
    )
    """Tavily API key."""

    def is_configured(self) -> bool:
        """Check if Tavily credentials are configured."""
        return self.api_key is not None or os.getenv("TAVILY_API_KEY") is not None

    def get_provider(self) -> AsyncTavilyClient:
        """Create Tavily provider instance."""
        from searchly.providers.tavily_provider.client import AsyncTavilyClient

        api_key = self.api_key.get_secret_value() if self.api_key else None
        return AsyncTavilyClient(api_key=api_key)


class YouConfig(BaseSearchProviderConfig):
    """You.com provider configuration.

    Uses the You.com API for web and news search.
    Supports country, language, and freshness filtering.
    """

    type: Literal["you"] = Field("you", init=False)

    api_key: SecretStr | None = Field(
        default=None,
        title="API Key",
        description="You.com API key. Defaults to YOU_API_KEY env var.",
    )
    """You.com API key."""

    base_url: str = Field(
        default="https://api.ydc-index.io",
        title="Base URL",
    )
    """Base URL for the API."""

    def is_configured(self) -> bool:
        """Check if You.com credentials are configured."""
        return self.api_key is not None or os.getenv("YOU_API_KEY") is not None

    def get_provider(self) -> AsyncYouClient:
        """Create You.com provider instance."""
        from searchly.providers.you_provider.you import AsyncYouClient

        api_key = self.api_key.get_secret_value() if self.api_key else None
        return AsyncYouClient(api_key=api_key, base_url=self.base_url)


# Union type for web search provider configurations (all providers support web search)
WebSearchProviderConfig = Annotated[
    BraveSearchConfig
    | DataForSEOConfig
    | ExaConfig
    | JigsawStackConfig
    | KagiConfig
    | LinkUpConfig
    | Search1Config
    | SerpAPIConfig
    | SerperConfig
    | TavilyConfig
    | YouConfig,
    Field(discriminator="type"),
]

# Union type for news search provider configurations (subset that supports news)
NewsSearchProviderConfig = Annotated[
    BraveSearchConfig
    | DataForSEOConfig
    | KagiConfig
    | SerpAPIConfig
    | SerperConfig
    | TavilyConfig
    | YouConfig,
    Field(discriminator="type"),
]
