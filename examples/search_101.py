#!/usr/bin/env python3
"""
Simple search example - PostCrawl SDK 101
"""

import asyncio
import os

from postcrawl import PostCrawlClient, SocialPost

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional, just continue without it
    pass

API_KEY = os.getenv("POSTCRAWL_API_KEY", "sk_your_api_key_here")

if not API_KEY or API_KEY == "sk_your_api_key_here":
    print("❌ Error: POSTCRAWL_API_KEY environment variable is not set.")
    print("Please set it in your .env file or environment.")
    exit(1)


async def main():
    """Simple search example."""
    # Create client
    client = PostCrawlClient(api_key=API_KEY)

    # Search Reddit
    results = await client.search(
        social_platforms=["reddit", "tiktok"],
        query="python",
        results=5,
        page=1,
    )

    # Print results with proper type annotations
    print(f"Found {len(results)} posts:")
    for post in results:  # post is of type SocialPost
        print(f"- {post.title}")
        print(f"  URL: {post.url}")
        print(f"  Platform: {post.social_source}")
        print(f"  Author: {post.author}")
        print(f"  Stats: {post.upvotes} upvotes, {post.comments} comments")
        print()


if __name__ == "__main__":
    asyncio.run(main())
