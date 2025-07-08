#!/usr/bin/env python3
"""
Simple search and extract example - PostCrawl SDK 101
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
    """Simple search and extract example."""
    # Create client
    client = PostCrawlClient(api_key=API_KEY)

    # Search and extract Reddit posts in one operation
    results = await client.search_and_extract(
        social_platforms=["reddit", "tiktok"],
        query="algorithms",
        results=3,
        page=1,
        include_comments=True,  # Extract comments too
        response_mode="raw",    # Get full post data
    )

    # Print results - each post is of type ExtractedPost
    print(f"Found and extracted {len(results)} posts:")
    for i, post in enumerate(results, 1):
        print(f"\n{i}. {post.url}")

        if post.error:
            print(f"   ❌ Error: {post.error}")
        elif post.raw:
            # Handle different platform types
            if isinstance(post.raw, RedditPost):
                # Reddit-specific fields
                print(f"   ✓ Title: {post.raw.title}")
                print(f"   ✓ Score: {post.raw.score}")
                print(f"   ✓ Subreddit: r/{post.raw.subreddit_name}")

                # Show content preview
                if post.raw.description:
                    preview = post.raw.description[:150]
                    print(f"   📄 Content: {preview}...")

                # Show comments if included
                if post.raw.comments:
                    print(f"   💬 {len(post.raw.comments)} comments")
                    # Show first comment
                    if post.raw.comments:
                        comment = post.raw.comments[0]
                        comment_preview = comment.text[:100]
                        print(f"      └─ {comment_preview}...")

            elif isinstance(post.raw, TiktokPost):
                # TikTok-specific fields
                print(f"   ✓ Username: @{post.raw.username}")
                print(f"   ✓ Likes: {post.raw.likes}")

                # Show description
                if post.raw.description:
                    preview = post.raw.description[:150]
                    print(f"   📄 Description: {preview}...")

                # Show hashtags
                if post.raw.hashtags:
                    print(f"   🏷️  Hashtags: {', '.join(post.raw.hashtags[:5])}")

                # Show comments if included
                if post.raw.comments:
                    print(f"   💬 {len(post.raw.comments)} comments")
                    # Show first comment
                    if post.raw.comments:
                        comment = post.raw.comments[0]
                        comment_preview = comment.text[:100]
                        print(f"      └─ @{comment.username}: {comment_preview}...")


if __name__ == "__main__":
    asyncio.run(main())
