"""
PostCrawl API constants.
"""

# API endpoints
# DEFAULT_BASE_URL="http://localhost:8787" # for dev
DEFAULT_BASE_URL = "https://edge.postcrawl.com"
API_VERSION = "v1"

# Endpoints
SEARCH_ENDPOINT = "/search"
EXTRACT_ENDPOINT = "/extract"
SEARCH_AND_EXTRACT_ENDPOINT = "/search-and-extract"

# Request defaults
DEFAULT_TIMEOUT = 90.0  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # seconds

# Headers
USER_AGENT = "postcrawl-python/0.1.0"

# Rate limiting
RATE_LIMIT_HEADER = "X-RateLimit-Limit"
RATE_LIMIT_REMAINING_HEADER = "X-RateLimit-Remaining"
RATE_LIMIT_RESET_HEADER = "X-RateLimit-Reset"
