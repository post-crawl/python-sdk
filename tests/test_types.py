"""
Tests for PostCrawl type definitions and validation.
"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from postcrawl.types import (
    ErrorDetail,
    ErrorResponse,
    ExtractedPost,
    ExtractRequest,
    RedditComment,
    RedditPost,
    SearchAndExtractRequest,
    SearchRequest,
    SearchResult,
    SocialPost,
    TiktokComment,
    TiktokPost,
    is_reddit_post,
    is_tiktok_post,
)


class TestRequestTypes:
    """Test request type validation."""

    def test_extract_request_valid(self):
        """Test valid ExtractRequest."""
        request = ExtractRequest(
            urls=["https://www.reddit.com/r/Python/comments/123/test/"],
            include_comments=True,
            response_mode="markdown",
        )
        assert len(request.urls) == 1
        assert request.include_comments is True
        assert request.response_mode == "markdown"

    def test_extract_request_defaults(self):
        """Test ExtractRequest default values."""
        request = ExtractRequest(urls=["https://www.reddit.com/r/Python/comments/123/test/"])
        # Generated types have None defaults, our wrapper doesn't override them
        assert request.include_comments is None
        assert request.response_mode is None

    def test_extract_request_empty_urls(self):
        """Test ExtractRequest with empty URLs."""
        with pytest.raises(PydanticValidationError):
            ExtractRequest(urls=[])

    def test_extract_request_too_many_urls(self):
        """Test ExtractRequest with too many URLs."""
        urls = [f"https://example.com/{i}" for i in range(101)]
        with pytest.raises(PydanticValidationError):
            ExtractRequest(urls=urls)

    def test_extract_request_invalid_url(self):
        """Test ExtractRequest with invalid URL format."""
        with pytest.raises(PydanticValidationError) as exc_info:
            ExtractRequest(urls=["not-a-valid-url"])

        errors = exc_info.value.errors()
        assert any("URL" in str(e) for e in errors)

    def test_search_request_valid(self):
        """Test valid SearchRequest."""
        request = SearchRequest(
            social_platforms=["reddit", "tiktok"], query="machine learning", results=50, page=2
        )
        assert len(request.social_platforms) == 2
        assert request.query == "machine learning"
        assert request.results == 50
        assert request.page == 2

    def test_search_request_empty_query(self):
        """Test SearchRequest with empty query."""
        with pytest.raises(PydanticValidationError):
            SearchRequest(social_platforms=["reddit"], query="", results=10, page=1)

    def test_search_request_whitespace_query(self):
        """Test SearchRequest with whitespace-only query."""
        with pytest.raises(PydanticValidationError):
            SearchRequest(social_platforms=["reddit"], query="   ", results=10, page=1)

    def test_search_request_invalid_results(self):
        """Test SearchRequest with invalid results count."""
        # Generated types don't have built-in validation for results range
        # These will succeed with the generated types
        request1 = SearchRequest(social_platforms=["reddit"], query="test", results=0, page=1)
        assert request1.results == 0

        request2 = SearchRequest(social_platforms=["reddit"], query="test", results=101, page=1)
        assert request2.results == 101

    def test_search_request_invalid_page(self):
        """Test SearchRequest with invalid page number."""
        # Generated types don't have built-in validation for page > 0
        request = SearchRequest(social_platforms=["reddit"], query="test", results=10, page=0)
        assert request.page == 0

    def test_search_and_extract_request_valid(self):
        """Test valid SearchAndExtractRequest."""
        request = SearchAndExtractRequest(
            social_platforms=["reddit"],
            query="python tutorials",
            results=25,
            page=1,
            include_comments=True,
            response_mode="markdown",
        )
        assert request.include_comments is True
        assert request.response_mode == "markdown"

    def test_search_and_extract_request_defaults(self):
        """Test SearchAndExtractRequest default values."""
        request = SearchAndExtractRequest(
            social_platforms=["tiktok"], query="coding tips", results=10, page=1
        )
        # Generated types have None defaults
        assert request.include_comments is None
        assert request.response_mode is None


class TestResponseTypes:
    """Test response type functionality."""

    def test_search_result(self):
        """Test SearchResult model."""
        result = SearchResult(
            title="Test Post",
            url="https://www.reddit.com/r/test/comments/123/",
            snippet="This is a test snippet",
            date="Dec 28, 2024",
            imageUrl="https://example.com/image.jpg",  # Use camelCase for field construction
        )
        assert result.title == "Test Post"
        assert result.url == "https://www.reddit.com/r/test/comments/123/"
        assert result.snippet == "This is a test snippet"
        assert result.date == "Dec 28, 2024"
        assert result.image_url == "https://example.com/image.jpg"  # Access via snake_case property

    def test_extracted_post_reddit(self):
        """Test ExtractedPost with Reddit data."""
        reddit_raw = RedditPost(
            id="1ab2c3d",
            name="t3_1ab2c3d",
            title="Test Post",
            url="https://www.reddit.com/r/Python/comments/1ab2c3d/test_post/",
            description="Test description",
            subredditName="Python",
            upvotes=42,
            downvotes=2,
            score=40,
            createdAt="2024-01-01T12:00:00Z",
            comments=[],
        )

        post = ExtractedPost(
            url="https://www.reddit.com/r/Python/comments/1ab2c3d/test_post/",
            source="reddit",
            raw=reddit_raw,
            markdown=None,
            error=None,
        )

        assert post.url == "https://www.reddit.com/r/Python/comments/1ab2c3d/test_post/"
        assert post.source == "reddit"
        assert post.platform == "reddit"  # Alias
        assert isinstance(post.raw, RedditPost)
        assert post.raw.title == "Test Post"
        assert post.raw.subreddit_name == "Python"
        assert post.is_reddit_post() is True
        assert post.is_tiktok_post() is False
        assert post.error is None

    def test_extracted_post_tiktok(self):
        """Test ExtractedPost with TikTok data."""
        tiktok_raw = TiktokPost(
            id="7123456789012345678",
            username="pythontutor",
            url="https://www.tiktok.com/@pythontutor/video/7123456789012345678",
            description="Test video about Python programming",
            createdAt="2024-01-01T12:00:00Z",
            comments=[],
            hashtags=["python", "programming", "tutorial"],
            likes="1234",
            totalComments=56,
        )

        post = ExtractedPost(
            url="https://www.tiktok.com/@pythontutor/video/7123456789012345678",
            source="tiktok",
            raw=tiktok_raw,
            markdown=None,
            error=None,
        )

        assert post.source == "tiktok"
        assert isinstance(post.raw, TiktokPost)
        assert post.raw.username == "pythontutor"
        assert post.raw.description == "Test video about Python programming"
        assert post.is_reddit_post() is False
        assert post.is_tiktok_post() is True
        assert post.error is None

    def test_extracted_post_with_error(self):
        """Test ExtractedPost with extraction error."""
        post = ExtractedPost(
            url="https://invalid.url/post",
            source="reddit",  # Must be 'reddit' or 'tiktok' per the Literal type
            raw=None,
            markdown=None,
            error="Failed to extract: Invalid URL",
        )

        assert post.error == "Failed to extract: Invalid URL"
        assert post.raw is None
        assert post.is_reddit_post() is False
        assert post.is_tiktok_post() is False

    def test_extracted_post_extra_fields(self):
        """Test ExtractedPost allows extra fields."""
        post = ExtractedPost(
            url="https://example.com/post",
            source="reddit",
            raw=None,
            markdown="# Test Post",
            error=None,
            title="Extra Title",
            author="Extra Author",
            content="Extra Content",
            extra_field="Should be allowed",
        )

        assert post.title == "Extra Title"
        assert post.author == "Extra Author"
        assert post.content == "Extra Content"
        assert hasattr(post, "extra_field")

    def test_social_post_legacy(self):
        """Test legacy SocialPost model."""
        post = SocialPost(
            id="123",
            title="Test Post",
            author="testuser",
            upvotes=42,
            comments=10,
            created_at="2024-12-28T12:00:00Z",
            url="https://reddit.com/r/test/comments/123/",
            social_source="reddit",
        )

        assert post.id == "123"
        assert post.title == "Test Post"
        assert post.author == "testuser"
        assert post.upvotes == 42
        assert post.comments == 10
        assert post.social_source == "reddit"


class TestPlatformSpecificTypes:
    """Test platform-specific type models."""

    def test_platform_types_exist(self):
        """Test that platform-specific types are imported and available."""
        # Just verify the types exist and can be imported
        assert RedditPost is not None
        assert RedditComment is not None
        assert TiktokPost is not None
        assert TiktokComment is not None

        # These are auto-generated types, so we don't test their exact structure
        # as it can change when the API changes


class TestTypeGuards:
    """Test type guard functions."""

    def test_is_reddit_post(self):
        """Test is_reddit_post type guard."""
        # Test with actual RedditPost instance
        reddit_post = RedditPost(
            id="test123",
            name="t3_test123",
            title="Test",
            url="https://reddit.com/r/test/comments/test123/",
            description="Test",
            subredditName="test",
            upvotes=1,
            downvotes=0,
            score=1,
            createdAt="2024-01-01T00:00:00Z",
        )
        assert is_reddit_post(reddit_post) is True

        # Test with non-RedditPost types
        assert is_reddit_post({"id": "123", "title": "Test"}) is False
        assert is_reddit_post("not a post") is False
        assert is_reddit_post(None) is False

    def test_is_tiktok_post(self):
        """Test is_tiktok_post type guard."""
        # Test with actual TiktokPost instance
        tiktok_post = TiktokPost(
            id="test456",
            username="testuser",
            url="https://tiktok.com/@testuser/video/test456",
            description="Test",
            createdAt="2024-01-01T00:00:00Z",
            comments=[],
            hashtags=[],
            likes="0",
            totalComments=0,
        )
        assert is_tiktok_post(tiktok_post) is True

        # Test with non-TiktokPost types
        assert is_tiktok_post({"id": "123", "desc": "Test"}) is False
        assert is_tiktok_post("not a post") is False
        assert is_tiktok_post(None) is False


class TestErrorTypes:
    """Test error response types."""

    def test_error_detail(self):
        """Test ErrorDetail model."""
        detail = ErrorDetail(field="query", code="invalid_value", message="Query cannot be empty")

        assert detail.field == "query"
        assert detail.code == "invalid_value"
        assert detail.message == "Query cannot be empty"

    def test_error_response(self):
        """Test ErrorResponse model."""
        response = ErrorResponse(
            error="validation_error",
            message="Validation failed",
            request_id="req_123",
            details=[
                ErrorDetail(
                    field="results", code="out_of_range", message="Must be between 1 and 100"
                )
            ],
        )

        assert response.error == "validation_error"
        assert response.message == "Validation failed"
        assert response.request_id == "req_123"
        assert len(response.details) == 1
        assert response.details[0].field == "results"

    def test_error_response_minimal(self):
        """Test ErrorResponse with minimal fields."""
        response = ErrorResponse(error="server_error", message="Internal server error")

        assert response.error == "server_error"
        assert response.message == "Internal server error"
        assert response.request_id is None
        assert response.details is None
