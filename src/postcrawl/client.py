"""
PostCrawl API client.
"""

import asyncio
from typing import Any

import httpx
from pydantic import ValidationError as PydanticValidationError

from .constants import (
    API_VERSION,
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    EXTRACT_ENDPOINT,
    RATE_LIMIT_HEADER,
    RATE_LIMIT_REMAINING_HEADER,
    RATE_LIMIT_RESET_HEADER,
    SEARCH_AND_EXTRACT_ENDPOINT,
    SEARCH_ENDPOINT,
    USER_AGENT,
)
from .exceptions import (
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    NetworkError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from .types import (
    ErrorDetail,
    ErrorResponse,
    ExtractedPost,
    ExtractRequest,
    ExtractResponse,
    ResponseMode,
    SearchAndExtractRequest,
    SearchAndExtractResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    SocialPlatform,
)


class PostCrawlClient:
    """
    PostCrawl API client for searching and extracting content from social media.

    Args:
        api_key: Your PostCrawl API key (starts with 'sk_')
        timeout: Request timeout in seconds (None = no timeout)
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Example:
        ```python
        client = PostCrawlClient(api_key="sk_...")

        # Search for content
        results = await client.search(
            social_platforms=["reddit"],
            query="machine learning",
            results=10,
            page=1
        )

        # Extract content from URLs
        posts = await client.extract(
            urls=["https://reddit.com/..."],
            include_comments=True
        )
        ```
    """

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float | None = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ):
        if not api_key:
            raise ValueError("API key is required")

        if not api_key.startswith("sk_"):
            raise ValueError("API key must start with 'sk_'")

        self.api_key = api_key
        self.base_url = DEFAULT_BASE_URL.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Will be created when needed
        self._client: httpx.AsyncClient | None = None

        # Track rate limit info
        self.rate_limit_info: dict[str, int | None] = {
            "limit": None,
            "remaining": None,
            "reset": None,
        }

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": USER_AGENT,
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def __aenter__(self) -> "PostCrawlClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _update_rate_limit_info(self, headers: httpx.Headers) -> None:
        """Update rate limit information from response headers."""
        if RATE_LIMIT_HEADER in headers:
            self.rate_limit_info["limit"] = int(headers[RATE_LIMIT_HEADER])
        if RATE_LIMIT_REMAINING_HEADER in headers:
            self.rate_limit_info["remaining"] = int(headers[RATE_LIMIT_REMAINING_HEADER])
        if RATE_LIMIT_RESET_HEADER in headers:
            self.rate_limit_info["reset"] = int(headers[RATE_LIMIT_RESET_HEADER])

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make an HTTP request with retry logic."""
        client = self._get_client()
        url = f"/{API_VERSION}{endpoint}"

        try:
            response = await client.request(
                method=method,
                url=url,
                json=json,
            )

            # Update rate limit info
            self._update_rate_limit_info(response.headers)

            # Check for errors
            if response.status_code >= 400:
                await self._handle_error_response(response)

            return response

        except httpx.TimeoutException as e:
            raise TimeoutError(original_error=e) from None
        except httpx.NetworkError as e:
            if retry_count < self.max_retries:
                await asyncio.sleep(self.retry_delay * (retry_count + 1))
                return await self._make_request(
                    method, endpoint, json=json, retry_count=retry_count + 1
                )
            raise NetworkError(f"Network error: {str(e)}", original_error=e) from None

    async def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        try:
            error_data = response.json()
            error_response = ErrorResponse(**error_data)
        except Exception:
            # If we can't parse the error, use the raw response
            error_response = ErrorResponse(
                error="Unknown error",
                message=response.text or f"HTTP {response.status_code}",
            )

        request_id = error_response.request_id

        if response.status_code == 401:
            raise AuthenticationError(
                error_response.message,
                request_id=request_id,
                response=response,
            )
        elif response.status_code == 403:
            raise InsufficientCreditsError(
                error_response.message,
                request_id=request_id,
                response=response,
            )
        elif response.status_code == 422:
            raise ValidationError(
                error_response.message,
                details=error_response.details,
                request_id=request_id,
                response=response,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                error_response.message,
                retry_after=int(retry_after) if retry_after else None,
                request_id=request_id,
                response=response,
            )
        else:
            raise APIError(
                error_response.message,
                status_code=response.status_code,
                request_id=request_id,
                response=response,
            )

    async def search(
        self,
        *,
        social_platforms: list[SocialPlatform],
        query: str,
        results: int,
        page: int,
    ) -> SearchResponse:
        """
        Search for content across social media platforms.

        Args:
            social_platforms: List of platforms to search ("reddit", "tiktok")
            query: Search query string
            results: Number of results to return (max 100)
            page: Page number for pagination (starts at 1)

        Returns:
            List of SearchResult objects with title, url, snippet, date, and image_url

        Raises:
            ValidationError: If request parameters are invalid
            AuthenticationError: If API key is invalid
            InsufficientCreditsError: If account has insufficient credits
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors
        """
        # Validate request
        try:
            request = SearchRequest(
                social_platforms=social_platforms,
                query=query,
                results=results,
                page=page,
            )
        except PydanticValidationError as e:
            raise ValidationError(
                "Invalid request parameters",
                details=[
                    ErrorDetail(
                        field=".".join(str(loc) for loc in err["loc"]),
                        code="invalid_value",
                        message=err["msg"],
                    )
                    for err in e.errors()
                ],
            ) from None

        # Make request
        response = await self._make_request(
            "POST",
            SEARCH_ENDPOINT,
            json=request.model_dump(mode="json", exclude_none=True),
        )

        # Parse response
        data = response.json()
        return [SearchResult(**post) for post in data]

    async def extract(
        self,
        *,
        urls: list[str],
        include_comments: bool = False,
        response_mode: ResponseMode = "raw",
    ) -> ExtractResponse:
        """
        Extract content from social media URLs.

        Args:
            urls: List of URLs to extract (max 25)
            include_comments: Whether to include comments (default: False)
            response_mode: Response format ("raw" or "markdown", default: "raw")

        Returns:
            List of extracted posts with content

        Raises:
            ValidationError: If request parameters are invalid
            AuthenticationError: If API key is invalid
            InsufficientCreditsError: If account has insufficient credits
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors
        """
        # Validate request
        try:
            request = ExtractRequest(
                urls=urls,
                include_comments=include_comments,
                response_mode=response_mode,
            )
        except PydanticValidationError as e:
            raise ValidationError(
                "Invalid request parameters",
                details=[
                    ErrorDetail(
                        field=".".join(str(loc) for loc in err["loc"]),
                        code="invalid_value",
                        message=err["msg"],
                    )
                    for err in e.errors()
                ],
            ) from None

        # Make request
        response = await self._make_request(
            "POST",
            EXTRACT_ENDPOINT,
            json=request.model_dump(mode="json", exclude_none=True),
        )

        # Parse response - Pydantic will handle type validation automatically
        data = response.json()
        return [ExtractedPost(**post_data) for post_data in data]

    async def search_and_extract(
        self,
        *,
        social_platforms: list[SocialPlatform],
        query: str,
        results: int,
        page: int,
        include_comments: bool = False,
        response_mode: ResponseMode = "raw",
    ) -> SearchAndExtractResponse:
        """
        Search for content and extract it in a single operation.

        Args:
            social_platforms: List of platforms to search ("reddit", "tiktok")
            query: Search query string
            results: Number of results to return (max 100)
            page: Page number for pagination (starts at 1)
            include_comments: Whether to include comments (default: False)
            response_mode: Response format ("raw" or "markdown", default: "raw")

        Returns:
            List of extracted posts from search results

        Raises:
            ValidationError: If request parameters are invalid
            AuthenticationError: If API key is invalid
            InsufficientCreditsError: If account has insufficient credits
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors
        """
        # Validate request
        try:
            request = SearchAndExtractRequest(
                social_platforms=social_platforms,
                query=query,
                results=results,
                page=page,
                include_comments=include_comments,
                response_mode=response_mode,
            )
        except PydanticValidationError as e:
            raise ValidationError(
                "Invalid request parameters",
                details=[
                    ErrorDetail(
                        field=".".join(str(loc) for loc in err["loc"]),
                        code="invalid_value",
                        message=err["msg"],
                    )
                    for err in e.errors()
                ],
            ) from None

        # Make request
        response = await self._make_request(
            "POST",
            SEARCH_AND_EXTRACT_ENDPOINT,
            json=request.model_dump(mode="json", exclude_none=True),
        )

        # Parse response - Pydantic will handle type validation automatically
        data = response.json()
        return [ExtractedPost(**post_data) for post_data in data]

    # Synchronous convenience methods
    def search_sync(self, **kwargs: Any) -> SearchResponse:
        """Synchronous version of search()."""
        return asyncio.run(self.search(**kwargs))

    def extract_sync(self, **kwargs: Any) -> ExtractResponse:
        """Synchronous version of extract()."""
        return asyncio.run(self.extract(**kwargs))

    def search_and_extract_sync(self, **kwargs: Any) -> SearchAndExtractResponse:
        """Synchronous version of search_and_extract()."""
        return asyncio.run(self.search_and_extract(**kwargs))
