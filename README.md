# PostCrawl Python SDK

Official Python SDK for PostCrawl - The Fastest LLM-Ready Social Media Crawler

## Features

- 🔍 **Search** across Reddit and TikTok
- 📊 **Extract** content from social media URLs with optional comments
- 🚀 **Combined search and extract** in a single operation
- 🏷️ **Type-safe** with Pydantic models and full type hints
- ⚡ **Async/await** support with synchronous convenience methods
- 🛡️ **Comprehensive error handling** with detailed exceptions
- 📈 **Rate limiting** support
- 🔄 **Automatic retries** for network errors

## Installation

Install using pip:

```bash
pip install postcrawl
```

Or with UV (recommended):

```bash
uv add postcrawl
```

For loading API keys from .env files, also install python-dotenv:

```bash
pip install python-dotenv
# or
uv add python-dotenv
```

## Requirements

- Python 3.10+
- A PostCrawl API key (get one at [postcrawl.com](https://postcrawl.com))

## Quick Start

```python
import asyncio
from postcrawl import PostCrawlClient

async def main():
    # Initialize the client with your API key
    async with PostCrawlClient(api_key="sk_your_api_key_here") as client:
        # Search for content
        results = await client.search(
            social_platforms=["reddit"],
            query="machine learning",
            results=10,
            page=1
        )

        for post in results:
            print(f"{post.title} - {post.url}")

# Run the async function
asyncio.run(main())
```


## API Reference

### Search
```python
results = await client.search(
    social_platforms=["reddit", "tiktok"],
    query="your search query",
    results=10,  # 1-100
    page=1       # pagination
)
```

### Extract
```python
posts = await client.extract(
    urls=["https://reddit.com/...", "https://tiktok.com/..."],
    include_comments=True,
    response_mode="raw"  # or "markdown"
)
```

### Search and Extract
```python
posts = await client.search_and_extract(
    social_platforms=["reddit"],
    query="search query",
    results=5,
    page=1,
    include_comments=False,
    response_mode="markdown"
)
```

### Synchronous Methods
```python
# All methods have synchronous versions
results = client.search_sync(...)
posts = client.extract_sync(...)
combined = client.search_and_extract_sync(...)
```

## Examples

Check out the `examples/` directory for complete working examples:
- `search_101.py` - Basic search functionality demo
- `extract_101.py` - Content extraction demo
- `search_and_extract_101.py` - Combined operation demo

Run examples with:
```bash
cd examples
python search_101.py
```

## Response Models

### SocialPost
- `id`: Unique post identifier
- `title`: Post title
- `author`: Author username
- `url`: Original post URL
- `upvotes`: Number of upvotes
- `comments`: Number of comments
- `created_at`: ISO timestamp
- `social_source`: Platform ("reddit" or "tiktok")

### ExtractedPost
- `url`: Original URL
- `source`: Platform name ("reddit" or "tiktok")
- `raw`: Raw content data (RedditPost or TiktokPost object)
- `markdown`: Markdown formatted content (when response_mode="markdown")
- `error`: Error message if extraction failed

## Working with Platform-Specific Types

The SDK provides type-safe access to platform-specific data:

```python
from postcrawl import PostCrawlClient, RedditPost, TiktokPost

# Extract content with proper type handling
posts = await client.extract(urls=["https://reddit.com/..."])

for post in posts:
    if post.error:
        print(f"Error: {post.error}")
    elif isinstance(post.raw, RedditPost):
        # Access Reddit-specific fields
        print(f"Subreddit: r/{post.raw.subreddit_name}")
        print(f"Score: {post.raw.score}")
        print(f"Title: {post.raw.title}")
        if post.raw.comments:
            print(f"Comments: {len(post.raw.comments)}")
    elif isinstance(post.raw, TiktokPost):
        # Access TikTok-specific fields
        print(f"Username: @{post.raw.username}")
        print(f"Likes: {post.raw.likes}")
        print(f"Views: {post.raw.views}")
        if post.raw.hashtags:
            print(f"Hashtags: {', '.join(post.raw.hashtags)}")
```

## Error Handling

```python
from postcrawl.exceptions import (
    AuthenticationError,      # Invalid API key
    InsufficientCreditsError, # Not enough credits
    RateLimitError,          # Rate limit exceeded
    ValidationError          # Invalid parameters
)
```

## Support

- Documentation: [github.com/post-crawl/python-sdk](https://github.com/post-crawl/python-sdk)
- GitHub: [github.com/post-crawl/python-sdk](https://github.com/post-crawl/python-sdk)
- Issues: [github.com/post-crawl/python-sdk/issues](https://github.com/post-crawl/python-sdk/issues)
