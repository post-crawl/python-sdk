"""
PostCrawl API exceptions.
"""

from typing import Any

from .types import ErrorDetail


class PostCrawlError(Exception):
    """Base exception for all PostCrawl errors."""

    def __init__(
        self,
        message: str,
        *,
        request_id: str | None = None,
        response: Any | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.request_id = request_id
        self.response = response


class APIError(PostCrawlError):
    """General API error."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        request_id: str | None = None,
        response: Any | None = None,
    ):
        super().__init__(message, request_id=request_id, response=response)
        self.status_code = status_code


class AuthenticationError(APIError):
    """Raised when API key is invalid or missing."""

    def __init__(
        self,
        message: str = "Invalid or missing API key",
        *,
        request_id: str | None = None,
        response: Any | None = None,
    ):
        super().__init__(
            message,
            status_code=401,
            request_id=request_id,
            response=response,
        )


class InsufficientCreditsError(APIError):
    """Raised when account has insufficient credits."""

    def __init__(
        self,
        message: str = "Insufficient credits",
        *,
        credits_required: int | None = None,
        credits_available: int | None = None,
        request_id: str | None = None,
        response: Any | None = None,
    ):
        super().__init__(
            message,
            status_code=403,
            request_id=request_id,
            response=response,
        )
        self.credits_required = credits_required
        self.credits_available = credits_available


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: int | None = None,
        request_id: str | None = None,
        response: Any | None = None,
    ):
        super().__init__(
            message,
            status_code=429,
            request_id=request_id,
            response=response,
        )
        self.retry_after = retry_after


class ValidationError(APIError):
    """Raised when request validation fails."""

    def __init__(
        self,
        message: str,
        *,
        details: list[ErrorDetail] | None = None,
        request_id: str | None = None,
        response: Any | None = None,
    ):
        super().__init__(
            message,
            status_code=422,
            request_id=request_id,
            response=response,
        )
        self.details = details or []


class NetworkError(PostCrawlError):
    """Raised when a network error occurs."""

    def __init__(
        self,
        message: str,
        *,
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.original_error = original_error


class TimeoutError(NetworkError):
    """Raised when a request times out."""

    def __init__(
        self,
        message: str = "Request timed out",
        *,
        original_error: Exception | None = None,
    ):
        super().__init__(message, original_error=original_error)
