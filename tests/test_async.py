"""
Tests for async/sync method functionality.
"""

import asyncio

import httpx
import pytest
from pytest_httpx import HTTPXMock

from postcrawl import PostCrawlClient
from postcrawl.exceptions import TimeoutError


class TestAsyncMethods:
    """Test async method functionality."""

    @pytest.mark.asyncio
    async def test_async_search(self, httpx_mock: HTTPXMock, api_key, mock_search_response):
        """Test async search method."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search",
            json=mock_search_response,
            status_code=200,
        )

        client = PostCrawlClient(api_key=api_key)
        try:
            results = await client.search(
                social_platforms=["reddit"], query="test", results=10, page=1
            )
            assert len(results) == 2
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_async_extract(self, httpx_mock: HTTPXMock, api_key, mock_extract_response):
        """Test async extract method."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/extract",
            json=mock_extract_response,
            status_code=200,
        )

        client = PostCrawlClient(api_key=api_key)
        try:
            results = await client.extract(urls=["https://www.reddit.com/r/test/comments/123/"])
            assert len(results) == 3
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_async_search_and_extract(
        self, httpx_mock: HTTPXMock, api_key, mock_extract_response
    ):
        """Test async search_and_extract method."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search-and-extract",
            json=mock_extract_response[:2],
            status_code=200,
        )

        client = PostCrawlClient(api_key=api_key)
        try:
            results = await client.search_and_extract(
                social_platforms=["reddit", "tiktok"], query="test", results=10, page=1
            )
            assert len(results) == 2
        finally:
            await client.close()


class TestSyncMethods:
    """Test sync wrapper methods."""

    def test_sync_search(self, httpx_mock: HTTPXMock, api_key, mock_search_response):
        """Test sync search wrapper."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search",
            json=mock_search_response,
            status_code=200,
        )

        client = PostCrawlClient(api_key=api_key)
        results = client.search_sync(social_platforms=["reddit"], query="test", results=10, page=1)

        assert len(results) == 2
        assert results[0].title == "Understanding Machine Learning Basics"

    def test_sync_extract(self, httpx_mock: HTTPXMock, api_key, mock_extract_response):
        """Test sync extract wrapper."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/extract",
            json=mock_extract_response,
            status_code=200,
        )

        client = PostCrawlClient(api_key=api_key)
        results = client.extract_sync(
            urls=[
                "https://www.reddit.com/r/test/comments/123/",
                "https://www.tiktok.com/@user/video/456",
            ]
        )

        assert len(results) == 3
        assert results[0].source == "reddit"
        assert results[1].source == "tiktok"

    def test_sync_search_and_extract(self, httpx_mock: HTTPXMock, api_key, mock_extract_response):
        """Test sync search_and_extract wrapper."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search-and-extract",
            json=mock_extract_response[:2],
            status_code=200,
        )

        client = PostCrawlClient(api_key=api_key)
        results = client.search_and_extract_sync(
            social_platforms=["reddit", "tiktok"],
            query="python tutorial",
            results=10,
            page=1,
            include_comments=True,
        )

        assert len(results) == 2
        assert all(hasattr(post, "url") for post in results)


class TestAsyncContextManager:
    """Test async context manager functionality."""

    @pytest.mark.asyncio
    async def test_async_context_manager_success(self, httpx_mock: HTTPXMock, api_key):
        """Test using client as async context manager."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search",
            json=[],
            status_code=200,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            results = await client.search(
                social_platforms=["reddit"], query="test", results=10, page=1
            )
            assert results == []
            assert client._client is not None  # Client should be active

        # After context exit, client should be closed
        assert client._client is None

    @pytest.mark.asyncio
    async def test_async_context_manager_with_exception(self, httpx_mock: HTTPXMock, api_key):
        """Test context manager properly closes on exception."""
        httpx_mock.add_exception(Exception("Test error"))

        client = PostCrawlClient(api_key=api_key)

        with pytest.raises(Exception, match="Test error"):
            async with client:
                await client.search(social_platforms=["reddit"], query="test", results=10, page=1)

        # Client should still be closed after exception
        assert client._client is None

    @pytest.mark.asyncio
    async def test_multiple_requests_in_context(self, httpx_mock: HTTPXMock, api_key):
        """Test multiple requests within same context."""
        # Mock multiple responses
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search",
            json=[
                {
                    "title": "Result 1",
                    "url": "https://example.com/1",
                    "snippet": "Test",
                    "date": "Dec 28, 2024",
                    "imageUrl": "",  # This is correct - the API uses camelCase
                }
            ],
            status_code=200,
        )
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/extract",
            json=[
                {
                    "url": "https://example.com/1",
                    "source": "reddit",
                    "raw": None,  # Set to null instead of empty dict
                    "markdown": None,
                    "error": None,
                }
            ],
            status_code=200,
        )

        async with PostCrawlClient(api_key=api_key) as client:
            # First request
            search_results = await client.search(
                social_platforms=["reddit"], query="test", results=10, page=1
            )
            assert len(search_results) == 1

            # Second request using same client
            extract_results = await client.extract(urls=["https://example.com/1"])
            assert len(extract_results) == 1

            # Client should remain active between requests
            assert client._client is not None


class TestAsyncConcurrency:
    """Test concurrent async operations."""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, httpx_mock: HTTPXMock, api_key):
        """Test making concurrent requests."""
        # Mock responses for concurrent requests
        for i in range(3):
            httpx_mock.add_response(
                method="POST",
                url="https://edge-alpha.postcrawl.com/v1/search",
                json=[
                    {
                        "title": f"Result {i}",
                        "url": f"https://example.com/{i}",
                        "snippet": f"Test {i}",
                        "date": "Dec 28, 2024",
                        "imageUrl": "",
                    }
                ],
                status_code=200,
            )

        async with PostCrawlClient(api_key=api_key) as client:
            # Create concurrent tasks
            tasks = [
                client.search(social_platforms=["reddit"], query=f"query {i}", results=10, page=1)
                for i in range(3)
            ]

            # Execute concurrently
            results = await asyncio.gather(*tasks)

            assert len(results) == 3
            for i, result_list in enumerate(results):
                assert len(result_list) == 1
                assert result_list[0].title == f"Result {i}"

    def test_sync_method_outside_async_context(self, httpx_mock: HTTPXMock, api_key):
        """Test that sync methods work outside async context."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search",
            json=[],
            status_code=200,
        )

        client = PostCrawlClient(api_key=api_key)

        # This should work in a regular sync context
        results = client.search_sync(social_platforms=["reddit"], query="test", results=10, page=1)

        assert results == []


class TestAsyncErrorHandling:
    """Test error handling in async context."""

    @pytest.mark.asyncio
    async def test_async_network_error_retry(self, httpx_mock: HTTPXMock, api_key):
        """Test network error retry in async context."""
        # First request fails with httpx NetworkError
        httpx_mock.add_exception(httpx.NetworkError("Connection failed"))

        # Retry succeeds
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/search",
            json=[],
            status_code=200,
        )

        async with PostCrawlClient(api_key=api_key, retry_delay=0.01) as client:
            results = await client.search(
                social_platforms=["reddit"], query="test", results=10, page=1
            )
            assert results == []

    @pytest.mark.asyncio
    async def test_async_timeout_handling(self, httpx_mock: HTTPXMock, api_key):
        """Test timeout handling in async operations."""
        import httpx

        httpx_mock.add_exception(httpx.TimeoutException("Request timed out"))

        async with PostCrawlClient(api_key=api_key, timeout=1.0) as client:
            with pytest.raises(TimeoutError):
                await client.search(social_platforms=["reddit"], query="test", results=10, page=1)
