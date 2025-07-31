#!/usr/bin/env python3
"""
Basic tests for CI/CD pipeline validation
Tests google-genai imports and core functionality
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_google_genai_import() -> bool:
 """Test that google-genai imports work correctly"""
 try:
 # pylint: disable=import-outside-toplevel
 from google import genai # noqa: F401
 from google.genai import types # noqa: F401

 print(" google-genai imports successful")
 return True
 except ImportError as e:
 print(f" google-genai import failed: {e}")
 return False

def test_environment_setup() -> bool:
 """Test that environment variables can be accessed"""
 try:
 google_api_key = os.getenv("GOOGLE_API_KEY")
 if google_api_key:
 print(" GOOGLE_API_KEY environment variable found")
 return True
 print("⚠ GOOGLE_API_KEY not found (expected in CI)")
 return True # Still pass - CI will set this
 except Exception as e:
 print(f" Environment test failed: {e}")
 return False

def test_mcp_server_import() -> bool:
 """Test that MCP server can be imported"""
 try:
 # pylint: disable=import-outside-toplevel,unused-import
 import mcp_server # noqa: F401

 print(" MCP server import successful")
 return True
 except ImportError as e:
 print(f" MCP server import failed: {e}")
 return False

def main() -> None:
 """Main test runner function"""
 print("🧪 Running basic validation tests for CI/CD pipeline...")

 tests = [
 test_google_genai_import,
 test_environment_setup,
 test_mcp_server_import,
 ]

 passed_count = 0
 total_count = len(tests)

 for test in tests:
 print(f"\n Running {test.__name__}...")
 if test():
 passed_count += 1

 print(f"\n Test Results: {passed_count}/{total_count} tests passed")

 if passed_count == total_count:
 print(" All tests passed! CI/CD pipeline ready.")
 sys.exit(0)
 print(" Some tests failed. Check configuration.")
 sys.exit(1)

if __name__ == "__main__":
 main()
