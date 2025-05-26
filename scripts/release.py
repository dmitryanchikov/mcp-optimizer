#!/usr/bin/env python3
"""Release preparation script for MCP Optimizer with Git Flow support."""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def get_current_branch() -> str:
    """Get current git branch."""
    result = run_command(["git", "branch", "--show-current"])
    return result.stdout.strip()


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def update_version(new_version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    updated_content = re.sub(
        r'version = "[^"]+"', f'version = "{new_version}"', content
    )
    pyproject_path.write_text(updated_content)
    print(f"Updated version to {new_version} in pyproject.toml")


def update_changelog(version: str) -> None:
    """Update CHANGELOG.md with release date."""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print("⚠️ CHANGELOG.md not found, skipping changelog update")
        return
        
    content = changelog_path.read_text()

    # Replace [Unreleased] with version and date
    today = datetime.now().strftime("%Y-%m-%d")
    updated_content = content.replace(
        "## [Unreleased]", f"## [Unreleased]\n\n## [{version}] - {today}"
    )

    changelog_path.write_text(updated_content)
    print(f"Updated CHANGELOG.md with version {version}")


def run_tests() -> bool:
    """Run all tests to ensure everything works."""
    print("Running tests...")

    # Run unit tests
    result = run_command(["uv", "run", "pytest", "tests/", "-v"], check=False)
    if result.returncode != 0:
        print("❌ Unit tests failed!")
        print(result.stdout)
        print(result.stderr)
        return False

    # Run comprehensive tests
    result = run_command(
        ["uv", "run", "python", "tests/test_integration/comprehensive_test.py"],
        check=False,
    )
    if result.returncode != 0:
        print("❌ Comprehensive tests failed!")
        print(result.stdout)
        print(result.stderr)
        return False

    # Run linting
    result = run_command(["uv", "run", "ruff", "check", "src/"], check=False)
    if result.returncode != 0:
        print("❌ Linting failed!")
        print(result.stdout)
        print(result.stderr)
        return False

    # Run type checking
    result = run_command(["uv", "run", "mypy", "src/"], check=False)
    if result.returncode != 0:
        print("❌ Type checking failed!")
        print(result.stdout)
        print(result.stderr)
        return False

    print("✅ All tests passed!")
    return True


def check_git_status() -> bool:
    """Check if git working directory is clean."""
    result = run_command(["git", "status", "--porcelain"], check=False)
    if result.stdout.strip():
        print("❌ Git working directory is not clean!")
        print("Please commit or stash your changes before releasing.")
        return False
    return True


def ensure_on_develop() -> bool:
    """Ensure we're on develop branch."""
    current_branch = get_current_branch()
    if current_branch != "develop":
        print(f"❌ Must be on 'develop' branch, currently on '{current_branch}'")
        print("Switch to develop: git checkout develop")
        return False
    return True


def create_release_branch(version: str) -> str:
    """Create release branch from develop."""
    branch_name = f"release/v{version}"
    
    # Ensure develop is up to date
    print("Updating develop branch...")
    run_command(["git", "pull", "origin", "develop"])
    
    # Create release branch
    print(f"Creating release branch: {branch_name}")
    run_command(["git", "checkout", "-b", branch_name])
    
    return branch_name


def commit_release_changes(version: str) -> None:
    """Commit release preparation changes."""
    run_command(["git", "add", "."])
    run_command(["git", "commit", "-m", f"chore: prepare release v{version}"])
    print(f"Committed release preparation for v{version}")


def push_release_branch(branch_name: str) -> None:
    """Push release branch to origin."""
    print(f"Pushing release branch: {branch_name}")
    run_command(["git", "push", "origin", branch_name])
    print("✅ Release branch pushed to origin")
    print("CI/CD will now build release candidate")


def create_hotfix_branch(version: str) -> str:
    """Create hotfix branch from main."""
    branch_name = f"hotfix/v{version}"
    
    # Switch to main and update
    print("Switching to main branch...")
    run_command(["git", "checkout", "main"])
    run_command(["git", "pull", "origin", "main"])
    
    # Create hotfix branch
    print(f"Creating hotfix branch: {branch_name}")
    run_command(["git", "checkout", "-b", branch_name])
    
    return branch_name


def validate_version_increment(current: str, new: str, release_type: str) -> bool:
    """Validate that version increment is correct."""
    current_parts = [int(x) for x in current.split('.')]
    new_parts = [int(x) for x in new.split('.')]
    
    if release_type == "major":
        expected = [current_parts[0] + 1, 0, 0]
    elif release_type == "minor":
        expected = [current_parts[0], current_parts[1] + 1, 0]
    elif release_type == "patch":
        expected = [current_parts[0], current_parts[1], current_parts[2] + 1]
    else:
        return True  # Allow any version for manual specification
    
    if new_parts != expected:
        print(f"❌ Version increment incorrect for {release_type} release")
        print(f"Expected: {'.'.join(map(str, expected))}, got: {new}")
        return False
    
    return True


def main():
    """Main release script with Git Flow support."""
    parser = argparse.ArgumentParser(description="Prepare MCP Optimizer release with Git Flow")
    parser.add_argument("version", nargs="?", help="New version number (e.g., 0.2.0)")
    parser.add_argument("--type", choices=["major", "minor", "patch"], 
                       help="Release type (auto-calculates version)")
    parser.add_argument("--hotfix", action="store_true", 
                       help="Create hotfix branch from main")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")

    args = parser.parse_args()

    # Determine version
    current_version = get_current_version()
    
    if args.type:
        # Auto-calculate version based on type
        parts = [int(x) for x in current_version.split('.')]
        if args.type == "major":
            new_version = f"{parts[0] + 1}.0.0"
        elif args.type == "minor":
            new_version = f"{parts[0]}.{parts[1] + 1}.0"
        elif args.type == "patch":
            new_version = f"{parts[0]}.{parts[1]}.{parts[2] + 1}"
    elif args.version:
        new_version = args.version
        # Validate version format
        if not re.match(r"^\d+\.\d+\.\d+$", new_version):
            print("❌ Version must be in format X.Y.Z (e.g., 0.2.0)")
            sys.exit(1)
    else:
        print("❌ Must specify either --type or version number")
        sys.exit(1)

    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    
    # Validate version increment
    if args.type and not validate_version_increment(current_version, new_version, args.type):
        sys.exit(1)

    if args.dry_run:
        print("🔍 DRY RUN - No changes will be made")
        if args.hotfix:
            print("Steps for HOTFIX release:")
            print("1. Switch to main branch")
            print(f"2. Create hotfix branch: hotfix/v{new_version}")
            print("3. Update version and changelog")
            print("4. Run tests")
            print("5. Commit changes")
            print("6. Push hotfix branch")
            print("7. Create PR to main")
            print("8. Create PR to develop")
        else:
            print("Steps for REGULAR release:")
            print("1. Ensure on develop branch")
            print(f"2. Create release branch: release/v{new_version}")
            print("3. Update version and changelog")
            print("4. Run tests")
            print("5. Commit changes")
            print("6. Push release branch")
            print("7. CI builds release candidate")
            print("8. Create PR to main for final release")
        return

    # Check git status
    if not check_git_status():
        sys.exit(1)

    # Branch creation logic
    if args.hotfix:
        print("🚨 Creating HOTFIX release")
        branch_name = create_hotfix_branch(new_version)
    else:
        print("🚀 Creating REGULAR release")
        if not ensure_on_develop():
            sys.exit(1)
        branch_name = create_release_branch(new_version)

    # Update version and changelog
    update_version(new_version)
    update_changelog(new_version)

    # Run tests
    if not args.skip_tests:
        if not run_tests():
            print("❌ Tests failed, aborting release")
            sys.exit(1)
    else:
        print("⚠️ Skipping tests")

    # Commit changes
    commit_release_changes(new_version)

    # Push branch
    push_release_branch(branch_name)

    print(f"🎉 Release {new_version} branch created successfully!")
    print(f"\nBranch: {branch_name}")
    
    if args.hotfix:
        print("\nNext steps for HOTFIX:")
        print("1. CI/CD will run tests and build")
        print("2. Create PR to main for immediate release")
        print("3. Create PR to develop to include fix")
        print("4. After merge to main, tag will trigger production release")
    else:
        print("\nNext steps for REGULAR release:")
        print("1. CI/CD will build release candidate")
        print("2. Test the release candidate")
        print("3. Create PR to main when ready")
        print("4. After merge to main, tag will trigger production release")
        print("5. Merge main back to develop")
    
    print(f"\nRelease candidate will be available as:")
    print(f"- Docker: ghcr.io/dmitryanchikov/mcp-optimizer:{new_version}-rc")
    print(f"- GitHub Release: v{new_version}-rc.X")


if __name__ == "__main__":
    main()
