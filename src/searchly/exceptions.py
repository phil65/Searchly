"""Exceptions raised by search providers."""


class SearchProviderError(Exception):
    """Raised when a provider reports an error in an otherwise successful response."""


class UsageLimitExceededError(Exception):
    """Raised when the usage limit is exceeded."""


class BadRequestError(Exception):
    """Raised when the request is invalid."""


class InvalidAPIKeyError(Exception):
    def __init__(self) -> None:
        super().__init__("The provided API key is invalid.")


class MissingAPIKeyError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "No API key provided."
            " Please provide the api_key attribute or set the TAVILY_API_KEY env var."
        )
