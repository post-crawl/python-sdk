"""
Tests for PostCrawl exception handling.
"""

import httpx
import pytest

from postcrawl.exceptions import (
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    NetworkError,
    PostCrawlError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from postcrawl.types import ErrorDetail


class TestExceptionHierarchy:
    """Test exception inheritance and basic functionality."""

    def test_base_exception(self):
        """Test PostCrawlError base exception."""
        exc = PostCrawlError("Test error", request_id="req_123", response={"status": "error"})

        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.request_id == "req_123"
        assert exc.response == {"status": "error"}
        assert isinstance(exc, Exception)

    def test_api_error(self):
        """Test APIError with status code."""
        exc = APIError("API error occurred", status_code=500, request_id="req_456", response=None)

        assert exc.message == "API error occurred"
        assert exc.status_code == 500
        assert exc.request_id == "req_456"
        assert isinstance(exc, PostCrawlError)

    def test_authentication_error(self):
        """Test AuthenticationError defaults."""
        exc = AuthenticationError()

        assert exc.message == "Invalid or missing API key"
        assert exc.status_code == 401
        assert isinstance(exc, APIError)

        # Test with custom message
        exc_custom = AuthenticationError("API key expired", request_id="req_auth_123")
        assert exc_custom.message == "API key expired"
        assert exc_custom.status_code == 401

    def test_insufficient_credits_error(self):
        """Test InsufficientCreditsError with credit info."""
        exc = InsufficientCreditsError(
            "Not enough credits",
            credits_required=100,
            credits_available=50,
            request_id="req_credits_123",
        )

        assert exc.message == "Not enough credits"
        assert exc.status_code == 403
        assert exc.credits_required == 100
        assert exc.credits_available == 50
        assert isinstance(exc, APIError)

    def test_rate_limit_error(self):
        """Test RateLimitError with retry info."""
        exc = RateLimitError("Rate limit exceeded", retry_after=60, request_id="req_rate_123")

        assert exc.message == "Rate limit exceeded"
        assert exc.status_code == 429
        assert exc.retry_after == 60
        assert isinstance(exc, APIError)

    def test_validation_error(self):
        """Test ValidationError with field details."""
        details = [
            ErrorDetail(field="query", code="required", message="Query is required"),
            ErrorDetail(
                field="results", code="out_of_range", message="Results must be between 1 and 100"
            ),
        ]

        exc = ValidationError("Validation failed", details=details, request_id="req_val_123")

        assert exc.message == "Validation failed"
        assert exc.status_code == 422
        assert len(exc.details) == 2
        assert exc.details[0].field == "query"
        assert exc.details[1].field == "results"
        assert isinstance(exc, APIError)

    def test_network_error(self):
        """Test NetworkError with original exception."""
        original = httpx.NetworkError("Connection refused")
        exc = NetworkError("Failed to connect to server", original_error=original)

        assert exc.message == "Failed to connect to server"
        assert exc.original_error == original
        assert isinstance(exc, PostCrawlError)
        assert not isinstance(exc, APIError)

    def test_timeout_error(self):
        """Test TimeoutError as NetworkError subclass."""
        original = httpx.TimeoutException("Request timed out")
        exc = TimeoutError(original_error=original)

        assert exc.message == "Request timed out"
        assert exc.original_error == original
        assert isinstance(exc, NetworkError)
        assert isinstance(exc, PostCrawlError)


class TestExceptionStringRepresentation:
    """Test exception string representations."""

    def test_exception_str(self):
        """Test string representation of exceptions."""
        exc = APIError("Something went wrong", status_code=500, request_id="req_123")

        assert str(exc) == "Something went wrong"

    def test_exception_with_details(self):
        """Test exception with additional context in string."""
        details = [
            ErrorDetail(
                field="social_platforms",
                code="invalid_value",
                message="Invalid platform: 'facebook'",
            )
        ]

        exc = ValidationError(
            "Invalid request parameters", details=details, request_id="req_val_456"
        )

        # The base message is used for string representation
        assert str(exc) == "Invalid request parameters"

        # But details are accessible
        assert len(exc.details) == 1
        assert exc.details[0].message == "Invalid platform: 'facebook'"


class TestExceptionContext:
    """Test exception context preservation."""

    def test_response_preservation(self):
        """Test that original response is preserved."""
        mock_response = httpx.Response(
            status_code=403,
            headers={"X-Request-ID": "req_789"},
            json={"error": "insufficient_credits"},
        )

        exc = InsufficientCreditsError("Insufficient credits for operation", response=mock_response)

        assert exc.response == mock_response
        assert exc.response.status_code == 403

    def test_request_id_propagation(self):
        """Test request ID is properly propagated."""
        exc = RateLimitError("Too many requests", retry_after=30, request_id="req_rate_limit_123")

        assert exc.request_id == "req_rate_limit_123"

    def test_chained_exceptions(self):
        """Test exception chaining preserves context."""
        original = ConnectionError("Network unreachable")

        try:
            raise NetworkError("Failed to reach API server", original_error=original)
        except NetworkError as e:
            assert e.original_error == original
            assert isinstance(e.original_error, ConnectionError)


class TestExceptionDefaults:
    """Test exception default values."""

    def test_authentication_error_defaults(self):
        """Test AuthenticationError default message."""
        exc = AuthenticationError()
        assert exc.message == "Invalid or missing API key"
        assert exc.status_code == 401
        assert exc.request_id is None
        assert exc.response is None

    def test_insufficient_credits_defaults(self):
        """Test InsufficientCreditsError defaults."""
        exc = InsufficientCreditsError()
        assert exc.message == "Insufficient credits"
        assert exc.status_code == 403
        assert exc.credits_required is None
        assert exc.credits_available is None

    def test_rate_limit_defaults(self):
        """Test RateLimitError defaults."""
        exc = RateLimitError()
        assert exc.message == "Rate limit exceeded"
        assert exc.status_code == 429
        assert exc.retry_after is None

    def test_timeout_defaults(self):
        """Test TimeoutError defaults."""
        exc = TimeoutError()
        assert exc.message == "Request timed out"
        assert exc.original_error is None

    def test_validation_error_empty_details(self):
        """Test ValidationError with no details."""
        exc = ValidationError("Validation failed")
        assert exc.message == "Validation failed"
        assert exc.status_code == 422
        assert exc.details == []


class TestExceptionUsagePatterns:
    """Test common exception usage patterns."""

    def test_catching_specific_exceptions(self):
        """Test catching specific exception types."""
        # Test catching authentication errors
        try:
            raise AuthenticationError("Invalid API key format")
        except AuthenticationError as e:
            assert e.status_code == 401
        except PostCrawlError:
            pytest.fail("Should catch AuthenticationError specifically")

    def test_catching_base_exception(self):
        """Test catching base PostCrawlError."""
        exceptions_to_test = [
            AuthenticationError(),
            InsufficientCreditsError(),
            RateLimitError(),
            ValidationError("Test"),
            NetworkError("Test"),
            TimeoutError(),
        ]

        for exc in exceptions_to_test:
            try:
                raise exc
            except PostCrawlError as e:
                assert isinstance(e, PostCrawlError)
            except Exception:
                pytest.fail(f"Should catch {type(exc).__name__} as PostCrawlError")

    def test_api_error_catching(self):
        """Test catching APIError for HTTP errors."""
        api_errors = [
            AuthenticationError(),
            InsufficientCreditsError(),
            RateLimitError(),
            ValidationError("Test"),
            APIError("General error", status_code=500),
        ]

        non_api_errors = [NetworkError("Test"), TimeoutError()]

        # API errors should be caught
        for exc in api_errors:
            try:
                raise exc
            except APIError as e:
                assert hasattr(e, "status_code")
            except Exception:
                pytest.fail(f"{type(exc).__name__} should be caught as APIError")

        # Non-API errors should not be caught
        for exc in non_api_errors:
            try:
                raise exc
            except APIError:
                pytest.fail(f"{type(exc).__name__} should not be caught as APIError")
            except PostCrawlError:
                pass  # Expected
