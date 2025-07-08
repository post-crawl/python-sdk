"""
Tests for PostCrawl types.
"""

import pytest
from pydantic import ValidationError

from postcrawl.types import (
    ExtractedPost,
    ExtractRequest,
    SearchAndExtractRequest,
    SearchRequest,
    SocialPost,
)


class TestRequestTypes:
    """Test request type validation."""

    def test_extract_request_validation(self):
        """Test ExtractRequest validation."""
        # Valid request
        request = ExtractRequest(
            urls=["https://reddit.com/test"],
            include_comments=True,
            response_mode="markdown",
        )
        assert len(request.urls) == 1
        assert request.include_comments is True
        assert request.response_mode == "markdown"

        # Invalid - empty URLs
        with pytest.raises(ValidationError):
            ExtractRequest(urls=[])

        # Invalid - too many URLs
        with pytest.raises(ValidationError):
            ExtractRequest(urls=["https://test.com"] * 101)  # Max is 100

        # Invalid - bad URL format
        with pytest.raises(ValidationError):
            ExtractRequest(urls=["not-a-url"])

    def test_search_request_validation(self):
        """Test SearchRequest validation."""
        # Valid request
        request = SearchRequest(
            social_platforms=["reddit", "tiktok"],
            query="test query",
            results=50,
            page=2,
        )
        assert len(request.social_platforms) == 2
        assert request.query == "test query"
        assert request.results == 50
        assert request.page == 2

        # Invalid - empty platforms
        with pytest.raises(ValidationError):
            SearchRequest(
                social_platforms=[],
                query="test",
                results=10,
                page=1,
            )

        # Invalid - empty query
        with pytest.raises(ValidationError):
            SearchRequest(
                social_platforms=["reddit"],
                query="",
                results=10,
                page=1,
            )

        # Invalid - results out of range
        with pytest.raises(ValidationError):
            SearchRequest(
                social_platforms=["reddit"],
                query="test",
                results=101,  # Max is 100
                page=1,
            )

        # Invalid - zero results
        with pytest.raises(ValidationError):
            SearchRequest(
                social_platforms=["reddit"],
                query="test",
                results=0,
                page=1,
            )

        # Invalid - zero page
        with pytest.raises(ValidationError):
            SearchRequest(
                social_platforms=["reddit"],
                query="test",
                results=10,
                page=0,
            )

    def test_search_and_extract_request_validation(self):
        """Test SearchAndExtractRequest validation."""
        # Valid request with all fields
        request = SearchAndExtractRequest(
            social_platforms=["reddit"],
            query="machine learning",
            results=25,
            page=1,
            include_comments=True,
            response_mode="markdown",
        )
        assert request.social_platforms == ["reddit"]
        assert request.include_comments is True
        assert request.response_mode == "markdown"

        # Valid request with optional fields omitted
        request = SearchAndExtractRequest(
            social_platforms=["tiktok"],
            query="AI",
            results=10,
            page=1,
        )
        assert request.include_comments is False  # Default value
        assert request.response_mode == "raw"  # Default value


class TestResponseTypes:
    """Test response type models."""

    def test_extracted_post_model(self):
        """Test ExtractedPost model."""
        # Valid post
        post = ExtractedPost(
            url="https://reddit.com/test",
            source="reddit",
            raw={"content": "Raw content here"},
            markdown="# Markdown content",
        )
        assert post.url == "https://reddit.com/test"
        assert post.source == "reddit"
        assert post.platform == "reddit"  # Test backward compatibility alias
        assert post.error is None

        # Post with error
        post = ExtractedPost(
            url="https://reddit.com/test",
            source="reddit",
            raw=None,
            markdown=None,
            error="Failed to extract",
        )
        assert post.error == "Failed to extract"

    def test_social_post_model(self):
        """Test SocialPost model."""
        # Valid post
        post = SocialPost(
            id="reddit-123-0",
            title="Test Post Title",
            author="testuser",
            upvotes=100,
            comments=25,
            created_at="2024-01-01T00:00:00Z",
            url="https://reddit.com/r/test/123",
            social_source="reddit",
        )
        assert post.id == "reddit-123-0"
        assert post.title == "Test Post Title"
        assert post.social_source == "reddit"

        # Invalid social source
        with pytest.raises(ValidationError):
            SocialPost(
                id="test-123",
                title="Test",
                author="user",
                upvotes=0,
                comments=0,
                created_at="2024-01-01T00:00:00Z",
                url="https://test.com",
                social_source="facebook",  # Not supported
            )
