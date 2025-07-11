"""
Tests for PostCrawl client functionality.
"""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from postcrawl import PostCrawlClient
from postcrawl.exceptions import (
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    NetworkError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from postcrawl.types import ExtractedPost, SearchResult


class TestClientInitialization:
    """Test client initialization and configuration."""

    def test_valid_api_key(self, api_key):
        """Test initialization with valid API key."""
        client = PostCrawlClient(api_key=api_key)
        assert client.api_key == api_key
        assert client.base_url == "https://edge.postcrawl.com"
        assert client.timeout == 90.0
        assert client.max_retries == 3
        assert client.retry_delay == 1.0

    def test_invalid_api_key_format(self):
        """Test initialization with invalid API key format."""
        with pytest.raises(ValueError, match="API key must start with 'sk_'"):
            PostCrawlClient(api_key="invalid_key")

    def test_empty_api_key(self):
        """Test initialization with empty API key."""
        with pytest.raises(ValueError, match="API key is required"):
            PostCrawlClient(api_key="")

    def test_custom_parameters(self, api_key):
        """Test initialization with custom parameters."""
        client = PostCrawlClient(api_key=api_key, timeout=30.0, max_retries=5, retry_delay=2.0)
        assert client.timeout == 30.0
        assert client.max_retries == 5
        assert client.retry_delay == 2.0


class TestSearchEndpoint:
    """Test search endpoint functionality."""

    @pytest.mark.asyncio
    async def test_search_success(self, httpx_mock: HTTPXMock, api_key, mock_search_response):
        """Test successful search request."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/search",
            json=mock_search_response,
            status_code=200,
            headers={
                "X-RateLimit-Limit": "200",
                "X-RateLimit-Remaining": "199",
                "X-RateLimit-Reset": "1703725200",
            },
        )

        async with PostCrawlClient(api_key=api_key) as client:
            results = await client.search(
                social_platforms=["reddit"], query="machine learning", results=10, page=1
            )

        assert len(results) == 2
        assert isinstance(results[0], SearchResult)
        assert results[0].title == "Understanding Machine Learning Basics"
        assert results[0].url.startswith("https://www.reddit.com")
        assert "machine learning" in results[0].snippet.lower()
        assert results[0].date == "Dec 28, 2024"
        assert results[0].image_url == "https://preview.redd.it/ml-basics.jpg"

        # Check rate limit info was updated
        assert client.rate_limit_info["limit"] == 200
        assert client.rate_limit_info["remaining"] == 199

    @pytest.mark.asyncio
    async def test_search_empty_results(self, httpx_mock: HTTPXMock, api_key):
        """Test search with no results."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/search",
            json=[],
            status_code=200,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            results = await client.search(
                social_platforms=["reddit", "tiktok"],
                query="very specific query with no results",
                results=10,
                page=1,
            )

        assert results == []
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_validation_error(self, api_key):
        """Test search with invalid parameters."""
        async with PostCrawlClient(api_key=api_key) as client:
            with pytest.raises(ValidationError) as exc_info:
                await client.search(
                    social_platforms=[],
                    query="test",
                    results=10,
                    page=1,  # Empty list
                )

            assert "Invalid request parameters" in str(exc_info.value)
            assert exc_info.value.details[0].field == "social_platforms"

    @pytest.mark.asyncio
    async def test_search_authentication_error(self, httpx_mock: HTTPXMock, api_key):
        """Test search with authentication error."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/search",
            json={"error": "unauthorized", "message": "Invalid API key", "request_id": "req_123"},
            status_code=401,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            with pytest.raises(AuthenticationError) as exc_info:
                await client.search(social_platforms=["reddit"], query="test", results=10, page=1)

            assert exc_info.value.status_code == 401
            assert exc_info.value.request_id == "req_123"

    @pytest.mark.asyncio
    async def test_search_rate_limit_error(self, httpx_mock: HTTPXMock, api_key):
        """Test search with rate limit error."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/search",
            json={
                "error": "rate_limit_exceeded",
                "message": "Too many requests",
                "request_id": "req_456",
            },
            status_code=429,
            headers={"Retry-After": "60"},
        )

        async with PostCrawlClient(api_key=api_key) as client:
            with pytest.raises(RateLimitError) as exc_info:
                await client.search(social_platforms=["reddit"], query="test", results=10, page=1)

            assert exc_info.value.status_code == 429
            assert exc_info.value.retry_after == 60


