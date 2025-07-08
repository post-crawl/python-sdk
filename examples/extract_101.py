#!/usr/bin/env python3
"""
Simple extraction example - PostCrawl SDK 101
"""

import asyncio
import os

from postcrawl import PostCrawlClient, ExtractedPost, RedditPost, TiktokPost

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
    """Simple extraction example."""
    # Create client
    client = PostCrawlClient(api_key=API_KEY)

    # Extract content from URLs
    urls = [
        "https://www.reddit.com/r/cs50/comments/1ltbkiq/cs50_python_fjnal_project_ideas/",
        "https://www.tiktok.com/@britacooks/video/7397065165805473054",
    ]

    print(f"Extracting content from {len(urls)} URLs...")
    results = await client.extract(urls=urls, include_comments=False)

    # Check if we got fewer results than URLs (some might be filtered)
    if len(results) < len(urls):
        print(f"⚠️  Note: API returned {len(results)} results for {len(urls)} URLs")
        print("    (Some URLs may have been filtered or failed)\n")

    # Print results - each post is of type ExtractedPost
    for i, post in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"URL: {post.url}")
        print(f"Platform: {post.source}")

        if post.error:
            print(f"Error: {post.error}")
        elif post.raw and isinstance(post.raw, RedditPost):
            print(f"Title: {post.raw.title}")
            print(f"Subreddit: r/{post.raw.subreddit_name}")
            print(f"Score: {post.raw.score}")
        elif post.raw and isinstance(post.raw, TiktokPost):
            print(f"Username: @{post.raw.username}")
            print(f"Description: {post.raw.description[:80]}...")
            print(f"Likes: {post.raw.likes}")

    # Summary
    if results:
        print(f"\n{'='*50}")
        print(f"✅ Successfully extracted {len(results)} posts")
    else:
        print("\n⚠️  No results returned")



if __name__ == "__main__":
    asyncio.run(main())
