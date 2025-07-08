#!/usr/bin/env python3
"""
Package verification script for PostCrawl SDK.
Run this before publishing to ensure everything is working correctly.
"""

import sys
import subprocess
import tempfile
import os
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
        
        # Determine activation script based on OS
        if os.name == 'nt':  # Windows
            activate_cmd = f"{venv_path}\\Scripts\\activate.bat && "
            python_cmd = f"{venv_path}\\Scripts\\python.exe"
        else:  # Unix-like
            activate_cmd = f"source {venv_path}/bin/activate && "
            python_cmd = f"{venv_path}/bin/python"
        
        # Install the wheel
        print("\n📥 Installing package...")
        run_command(f"{python_cmd} -m pip install --quiet {wheel_path}")
        
        # Test imports
        print("\n🧪 Testing imports...")
        test_script = '''
import postcrawl
from postcrawl import PostCrawlClient, SocialPost, ExtractedPost
from postcrawl import RedditPost, TiktokPost
from postcrawl.exceptions import PostCrawlError, AuthenticationError

print(f"✅ PostCrawl version: {postcrawl.__version__}")
print(f"✅ Available exports: {len(postcrawl.__all__)}")

# Test client initialization
client = PostCrawlClient(api_key="sk_test_key")
print(f"✅ Client initialized with base URL: {client.base_url}")

# Check type hints
import typing
if hasattr(postcrawl, "__file__"):
    import os
    py_typed = os.path.join(os.path.dirname(postcrawl.__file__), "py.typed")
    if os.path.exists(py_typed):
        print("✅ py.typed marker found - type hints supported")
    else:
        print("⚠️  py.typed marker not found")
'''
        
        result = run_command(f"{python_cmd} -c '{test_script}'", check=False)
        if result.returncode != 0:
            print(f"❌ Import test failed: {result.stderr}")
            sys.exit(1)
        print(result.stdout)
        
        # Check dependencies
        print("\n📋 Checking installed dependencies...")
        deps_result = run_command(f"{python_cmd} -m pip list | grep -E 'postcrawl|pydantic|httpx|typing-extensions|python-dotenv'", check=False)
        print(deps_result.stdout)
    
    print("\n✅ All verification tests passed!")
    print("\n📤 Ready to publish to TestPyPI:")
    print("   uv publish --publish-url https://test.pypi.org/legacy/")
    print("\n📥 To test installation from TestPyPI:")
    print("   pip install -i https://test.pypi.org/simple/ postcrawl==0.1.0")
    print("\n📤 When ready for production PyPI:")
    print("   uv publish")


if __name__ == "__main__":
    main()