class TestExtractEndpoint:
    """Test extract endpoint functionality."""

    @pytest.mark.asyncio
    async def test_extract_success(self, httpx_mock: HTTPXMock, api_key, mock_extract_response):
        """Test successful extract request."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/extract",
            json=mock_extract_response,
            status_code=200,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            results = await client.extract(
                urls=[
                    "https://www.reddit.com/r/Python/comments/1ab2c3d/test_post/",
                    "https://www.tiktok.com/@pythontutor/video/7123456789012345678",
                    "https://invalid.url/post",
                ],
                include_comments=True,
                response_mode="raw",
            )

        assert len(results) == 3

        # Check Reddit post
        reddit_post = results[0]
        assert isinstance(reddit_post, ExtractedPost)
        assert reddit_post.source == "reddit"
        assert reddit_post.raw is not None  # Has some data
        assert reddit_post.error is None

        # Check TikTok post
        tiktok_post = results[1]
        assert isinstance(tiktok_post, ExtractedPost)
        assert tiktok_post.source == "tiktok"
        assert tiktok_post.raw is not None  # Has some data
        assert tiktok_post.error is None

        # Check failed extraction
        failed_post = results[2]
        assert isinstance(failed_post, ExtractedPost)
        assert failed_post.source == "reddit"  # Changed to 'reddit' to match Literal type
        assert failed_post.raw is None
        assert failed_post.error == "Failed to extract content: Invalid URL"

    @pytest.mark.asyncio
    async def test_extract_with_markdown(self, httpx_mock: HTTPXMock, api_key):
        """Test extract with markdown response mode."""
        markdown_response = [
            {
                "url": "https://www.reddit.com/r/Python/comments/1ab2c3d/test_post/",
                "source": "reddit",
                "raw": None,
                "markdown": "# Test Post Title\\n\\nThis is the post content.",
                "error": None,
            }
        ]

        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/extract",
            json=markdown_response,
            status_code=200,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            results = await client.extract(
                urls=["https://www.reddit.com/r/Python/comments/1ab2c3d/test_post/"],
                response_mode="markdown",
            )

        assert len(results) == 1
        assert results[0].markdown == "# Test Post Title\\n\\nThis is the post content."
        assert results[0].raw is None

    @pytest.mark.asyncio
    async def test_extract_url_validation(self, api_key):
        """Test extract with invalid URLs."""
        async with PostCrawlClient(api_key=api_key) as client:
            with pytest.raises(ValidationError) as exc_info:
                await client.extract(urls=["not-a-valid-url"], include_comments=False)

            assert "Invalid request parameters" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_extract_insufficient_credits(self, httpx_mock: HTTPXMock, api_key):
        """Test extract with insufficient credits error."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/extract",
            json={
                "error": "insufficient_credits",
                "message": "Not enough credits. Required: 10, Available: 5",
                "request_id": "req_789",
            },
            status_code=403,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            with pytest.raises(InsufficientCreditsError) as exc_info:
                await client.extract(
                    urls=["https://www.reddit.com/r/Python/comments/1ab2c3d/test/"]
                )

            assert exc_info.value.status_code == 403
            assert "Not enough credits" in str(exc_info.value)


