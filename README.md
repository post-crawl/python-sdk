# PostCrawl Python SDK

Official Python SDK for [PostCrawl](https://postcrawl.com) - The Fastest LLM-Ready Social Media Crawler. Extract and search content from Reddit and TikTok with a simple, type-safe Python interface.

## Features

- 🔍 **Search** across Reddit and TikTok with advanced filtering
- 📊 **Extract** content from social media URLs with optional comments
- 🚀 **Combined search and extract** in a single operation
- 🏷️ **Type-safe** with Pydantic models and full type hints
- ⚡ **Async/await** support with synchronous convenience methods
- 🛡️ **Comprehensive error handling** with detailed exceptions
- 📈 **Rate limiting** support with credit tracking
- 🔄 **Automatic retries** for network errors
- 🎯 **Platform-specific models** for Reddit and TikTok data with strong typing
- 📝 **Rich content formatting** with markdown support
- 🐍 **Python 3.10+** with modern type annotations and snake_case naming

## Installation

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that we recommend:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add postcrawl to your project
uv add postcrawl
```

### Using pip

```bash
pip install postcrawl
```

### Optional: Environment Variables

For loading API keys from .env files:

```bash
uv add python-dotenv
# or
pip install python-dotenv
```

## Requirements

- Python 3.10 or higher
- PostCrawl API key ([Get one for free](https://postcrawl.com))

## Quick Start

### Async Usage (Recommended)
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

        # Process results
        for post in results:
            print(f"{post.title} - {post.url}")
            print(f"  Date: {post.date}")
            print(f"  Snippet: {post.snippet[:100]}...")

# Run the async function
asyncio.run(main())
```

### Synchronous Usage
```python
from postcrawl import PostCrawlClient

# Initialize the client
client = PostCrawlClient(api_key="sk_your_api_key_here")

# Search synchronously
results = client.search_sync(
    social_platforms=["reddit", "tiktok"],
    query="artificial intelligence",
    results=5
)

# Extract content from URLs
posts = client.extract_sync(
    urls=["https://reddit.com/r/...", "https://tiktok.com/@..."],
    include_comments=True
)
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
# Using uv (recommended)
uv run python examples/search_101.py

# Or with standard Python
cd examples
python search_101.py
```

## Response Models

### SearchResult
Response from the search endpoint:
- `title`: Title of the search result
- `url`: URL of the search result
- `snippet`: Text snippet from the content
- `date`: Date of the post (e.g., "Dec 28, 2024")
- `image_url`: URL of associated image (can be empty string)

### ExtractedPost
- `url`: Original URL
- `source`: Platform name ("reddit" or "tiktok")
- `raw`: Raw content data (RedditPost or TiktokPost object) - strongly typed
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
        # Access Reddit-specific fields with snake_case attributes
        print(f"Subreddit: r/{post.raw.subreddit_name}")
        print(f"Score: {post.raw.score}")
        print(f"Title: {post.raw.title}")
        print(f"Upvotes: {post.raw.upvotes}")
        print(f"Created: {post.raw.created_at}")
        if post.raw.comments:
            print(f"Comments: {len(post.raw.comments)}")
    elif isinstance(post.raw, TiktokPost):
        # Access TikTok-specific fields with snake_case attributes
        print(f"Username: @{post.raw.username}")
        print(f"Likes: {post.raw.likes}")
        print(f"Total Comments: {post.raw.total_comments}")
        print(f"Created: {post.raw.created_at}")
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

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup and contribution guidelines.

### Quick Development Setup

```bash
# Clone the repository
git clone https://github.com/post-crawl/python-sdk.git
cd python-sdk

# Install dependencies
uv sync

# Run tests
make test

# Run all checks (format, lint, test)
make check

# Build the package
make build
```

### Available Commands

```bash
make help         # Show all available commands
make format       # Format code with black and ruff
make lint         # Run linting and type checking
make test         # Run test suite
make check        # Run format, lint, and tests
make build        # Build distribution packages
make verify       # Verify package installation
make publish-test # Publish to TestPyPI
```

## API Key Management

### Environment Variables (Recommended)

Store your API key securely in environment variables:

```bash
export POSTCRAWL_API_KEY="sk_your_api_key_here"
```

Or use a `.env` file:
```bash
# .env
POSTCRAWL_API_KEY=sk_your_api_key_here
```

Then load it in your code:
```python
import os
from dotenv import load_dotenv
from postcrawl import PostCrawlClient

load_dotenv()
client = PostCrawlClient(api_key=os.getenv("POSTCRAWL_API_KEY"))
```

### Security Best Practices

- **Never hardcode API keys** in your source code
- **Add `.env` to `.gitignore`** to prevent accidental commits
- **Use environment variables** in production
- **Rotate keys regularly** through the PostCrawl dashboard
- **Set key permissions** to limit access to specific operations

## Rate Limits & Credits

PostCrawl uses a credit-based system:

- **Search**: ~1 credit per 10 results
- **Extract**: ~1 credit per URL (without comments)
- **Extract with comments**: ~3 credits per URL

Rate limits are returned in response headers:
```python
client = PostCrawlClient(api_key="sk_...")
results = await client.search(...)

print(f"Rate limit: {client.rate_limit_info['limit']}")
print(f"Remaining: {client.rate_limit_info['remaining']}")
print(f"Reset at: {client.rate_limit_info['reset']}")
```

## Support

- **Documentation**: [github.com/post-crawl/python-sdk](https://github.com/post-crawl/python-sdk)
- **Issues**: [github.com/post-crawl/python-sdk/issues](https://github.com/post-crawl/python-sdk/issues)
- **Email**: support@postcrawl.com

## License

MIT License - see [LICENSE](LICENSE) file for details.
