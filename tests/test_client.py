"""
Tests for PostCrawl client.
"""

import pytest
from pytest_httpx import HTTPXMock

from postcrawl import (
    AuthenticationError,
    InsufficientCreditsError,
    PostCrawlClient,
    RateLimitError,
    ValidationError,
)


@pytest.fixture
def api_key():
    """Test API key."""
    return "sk_test_123456789"


@pytest.fixture
def client(api_key):
    """Create a test client."""
    return PostCrawlClient(api_key=api_key)


class TestPostCrawlClient:
    """Test PostCrawl client functionality."""

    def test_client_initialization(self):
        """Test client initialization."""
        # Valid API key
        client = PostCrawlClient(api_key="sk_test")
        assert client.api_key == "sk_test"

        # Invalid API key format
        with pytest.raises(ValueError, match="API key must start with 'sk_'"):
            PostCrawlClient(api_key="invalid_key")

        # Missing API key
        with pytest.raises(ValueError, match="API key is required"):
            PostCrawlClient(api_key="")

    @pytest.mark.asyncio
    async def test_search_success(self, client, httpx_mock: HTTPXMock):
        """Test successful search request."""
        # Mock response
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search",
            json=[
                {
                    "id": "reddit-123-0",
                    "title": "Test Post",
                    "author": "testuser",
                    "upvotes": 100,
                    "comments": 25,
                    "created_at": "2024-01-01T00:00:00Z",
                    "url": "https://reddit.com/r/test/123",
                    "social_source": "reddit",
                }
            ],
        )

        # Make request
        results = await client.search(
            social_platforms=["reddit"],
            query="test query",
            results=10,
            page=1,
        )

        # Verify results
        assert len(results) == 1
        assert results[0].id == "reddit-123-0"
        assert results[0].title == "Test Post"
        assert results[0].social_source == "reddit"

    @pytest.mark.asyncio
    async def test_extract_success(self, client, httpx_mock: HTTPXMock):
        """Test successful extract request."""
        # Mock response
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/extract",
            json=[
                {
                    "url": "https://reddit.com/r/test/123",
                    "source": "reddit",  # API returns 'source' not 'platform'
                    "raw": {"content": "Raw content", "title": "Test Post"},
                    "markdown": "# Markdown content",
                }
            ],
        )

        # Make request
        results = await client.extract(
            urls=["https://reddit.com/r/test/123"],
            include_comments=True,
            response_mode="markdown",
        )

        # Verify results
        assert len(results) == 1
        assert results[0].url == "https://reddit.com/r/test/123"
        assert results[0].source == "reddit"
        assert results[0].raw == {"content": "Raw content", "title": "Test Post"}
        assert results[0].markdown == "# Markdown content"

    @pytest.mark.asyncio
    async def test_authentication_error(self, client, httpx_mock: HTTPXMock):
        """Test authentication error handling."""
        # Mock 401 response
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search",
            status_code=401,
            json={
                "error": "unauthorized",
                "message": "Invalid API key",
                "request_id": "req_123",
            },
        )

        # Make request and expect error
        with pytest.raises(AuthenticationError) as exc_info:
            await client.search(
                social_platforms=["reddit"],
                query="test",
                results=10,
                page=1,
            )

        assert exc_info.value.message == "Invalid API key"
        assert exc_info.value.request_id == "req_123"
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_insufficient_credits_error(self, client, httpx_mock: HTTPXMock):
        """Test insufficient credits error handling."""
        # Mock 403 response
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/extract",
            status_code=403,
            json={
                "error": "insufficient_credits",
                "message": "Insufficient credits for this operation",
                "request_id": "req_456",
            },
        )

        # Make request and expect error
        with pytest.raises(InsufficientCreditsError) as exc_info:
            await client.extract(urls=["https://reddit.com/test"])

        assert exc_info.value.message == "Insufficient credits for this operation"
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, client, httpx_mock: HTTPXMock):
        """Test rate limit error handling."""
        # Mock 429 response
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search",
            status_code=429,
            json={
                "error": "rate_limit_exceeded",
                "message": "Rate limit exceeded",
            },
            headers={
                "Retry-After": "60",
            },
        )

        # Make request and expect error
        with pytest.raises(RateLimitError) as exc_info:
            await client.search(
                social_platforms=["reddit"],
                query="test",
                results=10,
                page=1,
            )

        assert exc_info.value.message == "Rate limit exceeded"
        assert exc_info.value.retry_after == 60
        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_validation_error(self, client):
        """Test validation error handling."""
        # Test client-side validation (Pydantic will catch this before API call)
        with pytest.raises(ValidationError) as exc_info:
            await client.search(
                social_platforms=["reddit"],
                query="test",
                results=200,  # Invalid - exceeds max of 100
                page=1,
            )

        # Check that it's a Pydantic validation error
        assert "Invalid request parameters" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_and_extract_success(self, client, httpx_mock: HTTPXMock):
        """Test successful search and extract request."""
        # Mock response
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search-and-extract",
            json=[
                {
                    "url": "https://reddit.com/r/test/123",
                    "source": "reddit",  # API returns 'source' not 'platform'
                    "raw": {"content": "Found content"},
                    "markdown": "# Found content",
                }
            ],
        )

        # Make request
        results = await client.search_and_extract(
            social_platforms=["reddit"],
            query="test query",
            results=5,
            page=1,
            include_comments=False,
        )

        # Verify results
        assert len(results) == 1
        assert results[0].source == "reddit"
        assert results[0].raw == {"content": "Found content"}

    @pytest.mark.asyncio
    async def test_context_manager(self, api_key):
        """Test client as async context manager."""
        async with PostCrawlClient(api_key=api_key) as client:
            assert client._client is None  # Not created until first request

        # Client should be closed after context
        assert client._client is None

    def test_sync_methods(self, client, httpx_mock: HTTPXMock):
        """Test synchronous convenience methods."""
        # Mock response
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search",
            json=[
                {
                    "id": "test-123",
                    "title": "Sync Test",
                    "author": "user",
                    "upvotes": 10,
                    "comments": 5,
                    "created_at": "2024-01-01T00:00:00Z",
                    "url": "https://reddit.com/test",
                    "social_source": "reddit",
                }
            ],
        )

        # Use sync method
        results = client.search_sync(
            social_platforms=["reddit"],
            query="test",
            results=1,
            page=1,
        )

        assert len(results) == 1
        assert results[0].title == "Sync Test"