class TestSearchAndExtractEndpoint:
    """Test search-and-extract endpoint functionality."""

    @pytest.mark.asyncio
    async def test_search_and_extract_success(
        self, httpx_mock: HTTPXMock, api_key, mock_extract_response
    ):
        """Test successful search-and-extract request."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/search-and-extract",
            json=mock_extract_response[:2],  # Return first 2 items
            status_code=200,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            results = await client.search_and_extract(
                social_platforms=["reddit", "tiktok"],
                query="python tutorial",
                results=10,
                page=1,
                include_comments=True,
                response_mode="raw",
            )

        assert len(results) == 2
        assert all(isinstance(post, ExtractedPost) for post in results)
        assert results[0].source == "reddit"
        assert results[1].source == "tiktok"


class TestNetworkAndRetry:
    """Test network errors and retry logic."""

    @pytest.mark.asyncio
    async def test_network_error_with_retry(self, httpx_mock: HTTPXMock, api_key):
        """Test network error triggers retry."""
        # First request fails with network error
        httpx_mock.add_exception(httpx.NetworkError("Connection failed"))

        # Second request succeeds
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/search",
            json=[],
            status_code=200,
        )

        async with PostCrawlClient(api_key=api_key, retry_delay=0.1) as client:
            results = await client.search(
                social_platforms=["reddit"], query="test", results=10, page=1
            )

        assert results == []

    @pytest.mark.asyncio
    async def test_network_error_max_retries(self, httpx_mock: HTTPXMock, api_key):
        """Test network error after max retries."""
        # All requests fail
        for _ in range(4):  # 1 initial + 3 retries
            httpx_mock.add_exception(httpx.NetworkError("Connection failed"))

        async with PostCrawlClient(api_key=api_key, max_retries=3, retry_delay=0.01) as client:
            with pytest.raises(NetworkError) as exc_info:
                await client.search(social_platforms=["reddit"], query="test", results=10, page=1)

            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_error(self, httpx_mock: HTTPXMock, api_key):
        """Test timeout error handling."""
        httpx_mock.add_exception(httpx.TimeoutException("Request timed out"))

        async with PostCrawlClient(api_key=api_key) as client:
            with pytest.raises(TimeoutError) as exc_info:
                await client.search(social_platforms=["reddit"], query="test", results=10, page=1)

            assert isinstance(exc_info.value.original_error, httpx.TimeoutException)


class TestContextManager:
    """Test context manager functionality."""

    @pytest.mark.asyncio
    async def test_context_manager(self, httpx_mock: HTTPXMock, api_key):
        """Test client works as async context manager."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/search",
            json=[],
            status_code=200,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            assert client._client is None  # Client created on demand
            await client.search(social_platforms=["reddit"], query="test", results=10, page=1)
            assert client._client is not None  # Client created after first request

        # Client should be closed after context exit
        assert client._client is None

    @pytest.mark.asyncio
    async def test_manual_close(self, api_key):
        """Test manual client close."""
        client = PostCrawlClient(api_key=api_key)
        await client.close()  # Should not raise even if client not created

        # Create client
        _ = client._get_client()
        assert client._client is not None

        # Close client
        await client.close()
        assert client._client is None


class TestRateLimitInfo:
    """Test rate limit information tracking."""

    @pytest.mark.asyncio
    async def test_rate_limit_headers(
        self, httpx_mock: HTTPXMock, api_key, mock_rate_limit_headers
    ):
        """Test rate limit headers are properly parsed."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/search",
            json=[],
            status_code=200,
            headers=mock_rate_limit_headers,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            await client.search(social_platforms=["reddit"], query="test", results=10, page=1)

            assert client.rate_limit_info["limit"] == 200
            assert client.rate_limit_info["remaining"] == 150
            assert client.rate_limit_info["reset"] == 1703725200


class TestErrorResponseHandling:
    """Test various error response handling."""

    @pytest.mark.asyncio
    async def test_malformed_error_response(self, httpx_mock: HTTPXMock, api_key):
        """Test handling of malformed error responses."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/search",
            text="Internal Server Error",
            status_code=500,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            with pytest.raises(APIError) as exc_info:
                await client.search(social_platforms=["reddit"], query="test", results=10, page=1)

            assert exc_info.value.status_code == 500
            assert "Internal Server Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validation_error_with_details(self, httpx_mock: HTTPXMock, api_key):
        """Test validation error with field details."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge.postcrawl.com/v1/search",
            json={
                "error": "validation_error",
                "message": "Validation failed",
                "request_id": "req_val_123",
                "details": [
                    {
                        "field": "results",
                        "code": "invalid_value",
                        "message": "Must be between 1 and 100",
                    }
                ],
            },
            status_code=422,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            # First ensure the request doesn't fail client-side validation
            # by using valid parameters that the server will reject
            with pytest.raises(ValidationError) as exc_info:
                await client.search(
                    social_platforms=["reddit"],
                    query="test",
                    results=50,  # Valid for client, server will reject
                    page=1,
                )

            assert exc_info.value.status_code == 422
            assert len(exc_info.value.details) == 1
            assert exc_info.value.details[0].field == "results"
            assert exc_info.value.details[0].message == "Must be between 1 and 100"
