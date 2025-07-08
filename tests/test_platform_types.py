"""
Tests for platform-specific type handling.
"""

import pytest

from postcrawl import PostCrawlClient, RedditPost, TiktokPost


class TestPlatformTypes:
    """Test platform-specific type parsing and type guards."""

    @pytest.mark.asyncio
    async def test_reddit_post_parsing(self, httpx_mock):
        """Test that Reddit posts are parsed as RedditPost instances."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/extract",
            json=[
                {
                    "url": "https://reddit.com/r/test/123",
                    "source": "reddit",
                    "raw": {
                        "id": "123",
                        "title": "Test Post",
                        "description": "Test description",
                        "subredditName": "test",
                        "name": "t3_123",
                        "upvotes": 100,
                        "downvotes": 10,
                        "score": 90,
                        "createdAt": "2024-01-01T00:00:00Z",
                        "url": "https://reddit.com/r/test/123",
                        "comments": [
                            {
                                "id": "c1",
                                "text": "Test comment",
                                "upvotes": 50,
                                "downvotes": 5,
                                "parentId": "123",
                                "score": 45,
                                "createdAt": "2024-01-01T01:00:00Z",
                                "permalink": "/r/test/comments/123/test/c1",
                                "replies": []
                            }
                        ]
                    },
                    "markdown": None,
                    "error": None
                }
            ],
            status_code=200,
        )

        client = PostCrawlClient(api_key="sk_test_key")
        results = await client.extract(urls=["https://reddit.com/r/test/123"])

        assert len(results) == 1
        post = results[0]

        # Check type guards
        assert post.is_reddit_post()
        assert not post.is_tiktok_post()

        # Check specific Reddit post
        reddit_post = post.get_reddit_post()
        assert reddit_post is not None
        assert isinstance(reddit_post, RedditPost)
        assert reddit_post.title == "Test Post"
        assert reddit_post.subreddit_name == "test"
        assert reddit_post.score == 90
        assert len(reddit_post.comments) == 1
        assert reddit_post.comments[0].text == "Test comment"

    @pytest.mark.asyncio
    async def test_tiktok_post_parsing(self, httpx_mock):
        """Test that TikTok posts are parsed as TiktokPost instances."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/extract",
            json=[
                {
                    "url": "https://tiktok.com/@user/video/123",
                    "source": "tiktok",
                    "raw": {
                        "id": "123",
                        "description": "Check out this recipe!",
                        "title": "Amazing Recipe",
                        "username": "testuser",
                        "hashtags": ["cooking", "recipe"],
                        "likes": "1.2M",
                        "totalComments": 500,
                        "createdAt": "2024-01-01T00:00:00Z",
                        "url": "https://tiktok.com/@user/video/123",
                        "comments": [
                            {
                                "id": "c1",
                                "username": "commenter1",
                                "nickname": "Commenter One",
                                "text": "Looks delicious!",
                                "createdAt": "2024-01-01T01:00:00Z",
                                "avatarUrl": "https://example.com/avatar.jpg",
                                "likes": 100,
                                "replies": []
                            }
                        ]
                    },
                    "markdown": None,
                    "error": None
                }
            ],
            status_code=200,
        )

        client = PostCrawlClient(api_key="sk_test_key")
        results = await client.extract(urls=["https://tiktok.com/@user/video/123"])

        assert len(results) == 1
        post = results[0]

        # Check type guards
        assert post.is_tiktok_post()
        assert not post.is_reddit_post()

        # Check specific TikTok post
        tiktok_post = post.get_tiktok_post()
        assert tiktok_post is not None
        assert isinstance(tiktok_post, TiktokPost)
        assert tiktok_post.username == "testuser"
        assert tiktok_post.description == "Check out this recipe!"
        assert tiktok_post.likes == "1.2M"
        assert tiktok_post.total_comments == 500
        assert len(tiktok_post.hashtags) == 2
        assert "cooking" in tiktok_post.hashtags

    @pytest.mark.asyncio
    async def test_fallback_to_dict(self, httpx_mock):
        """Test that invalid data falls back to dict."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/extract",
            json=[
                {
                    "url": "https://reddit.com/r/test/123",
                    "source": "reddit",
                    "raw": {
                        "invalid_field": "This doesn't match RedditPost schema"
                    },
                    "markdown": None,
                    "error": None
                }
            ],
            status_code=200,
        )

        client = PostCrawlClient(api_key="sk_test_key")
        results = await client.extract(urls=["https://reddit.com/r/test/123"])

        assert len(results) == 1
        post = results[0]

        # Should not be typed as RedditPost due to invalid schema
        assert not post.is_reddit_post()
        assert not post.is_tiktok_post()
        assert post.get_reddit_post() is None
        assert post.get_tiktok_post() is None

        # Raw should be a dict
        assert isinstance(post.raw, dict)
        assert post.raw["invalid_field"] == "This doesn't match RedditPost schema"

    @pytest.mark.asyncio
    async def test_error_posts_not_typed(self, httpx_mock):
        """Test that posts with errors don't get typed."""
        httpx_mock.add_response(
            method="POST",
            url="https://edge-alpha.postcrawl.com/v1/extract",
            json=[
                {
                    "url": "https://reddit.com/r/test/123",
                    "source": "reddit",
                    "raw": {
                        "id": "123",
                        "title": "Test"
                    },
                    "markdown": None,
                    "error": "Failed to extract"
                }
            ],
            status_code=200,
        )

        client = PostCrawlClient(api_key="sk_test_key")
        results = await client.extract(urls=["https://reddit.com/r/test/123"])

        assert len(results) == 1
        post = results[0]

        # Should not be typed due to error
        assert not post.is_reddit_post()
        assert post.error == "Failed to extract"
        assert isinstance(post.raw, dict)
