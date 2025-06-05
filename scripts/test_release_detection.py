#!/usr/bin/env python3
"""Test script for release detection logic."""

import re


def test_detection_patterns():
    """Test various commit message patterns for release detection."""

    test_cases = [
        # Release branch merges
        {
            "message": "Merge pull request #123 from user/release/v1.2.3",
            "expected_type": "release_branch",
            "expected_version": "1.2.3"
        },
        {
            "message": "Merge pull request #456 from dmitryanchikov/release/v2.0.0",
            "expected_type": "release_branch",
            "expected_version": "2.0.0"
        },

        # Hotfix branch merges
        {
            "message": "Merge pull request #789 from user/hotfix/v1.1.1",
            "expected_type": "hotfix_branch",
            "expected_version": "1.1.1"
        },

        # Commit message patterns
        {
            "message": "chore: prepare release v1.3.0",
            "expected_type": "commit_message",
            "expected_version": "1.3.0"
        },

        # Non-release messages
        {
            "message": "feat: add new optimization algorithm",
            "expected_type": "none",
            "expected_version": None
        },
        {
            "message": "Merge pull request #999 from user/feature/new-solver",
            "expected_type": "none",
            "expected_version": None
        }
    ]

    print("🧪 Testing Release Detection Patterns")
    print("=" * 50)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['message'][:50]}...")

        # Test release branch pattern
        release_match = re.search(r"Merge pull request #\d+ from [^/]+/release/v([0-9]+\.[0-9]+\.[0-9]+)", test['message'])

        # Test hotfix branch pattern
        hotfix_match = re.search(r"Merge pull request #\d+ from [^/]+/hotfix/v([0-9]+\.[0-9]+\.[0-9]+)", test['message'])

        # Test commit message pattern
        commit_match = re.search(r'chore: prepare release v([0-9]+\.[0-9]+\.[0-9]+)', test['message'])

        detected_type = "none"
        detected_version = None

        if release_match:
            detected_type = "release_branch"
            detected_version = release_match.group(1)
        elif hotfix_match:
            detected_type = "hotfix_branch"
            detected_version = hotfix_match.group(1)
        elif commit_match:
            detected_type = "commit_message"
            detected_version = commit_match.group(1)

        # Check results
        type_match = detected_type == test['expected_type']
        version_match = detected_version == test['expected_version']

        status = "✅ PASS" if (type_match and version_match) else "❌ FAIL"

        print(f"  Expected: {test['expected_type']} v{test['expected_version']}")
        print(f"  Detected: {detected_type} v{detected_version}")
        print(f"  Result: {status}")


def test_version_validation():
    """Test version format validation."""

    print("\n\n🔍 Testing Version Validation")
    print("=" * 50)

    test_versions = [
        ("1.2.3", True),
        ("0.1.0", True),
        ("10.20.30", True),
        ("1.2", False),
        ("1.2.3.4", False),
        ("v1.2.3", False),
        ("1.2.3-rc", False),
        ("1.2.3-alpha.1", False),
        ("", False),
        ("abc", False)
    ]

    version_pattern = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")

    for version, expected in test_versions:
        is_valid = bool(version_pattern.match(version))
        status = "✅ PASS" if (is_valid == expected) else "❌ FAIL"

        print(f"  {version:15} -> {is_valid:5} (expected {expected:5}) {status}")


def simulate_detection_logic():
    """Simulate the complete detection logic."""

    print("\n\n🎯 Simulating Complete Detection Logic")
    print("=" * 50)

    # Simulate different scenarios
    scenarios = [
        {
            "name": "Standard Release",
            "merge_msg": "Merge pull request #123 from user/release/v1.2.0",
            "current_version": "1.2.0",
            "previous_version": "1.1.0",
            "changelog_entry": True
        },
        {
            "name": "Hotfix Release",
            "merge_msg": "Merge pull request #456 from user/hotfix/v1.1.1",
            "current_version": "1.1.1",
            "previous_version": "1.1.0",
            "changelog_entry": True
        },
        {
            "name": "Version Bump Only",
            "merge_msg": "feat: add new feature",
            "current_version": "1.3.0",
            "previous_version": "1.2.0",
            "changelog_entry": True
        },
        {
            "name": "Commit Message Fallback",
            "merge_msg": "chore: prepare release v1.4.0",
            "current_version": "1.4.0",
            "previous_version": "1.3.0",
            "changelog_entry": False
        },
        {
            "name": "No Release",
            "merge_msg": "feat: add new feature",
            "current_version": "1.2.0",
            "previous_version": "1.2.0",
            "changelog_entry": False
        }
    ]

    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")

        # Method 1: Release branch merge
        release_match = re.search(r"Merge pull request #\d+ from [^/]+/release/v([0-9]+\.[0-9]+\.[0-9]+)", scenario['merge_msg'])

        # Method 2: Hotfix branch merge
        hotfix_match = re.search(r"Merge pull request #\d+ from [^/]+/hotfix/v([0-9]+\.[0-9]+\.[0-9]+)", scenario['merge_msg'])

        # Method 3: Version change + changelog
        version_changed = scenario['current_version'] != scenario['previous_version']
        has_changelog = scenario['changelog_entry']

        # Method 4: Commit message
        commit_match = re.search(r'chore: prepare release v([0-9]+\.[0-9]+\.[0-9]+)', scenario['merge_msg'])

        # Determine result
        if release_match:
            result = f"✅ Release detected via branch merge: v{release_match.group(1)}"
        elif hotfix_match:
            result = f"🚨 Hotfix detected via branch merge: v{hotfix_match.group(1)}"
        elif version_changed and has_changelog:
            result = f"✅ Release detected via version change: v{scenario['current_version']}"
        elif commit_match:
            result = f"✅ Release detected via commit message: v{commit_match.group(1)}"
        else:
            result = "ℹ️ No release detected"

        print(f"  {result}")


def main():
    """Run all tests."""
    print("🚀 MCP Optimizer Release Detection Tests")
    print("=" * 60)

    test_detection_patterns()
    test_version_validation()
    simulate_detection_logic()

    print("\n\n✅ All tests completed!")
    print("\n💡 This logic is implemented in:")
    print("   .github/workflows/auto-finalize-release.yml")


if __name__ == "__main__":
    main()
