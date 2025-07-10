#!/usr/bin/env python3
"""
Simple search example - PostCrawl SDK 101
"""

import asyncio
import os

# Load environment variables from .env file
from dotenv import load_dotenv

from postcrawl import PostCrawlClient

load_dotenv()


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
    for post in results:  # post is of type SearchResult
        print(f"\n- {post.title}")
        print(f"  URL: {post.url}")
        print(f"  Date: {post.date}")
        print(
            f"  Snippet: {post.snippet[:100]}..."
            if len(post.snippet) > 100
            else f"  Snippet: {post.snippet}"
        )
        if post.image_url:
            print(f"  Image: {post.image_url}")


if __name__ == "__main__":
    asyncio.run(main())
