#!/usr/bin/env python3
"""
Test runner for Authorization Service
"""
import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run all authorization service tests."""
    project_root = Path(__file__).parent.parent.parent
    auth_tests_dir = project_root / "authorization_service" / "tests"

    print("Running Authorization Service tests...")
    print(f"Test directory: {auth_tests_dir}")

    # Run tests with unittest
    result = subprocess.run([
        sys.executable, "-m", "unittest", "discover",
        "-s", str(auth_tests_dir),
        "-p", "test_*.py",
        "-v"
    ], cwd=str(project_root))

    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)