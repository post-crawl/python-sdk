# PostCrawl Python SDK Examples

This directory contains interactive examples demonstrating the PostCrawl Python SDK's functionality. Each example showcases different API endpoints and features.

## Prerequisites

1. **Get an API key** from [postcrawl.com](https://postcrawl.com)
2. **Set your API key**:
   ```bash
   export POSTCRAWL_API_KEY=sk_your_api_key_here
   ```
3. **Install dependencies**:
   ```bash
   pip install postcrawl python-dotenv
   # or with uv:
   uv pip install postcrawl python-dotenv
   ```

## Available Examples

### 🔍 Search Example (`search_101.py`)
Demonstrates basic search functionality:
- Search across Reddit and TikTok platforms
- Query for "python" related posts
- Display results with title and URL

### 📊 Extract Example (`extract_101.py`)
Shows content extraction from URLs:
- Extract content from Reddit and TikTok URLs
- Handle platform-specific data with proper types (`RedditPost`, `TiktokPost`)
- Display relevant fields based on platform

### 🔍📊 Combined Search & Extract (`search_and_extract_101.py`)
Demonstrates combined operation:
- Search for "algorithms" across platforms
- Extract full content including comments
- Use proper type checking for platform-specific fields
- Display Reddit-specific fields (subreddit, score, comments)
- Display TikTok-specific fields (username, likes, hashtags)

## Running Examples

```bash
# Search functionality
python search_101.py

# Extract functionality  
python extract_101.py

# Combined functionality
python search_and_extract_101.py
```

### Environment Configuration
Create a `.env` file in the examples directory:
```env
POSTCRAWL_API_KEY=sk_your_api_key_here
```

Or set environment variables:
```bash
export POSTCRAWL_API_KEY=sk_your_api_key_here
export POSTCRAWL_API_URL=https://edge-alpha.postcrawl.com  # Optional
```

## Example Output

Each example provides detailed output including:

```
⚠️  CREDIT CONSUMPTION WARNING:
This test will consume approximately 1 credit (10 results).
Do you want to proceed? (y/n): y

============================================================
Testing: Search Endpoint - Basic
============================================================

📤 Request: {
  "social_platforms": ["reddit"],
  "query": "pizza",
  "results": 10,
  "page": 1
}

✅ PASS: Response is a list with 10 items
✅ PASS: All items are SocialPost instances
✅ PASS: All posts have valid structure
✅ PASS: All posts are from Reddit as requested
✅ PASS: Rate limit info available (limit: 1000)

📋 Sample Results:
  Title: Best Pizza Recipe Ever
  Author: pizza_lover_2024
  URL: https://reddit.com/r/cooking/...
  Stats: 156 upvotes, 42 comments

💰 Rate Limit Info:
  Limit: 1000 requests
  Remaining: 999 requests
  Reset: 1641234567

Summary: 5/5 tests passed
✅ All search tests passed!
```

## Credit Consumption Guide

| Operation | Typical Cost | Notes |
|-----------|--------------|-------|
| Search (10 results) | ~1 credit | Cost varies by platform |
| Extract (1 URL, no comments) | ~1 credit | Per URL processed |
| Extract (1 URL, with comments) | ~3 credits | Comments increase cost |
| Search-and-Extract | Search cost + Extract cost | Combined operation |

**Important Notes:**
- All examples show estimated credit costs before execution
- Actual costs may vary based on content complexity
- Invalid URLs are filtered out and don't consume credits
- Rate limits vary by subscription tier

## Testing vs Production

These examples work with both:
- **Production API**: `https://edge-alpha.postcrawl.com` (default)
- **Local Development**: Set `POSTCRAWL_API_URL=http://localhost:8787`

For local testing with the scraping server:
```bash
# Terminal 1: Start scraping server
cd apps/scraping-server-v1
bun run dev

# Terminal 2: Run examples with local API
export POSTCRAWL_API_URL=http://localhost:8787
uv run python search_example.py
```

## Best Practices

1. **Always confirm credit consumption** - Each example asks before proceeding
2. **Start with basic examples** - Try `basic_search.py` before `search_example.py`
3. **Monitor rate limits** - Examples display rate limit information
4. **Handle errors gracefully** - See `error_handling.py` for patterns
5. **Use raw mode for structured data** - Better for programmatic access
6. **Use markdown mode for readability** - Better for human consumption