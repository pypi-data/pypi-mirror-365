class OpenMarketsException(Exception):
    """Base class for all custom exceptions in OpenMarkets."""

    pass


class APIError(OpenMarketsException):
    """Raised for API related errors."""

    pass


class InvalidSymbolError(OpenMarketsException):
    """Raised for invalid symbols."""

    pass
