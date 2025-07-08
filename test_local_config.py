#!/usr/bin/env python3
"""Test local development configuration."""

import os

from postcrawl import PostCrawlClient
from postcrawl.constants import DEFAULT_BASE_URL


def test_environment_configuration():
    """Test that environment variable configuration works."""

    print("🧪 Testing PostCrawl SDK local development configuration...")
    print("=" * 60)

    # Test 1: Default configuration
    print("\n1️⃣ Default Configuration:")
    print(f"   DEFAULT_BASE_URL: {DEFAULT_BASE_URL}")
    current_env = os.getenv("POSTCRAWL_API_URL")
    if current_env:
        print(f"   ✅ POSTCRAWL_API_URL is set: {current_env}")
    else:
        print("   ℹ️  POSTCRAWL_API_URL not set, using default")

    # Test 2: Client initialization with defaults
    print("\n2️⃣ Client with default configuration:")
    client1 = PostCrawlClient(api_key="sk_test_123")
    print(f"   Base URL: {client1.base_url}")

    # Test 3: Simulate environment variable
    print("\n3️⃣ Testing with environment variable:")
    original_env = os.environ.get("POSTCRAWL_API_URL")
    try:
        os.environ["POSTCRAWL_API_URL"] = "http://localhost:8787"
        # Need to reload the module to pick up the new env var
        from importlib import reload

        import postcrawl.constants

        reload(postcrawl.constants)
        from postcrawl.constants import DEFAULT_BASE_URL as reloaded_url

        print(f"   Reloaded DEFAULT_BASE_URL: {reloaded_url}")

        # Create new client
        client3 = PostCrawlClient(api_key="sk_test_123")
        print(f"   Client base URL: {client3.base_url}")

    finally:
        # Restore original environment
        if original_env is None:
            os.environ.pop("POSTCRAWL_API_URL", None)
        else:
            os.environ["POSTCRAWL_API_URL"] = original_env

    print("\n" + "=" * 60)
    print("✅ Configuration test complete!")
    print("\n📝 To use with local development:")
    print("   1. Start scraping-server-v1: cd apps/scraping-server-v1 && bun run dev")
    print("   2. Set environment: export POSTCRAWL_API_URL=http://localhost:8787")
    print("   3. Run your Python script normally")
    print("=" * 60)


if __name__ == "__main__":
    test_environment_configuration()
