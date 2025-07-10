"""
PostCrawl API type definitions - Compatibility layer.

This module provides backward compatibility by re-exporting generated types
and adding any custom validators or additional types not in the generated code.

Key Types:
- SearchResult: Response from search endpoint (title, url, snippet, date, image_url)
- ExtractedPost: Response from extract endpoint (url, source, raw, markdown, error)
- SocialPost: DEPRECATED - Legacy search response type (use SearchResult instead)
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

# Import all generated types
from .generated_types import (
    ExtractRequest as GeneratedExtractRequest,
)
from .generated_types import (
    PostOutputT,
    RedditComment,
    RedditPost,
    SearchResult,
    TiktokComment,
    TiktokPost,
)
from .generated_types import (
    SearchAndExtractRequest as GeneratedSearchAndExtractRequest,
)
from .generated_types import (
    SearchRequest as GeneratedSearchRequest,
)

# Re-export enums with proper names
SocialPlatform = Literal["reddit", "tiktok"]
ResponseMode = Literal["raw", "markdown"]


# Custom ExtractRequest with URL validation and field descriptions
class ExtractRequest(GeneratedExtractRequest):
    """Request model for the extract endpoint with additional validation."""

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: list[str]) -> list[str]:
        """Validate URLs list and each URL format."""
        if len(v) == 0:
            raise ValueError("At least one URL is required")
        if len(v) > 100:
            raise ValueError("Cannot process more than 100 URLs at once")

        # Validate each URL
        for url in v:
            try:
                # Use Pydantic's HttpUrl for validation
                HttpUrl(url)
            except Exception:
                raise ValueError(f"Invalid URL format: {url}") from None

        return v


# Custom SearchRequest with validations
class SearchRequest(GeneratedSearchRequest):
    """Request model for the search endpoint with additional validation."""

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v

    @field_validator("social_platforms")
    @classmethod
    def validate_social_platforms(cls, v: list[SocialPlatform]) -> list[SocialPlatform]:
        if not v or len(v) == 0:
            raise ValueError("At least one social platform is required")
        return v


# Custom SearchAndExtractRequest with validations
class SearchAndExtractRequest(GeneratedSearchAndExtractRequest):
    """Request model for the search-and-extract endpoint with additional validation."""

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v

    @field_validator("social_platforms")
    @classmethod
    def validate_social_platforms(cls, v: list[SocialPlatform]) -> list[SocialPlatform]:
        if not v or len(v) == 0:
            raise ValueError("At least one social platform is required")
        return v


# Response Models - Extend the generated PostOutputT type
class ExtractedPost(PostOutputT):
    """Response model for an extracted post - extends generated PostOutputT."""

    # The generated PostOutputT already has:
    # - url: str
    # - source: Literal['reddit', 'tiktok']
    # - raw: RedditPost | TiktokPost | None
    # - markdown: str | None
    # - error: str | None

    # Additional fields for backward compatibility
    title: str | None = Field(None, description="Post title")
    author: str | None = Field(None, description="Post author")
    content: str | None = Field(None, description="Post content")
    comments: list[Any] | None = Field(None, description="Post comments")

    model_config = ConfigDict(
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # For backward compatibility
    )

    @property
    def platform(self) -> str:
        """Alias for source for backward compatibility."""
        return self.source

    def is_reddit_post(self) -> bool:
        """Check if this is a Reddit post."""
        return self.source == "reddit" and isinstance(self.raw, RedditPost)

    def is_tiktok_post(self) -> bool:
        """Check if this is a TikTok post."""
        return self.source == "tiktok" and isinstance(self.raw, TiktokPost)

    def get_reddit_post(self) -> RedditPost | None:
        """Get the raw data as a RedditPost if available."""
        if self.is_reddit_post():
            return self.raw  # type: ignore
        return None

    def get_tiktok_post(self) -> TiktokPost | None:
        """Get the raw data as a TiktokPost if available."""
        if self.is_tiktok_post():
            return self.raw  # type: ignore
        return None


# SearchResult is imported from generated_types, which has:
# - title: str
# - url: str
# - snippet: str
# - date: str
# - image_url: str (aliased from API's imageUrl)


# Legacy model for backward compatibility (deprecated)
class SocialPost(BaseModel):
    """
    Legacy response model for search results.

    DEPRECATED: Use SearchResult instead. This model is kept for backward compatibility
    but does not match the actual API response.
    """

    id: str | None = Field(None, description="Unique identifier for the post")
    title: str | None = Field(None, description="Post title")
    author: str | None = Field(None, description="Post author username")
    upvotes: int | None = Field(None, description="Number of upvotes")
    comments: int | None = Field(None, description="Number of comments")
    created_at: str | None = Field(None, description="ISO datetime when post was created")
    url: str | None = Field(None, description="URL to the original post")
    social_source: SocialPlatform | None = Field(None, description="Source social platform")


# Response type aliases
ExtractResponse = list[ExtractedPost]
SearchResponse = list[SearchResult]  # Updated to use SearchResult
SearchAndExtractResponse = list[ExtractedPost]


# Type guard functions for type narrowing
def is_reddit_post(raw: Any) -> bool:
    """Type guard to check if raw data is a RedditPost."""
    return isinstance(raw, RedditPost)


def is_tiktok_post(raw: Any) -> bool:
    """Type guard to check if raw data is a TiktokPost."""
    return isinstance(raw, TiktokPost)


# Re-export platform-specific types for easy access
__all__ = [
    # Request models
    "ExtractRequest",
    "SearchRequest",
    "SearchAndExtractRequest",
    # Response models
    "ExtractedPost",
    "SearchResult",
    "SocialPost",
    "ExtractResponse",
    "SearchResponse",
    "SearchAndExtractResponse",
    # Platform-specific types
    "RedditPost",
    "RedditComment",
    "TiktokPost",
    "TiktokComment",
    # Enums
    "SocialPlatform",
    "ResponseMode",
    # Error models
    "ErrorDetail",
    "ErrorResponse",
    # Type guards
    "is_reddit_post",
    "is_tiktok_post",
]


# Error Models (these weren't generated, so we keep them)
class ErrorDetail(BaseModel):
    """Error detail for field-specific errors."""

    field: str
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str
    message: str
    request_id: str | None = None
    details: list[ErrorDetail] | None = None
