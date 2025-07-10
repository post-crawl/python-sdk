# PostCrawl Python SDK Examples

This directory contains example scripts demonstrating how to use the PostCrawl Python SDK.

## Prerequisites

1. **Install the SDK**:
   ```bash
   pip install postcrawl
   # or with uv:
   uv add postcrawl
   ```

2. **Get an API key** from [postcrawl.com](https://postcrawl.com)

3. **Set your API key**:
   ```bash
   export POSTCRAWL_API_KEY=sk_your_api_key_here
   ```

## Available Examples

### 🔍 Search Example (`search_101.py`)
Search for content across Reddit and TikTok platforms.

```bash
python search_101.py
```

**Features demonstrated:**
- Search across multiple platforms
- Pagination support
- Result parsing and display

### 📊 Extract Example (`extract_101.py`)
Extract full content from social media URLs.

```bash
python extract_101.py
```

**Features demonstrated:**
- Extract content from Reddit and TikTok URLs
- Handle platform-specific data types
- Access comments and metadata

### 🚀 Search & Extract Combined (`search_and_extract_101.py`)
Perform search and extraction in a single operation.

```bash
python search_and_extract_101.py
```

**Features demonstrated:**
- Combined search and extract operation
- Markdown formatting option
- Type-safe access to platform data

## Running the Examples

### With environment variables:
```bash
export POSTCRAWL_API_KEY=sk_your_api_key_here
python search_101.py
```

### With .env file:
Create a `.env` file in the examples directory:
```
POSTCRAWL_API_KEY=sk_your_api_key_here
```

Then run:
```bash
python search_101.py
```

## Example Output

```
🔍 Searching for 'python programming' on Reddit...

Found 10 results:

1. "Best Python Resources for Beginners"
   URL: https://reddit.com/r/learnpython/...
   Date: Dec 28, 2024
   Preview: I've been learning Python for 3 months...

2. "Python vs JavaScript in 2024"
   URL: https://reddit.com/r/programming/...
   Date: Dec 27, 2024
   Preview: After using both languages extensively...
```

## Credit Usage

| Operation | Approximate Credits |
|-----------|-------------------|
| Search (10 results) | ~1 credit |
| Extract (without comments) | ~1 credit per URL |
| Extract (with comments) | ~3 credits per URL |

## Tips

- Start with small result counts to test
- Use `include_comments=False` to reduce credit usage
- Check rate limits with `client.rate_limit_info`
- Handle errors gracefully (see exception handling in examples)

## Support

- Documentation: [github.com/post-crawl/python-sdk](https://github.com/post-crawl/python-sdk)
- API Reference: [postcrawl.com/docs](https://postcrawl.com/docs)
- Issues: [github.com/post-crawl/python-sdk/issues](https://github.com/post-crawl/python-sdk/issues)