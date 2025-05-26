#!/usr/bin/env python3
"""Release preparation script for MCP Optimizer."""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


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
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content
    )
    pyproject_path.write_text(updated_content)
    print(f"Updated version to {new_version} in pyproject.toml")


def update_changelog(version: str) -> None:
    """Update CHANGELOG.md with release date."""
    changelog_path = Path("CHANGELOG.md")
    content = changelog_path.read_text()
    
    # Replace [Unreleased] with version and date
    today = datetime.now().strftime("%Y-%m-%d")
    updated_content = content.replace(
        "## [Unreleased]",
        f"## [Unreleased]\n\n## [{version}] - {today}"
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
        check=False
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


def build_package() -> bool:
    """Build the Python package."""
    print("Building package...")
    
    # Clean previous builds
    run_command(["rm", "-rf", "dist/"], check=False)
    
    # Build package
    result = run_command(["uv", "build"], check=False)
    if result.returncode != 0:
        print("❌ Package build failed!")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print("✅ Package built successfully!")
    return True


def build_docker_image(version: str) -> bool:
    """Build Docker image."""
    print("Building Docker image...")
    
    result = run_command([
        "docker", "build", 
        "-t", f"mcp-optimizer:{version}",
        "-t", "mcp-optimizer:latest",
        "."
    ], check=False)
    
    if result.returncode != 0:
        print("❌ Docker build failed!")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print("✅ Docker image built successfully!")
    return True


def check_git_status() -> bool:
    """Check if git working directory is clean."""
    result = run_command(["git", "status", "--porcelain"], check=False)
    if result.stdout.strip():
        print("❌ Git working directory is not clean!")
        print("Please commit or stash your changes before releasing.")
        return False
    return True


def create_git_tag(version: str) -> None:
    """Create and push git tag."""
    tag_name = f"v{version}"
    
    # Create tag
    run_command(["git", "add", "."])
    run_command(["git", "commit", "-m", f"chore: release version {version}"])
    run_command(["git", "tag", "-a", tag_name, "-m", f"Release {version}"])
    
    print(f"Created git tag {tag_name}")
    print("To push the tag, run: git push origin main --tags")


def main():
    """Main release script."""
    parser = argparse.ArgumentParser(description="Prepare MCP Optimizer release")
    parser.add_argument("version", help="New version number (e.g., 0.2.0)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker build")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', args.version):
        print("❌ Version must be in format X.Y.Z (e.g., 0.2.0)")
        sys.exit(1)
    
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    print(f"New version: {args.version}")
    
    if args.dry_run:
        print("🔍 DRY RUN - No changes will be made")
        print("Steps that would be executed:")
        print("1. Check git status")
        print("2. Run tests (if not skipped)")
        print("3. Update version in pyproject.toml")
        print("4. Update CHANGELOG.md")
        print("5. Build Python package")
        print("6. Build Docker image (if not skipped)")
        print("7. Create git tag")
        return
    
    # Check git status
    if not check_git_status():
        sys.exit(1)
    
    # Run tests
    if not args.skip_tests:
        if not run_tests():
            sys.exit(1)
    else:
        print("⚠️ Skipping tests")
    
    # Update version
    update_version(args.version)
    
    # Update changelog
    update_changelog(args.version)
    
    # Build package
    if not build_package():
        sys.exit(1)
    
    # Build Docker image
    if not args.skip_docker:
        if not build_docker_image(args.version):
            sys.exit(1)
    else:
        print("⚠️ Skipping Docker build")
    
    # Create git tag
    create_git_tag(args.version)
    
    print(f"🎉 Release {args.version} prepared successfully!")
    print("\nNext steps:")
    print("1. Review the changes")
    print("2. Push to GitHub: git push origin main --tags")
    print("3. Create GitHub release from the tag")
    print("4. Publish to PyPI: uv publish")
    print("5. Push Docker image to registry")


if __name__ == "__main__":
    main() 