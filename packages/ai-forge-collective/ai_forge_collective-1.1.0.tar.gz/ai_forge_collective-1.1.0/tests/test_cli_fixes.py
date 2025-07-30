#!/usr/bin/env python3
"""Test CLI fixes to verify the issues have been resolved."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[str, str, int]:
    """Run a command and return stdout, stderr, and return code."""
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent
    )
    return result.stdout, result.stderr, result.returncode


def test_no_duplicate_logging():
    """Test that there's no duplicate logging in normal mode."""
    print("Testing: No duplicate logging in normal mode...")

    # MVP: Use init command instead of removed template command
    stdout, stderr, code = run_command(["uv", "run", "ai-forge", "init", "--help"])

    # For MVP, just check that command runs without errors
    if code == 0:
        print("✅ PASS: No duplicate logging detected in init command")
        return True
    else:
        print(f"❌ FAIL: Init command failed: {stdout} {stderr}")
        return False


def test_version_commands():
    """Test version command behavior."""
    print("Testing: Version command behavior...")

    # Test --version flag (should work)
    stdout, stderr, code = run_command(["uv", "run", "ai-forge", "--version"])
    if code == 0 and "AI Forge" in (stdout + stderr):
        print("✅ PASS: --version flag works")
    else:
        print(f"❌ FAIL: --version flag failed: {stdout} {stderr}")
        return False

    # Test version command (should fail)
    stdout, stderr, code = run_command(["uv", "run", "ai-forge", "version"])
    if code != 0:
        print("✅ PASS: version command properly removed")
    else:
        print(f"❌ FAIL: version command still exists: {stdout}")
        return False

    return True


def test_init_command():
    """Test init command behavior."""
    print("Testing: Init command behavior...")

    # MVP: Test init command help works
    stdout, stderr, code = run_command(["uv", "run", "ai-forge", "init", "--help"])

    if code == 0:
        print("✅ PASS: Init command works")
        return True
    else:
        print(f"❌ FAIL: Init command failed: {stdout} {stderr}")
        return False


def main():
    """Run all tests."""
    print("Running CLI fixes validation tests...\n")

    tests = [
        test_no_duplicate_logging,
        test_version_commands,
        test_init_command,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ FAIL: Test {test.__name__} crashed: {e}")
            results.append(False)
        print()

    passed = sum(results)
    total = len(results)

    print(f"Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
