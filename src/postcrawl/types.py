"""
PostCrawl API type definitions - Compatibility layer.

This module provides backward compatibility by re-exporting generated types
and adding any custom validators or additional types not in the generated code.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

# Import generated platform-specific types
from .generated_types import RedditComment, RedditPost, TiktokComment, TiktokPost

# Re-export enums with proper names
SocialPlatform = Literal["reddit", "tiktok"]
ResponseMode = Literal["raw", "markdown"]


# Custom ExtractRequest with URL validation and field descriptions
class ExtractRequest(BaseModel):
    """Request model for the extract endpoint."""

    urls: list[HttpUrl] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Array of URLs to extract content from",
    )
    include_comments: bool = Field(
        False, description="Whether to include comments and replies. Default: false"
    )
    response_mode: ResponseMode = Field("raw", description="Response format. Default: raw")

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v):
        if len(v) == 0:
            raise ValueError("At least one URL is required")
        if len(v) > 100:
            raise ValueError("Cannot process more than 100 URLs at once")
        return v


# Custom SearchRequest with validations
class SearchRequest(BaseModel):
    """Request model for the search endpoint."""

    social_platforms: list[SocialPlatform] = Field(
        ..., min_length=1, description="Social media platforms to search"
    )
    query: str = Field(..., min_length=1, description="Search query")
    results: int = Field(..., gt=0, le=100, description="Number of results to return")
    page: int = Field(..., gt=0, description="Page number for pagination")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v


# Custom SearchAndExtractRequest with validations
class SearchAndExtractRequest(BaseModel):
    """Request model for the search-and-extract endpoint."""

    social_platforms: list[SocialPlatform] = Field(
        ..., min_length=1, description="Social media platforms to search"
    )
    query: str = Field(..., min_length=1, description="Search query")
    results: int = Field(..., gt=0, le=100, description="Number of results to return")
    page: int = Field(..., gt=0, description="Page number for pagination")
    include_comments: bool = Field(
        False, description="Whether to include comments and replies. Default: false"
    )
    response_mode: ResponseMode = Field("raw", description="Response format. Default: raw")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v


# Response Models - Create proper classes from the generated types
class ExtractedPost(BaseModel):
    """Response model for an extracted post."""

    url: str = Field(..., description="Original URL of the post")
    source: str = Field(..., description="Source platform")
    raw: RedditPost | TiktokPost | dict | str | None = Field(
        None, description="Raw extracted content"
    )
    markdown: str | None = Field(None, description="Markdown formatted content")
    error: str | None = Field(None, description="Error message if extraction failed")

    # Additional fields from raw response
    title: str | None = Field(None, description="Post title")
    author: str | None = Field(None, description="Post author")
    content: str | None = Field(None, description="Post content")
    comments: list | None = Field(None, description="Post comments")

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


# For search results, we need to create a proper model
# The generated types have very long names, so we'll create clean ones
class SocialPost(BaseModel):
    """Response model for a search result."""

    id: str = Field(..., description="Unique identifier for the post")
    title: str = Field(..., description="Post title")
    author: str = Field(..., description="Post author username")
    upvotes: int = Field(..., description="Number of upvotes")
    comments: int = Field(..., description="Number of comments")
    created_at: str = Field(..., description="ISO datetime when post was created")
    url: str = Field(..., description="URL to the original post")
    social_source: SocialPlatform = Field(..., description="Source social platform")


# Response type aliases
ExtractResponse = list[ExtractedPost]
SearchResponse = list[SocialPost]
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
    'ExtractRequest',
    'SearchRequest',
    'SearchAndExtractRequest',
    # Response models
    'ExtractedPost',
    'SocialPost',
    'ExtractResponse',
    'SearchResponse',
    'SearchAndExtractResponse',
    # Platform-specific types
    'RedditPost',
    'RedditComment',
    'TiktokPost',
    'TiktokComment',
    # Enums
    'SocialPlatform',
    'ResponseMode',
    # Error models
    'ErrorDetail',
    'ErrorResponse',
    # Type guards
    'is_reddit_post',
    'is_tiktok_post',
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
