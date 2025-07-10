"""
PostCrawl Python SDK - A Python client for the PostCrawl API.

This SDK provides a simple and type-safe way to interact with the PostCrawl API
for searching and extracting content from social media platforms.
"""

__version__ = "0.1.1"

from .client import PostCrawlClient
from .exceptions import (
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    NetworkError,
    PostCrawlError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from .types import (
    ExtractedPost,
    ExtractRequest,
    ExtractResponse,
    RedditComment,
    RedditPost,
    ResponseMode,
    SearchAndExtractRequest,
    SearchAndExtractResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    SocialPlatform,
    SocialPost,
    TiktokComment,
    TiktokPost,
)

__all__ = [
    # Client
    "PostCrawlClient",
    # Types
    "ExtractedPost",
    "ExtractRequest",
    "ExtractResponse",
    "RedditComment",
    "RedditPost",
    "ResponseMode",
    "SearchAndExtractRequest",
    "SearchAndExtractResponse",
    "SearchRequest",
    "SearchResponse",
    "SearchResult",
    "SocialPlatform",
    "SocialPost",
    "TiktokComment",
    "TiktokPost",
    # Exceptions
    "APIError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "NetworkError",
    "PostCrawlError",
    "RateLimitError",
    "TimeoutError",
    "ValidationError",
    # Version
    "__version__",
]
