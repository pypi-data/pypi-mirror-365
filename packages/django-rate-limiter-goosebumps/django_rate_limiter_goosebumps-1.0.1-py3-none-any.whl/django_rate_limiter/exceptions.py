"""
Custom exceptions for Django Rate Limiter.
"""


class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded."""

    def __init__(
        self, message="Rate limit exceeded", retry_after=None, limit=None, window=None
    ):
        super().__init__(message)
        self.retry_after = retry_after
        self.limit = limit
        self.window = window

    def __str__(self):
        msg = super().__str__()
        if self.retry_after:
            msg += f" (retry after {self.retry_after} seconds)"
        if self.limit and self.window:
            msg += f" (limit: {self.limit} requests per {self.window} seconds)"
        return msg


class ConfigurationError(Exception):
    """Raised when there's a configuration error."""

    pass


class BackendError(Exception):
    """Raised when there's an error with the storage backend."""

    pass
