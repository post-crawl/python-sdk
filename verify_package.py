#!/usr/bin/env python3
"""
Package verification script for PostCrawl SDK.
Run this before publishing to ensure everything is working correctly.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return output."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def main():
    print("🔍 PostCrawl SDK Package Verification")
    print("=" * 50)

    # Check if dist exists
    if not Path("dist").exists():
        print("❌ No dist directory found. Run 'uv build' first.")
        sys.exit(1)

    # Find the wheel file
    wheels = list(Path("dist").glob("*.whl"))
    if not wheels:
        print("❌ No wheel file found in dist/")
        sys.exit(1)

    wheel_path = wheels[0].absolute()
    print(f"📦 Found wheel: {wheel_path.name}")

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\n📁 Testing in temporary directory: {tmpdir}")

        # Create and activate virtual environment
        venv_path = Path(tmpdir) / "venv"
        run_command(f"python -m venv {venv_path}")

        # Determine Python executable based on OS
        if os.name == "nt":  # Windows
            python_cmd = f"{venv_path}\\Scripts\\python.exe"
        else:  # Unix-like
            python_cmd = f"{venv_path}/bin/python"

        # Install the wheel
        print("\n📥 Installing package...")
        run_command(f"{python_cmd} -m pip install --quiet {wheel_path}")

        # Test imports
        print("\n🧪 Testing imports...")
        test_script = """
import sys
try:
    # Test main imports
    import postcrawl
    from postcrawl import PostCrawlClient
    from postcrawl.types import ExtractedPost, SearchResult, RedditPost, TiktokPost
    from postcrawl.exceptions import PostCrawlError, AuthenticationError, RateLimitError
    print("✅ All imports successful")

    # Test version
    version = getattr(postcrawl, "__version__", "unknown")
    print(f"✅ PostCrawl version: {version}")

    # Test exports
    exports = getattr(postcrawl, "__all__", [])
    print(f"✅ Available exports: {len(exports)}")

    # Test client initialization
    client = PostCrawlClient(api_key="sk_test_key")
    print(f"✅ Client initialized with base URL: {client.base_url}")
    print(f"✅ Client timeout: {client.timeout}s")
    print(f"✅ Client max retries: {client.max_retries}")

    # Test type completeness
    from postcrawl.types import (
        SearchRequest, ExtractRequest, SearchAndExtractRequest,
        ErrorDetail, ErrorResponse, SocialPlatform, ResponseMode
    )
    print("✅ All type definitions available")

    # Check py.typed for type hints
    import os
    if hasattr(postcrawl, "__file__"):
        py_typed = os.path.join(os.path.dirname(postcrawl.__file__), "py.typed")
        if os.path.exists(py_typed):
            print("✅ py.typed marker found - type hints supported")
        else:
            print("⚠️  py.typed marker not found")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
"""

        # Write test script to file (avoids shell escaping issues)
        test_file = Path(tmpdir) / "test_imports.py"
        test_file.write_text(test_script)
        result = run_command(f"{python_cmd} {test_file}", check=False)
        if result.returncode != 0:
            print(f"❌ Import test failed: {result.stderr}")
            sys.exit(1)
        print(result.stdout)

        # Check dependencies
        print("\n📋 Checking installed dependencies...")
        if os.name == "nt":  # Windows
            deps_result = run_command(
                f"{python_cmd} -m pip list | findstr /R "
                f'"postcrawl pydantic httpx typing-extensions python-dotenv"',
                check=False,
            )
        else:  # Unix-like
            deps_result = run_command(
                f"{python_cmd} -m pip list | grep -E "
                f"'postcrawl|pydantic|httpx|typing-extensions|python-dotenv'",
                check=False,
            )
        print(deps_result.stdout)

    # Get version from pyproject.toml
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # Python 3.10

    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
            version = pyproject["project"]["version"]
    except Exception:
        version = "unknown"

    print("\n✅ All verification tests passed!")
    print(f"\n📦 Package version: {version}")
    print("\n📤 Ready to publish to TestPyPI:")
    print("   uv publish --publish-url https://test.pypi.org/legacy/")
    print("\n📥 To test installation from TestPyPI:")
    print(f"   pip install -i https://test.pypi.org/simple/ postcrawl=={version}")
    print("\n📤 When ready for production PyPI:")
    print("   uv publish")


if __name__ == "__main__":
    main()
