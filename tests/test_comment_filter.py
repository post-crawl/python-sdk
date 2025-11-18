import pytest
from pytest_httpx import HTTPXMock

from postcrawl import PostCrawlClient
from postcrawl.types import CommentFilterConfig


@pytest.mark.asyncio
async def test_extract_with_comment_filter(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://edge.postcrawl.com/v1/extract",
        json=[],
        status_code=200,
    )

    filter_config = CommentFilterConfig(min_score=10, max_depth=2)

    async with PostCrawlClient(api_key="sk_test") as client:
        await client.extract(
            urls=["https://reddit.com/r/test"],
            include_comments=True,
            comment_filter_config=filter_config,
        )

    request = httpx_mock.get_request()
    assert request is not None
    import json

    body = json.loads(request.content)

    assert body["comment_filter_config"] == {
        "min_score": 10,
        "max_depth": 2,
    }


@pytest.mark.asyncio
async def test_search_and_extract_with_comment_filter(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://edge.postcrawl.com/v1/search-and-extract",
        json=[],
        status_code=200,
    )

    filter_config = CommentFilterConfig(tier_limits={"0": 5}, preserve_high_quality_threads=False)

    async with PostCrawlClient(api_key="sk_test") as client:
        await client.search_and_extract(
            social_platforms=["reddit"],
            query="test",
            results=10,
            page=1,
            include_comments=True,
            comment_filter_config=filter_config,
        )

    request = httpx_mock.get_request()
    assert request is not None
    import json

    body = json.loads(request.content)

    assert body["comment_filter_config"] == {
        "tier_limits": {"0": 5},
        "preserve_high_quality_threads": False,
    }
