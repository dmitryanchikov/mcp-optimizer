#!/usr/bin/env python3
"""Finalize release script for MCP Optimizer - creates tags and merges back to develop."""

import argparse
import re
import subprocess
import sys
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


def check_git_status() -> bool:
    """Check if git working directory is clean."""
    result = run_command(["git", "status", "--porcelain"], check=False)
    if result.stdout.strip():
        print("❌ Git working directory is not clean!")
        print("Please commit or stash your changes before finalizing release.")
        return False
    return True


def ensure_on_main() -> bool:
    """Ensure we're on main branch."""
    current_branch = get_current_branch()
    if current_branch != "main":
        print(f"❌ Must be on 'main' branch, currently on '{current_branch}'")
        print("Switch to main: git checkout main")
        return False
    return True


def create_release_tag(version: str) -> None:
    """Create and push release tag."""
    tag_name = f"v{version}"
    
    # Ensure main is up to date
    print("Updating main branch...")
    run_command(["git", "pull", "origin", "main"])
    
    # Create annotated tag
    print(f"Creating release tag: {tag_name}")
    run_command(["git", "tag", "-a", tag_name, "-m", f"Release {version}"])
    
    # Push tag
    print(f"Pushing tag: {tag_name}")
    run_command(["git", "push", "origin", tag_name])
    
    print(f"✅ Release tag {tag_name} created and pushed")


def merge_back_to_develop(version: str) -> None:
    """Merge main back to develop to include any release fixes."""
    print("Merging main back to develop...")
    
    # Switch to develop
    run_command(["git", "checkout", "develop"])
    run_command(["git", "pull", "origin", "develop"])
    
    # Merge main
    run_command(["git", "merge", "main", "--no-ff", "-m", f"chore: merge release v{version} back to develop"])
    
    # Push develop
    run_command(["git", "push", "origin", "develop"])
    
    print("✅ Main merged back to develop")


def cleanup_release_branch(version: str) -> None:
    """Delete the release branch after successful release."""
    branch_name = f"release/v{version}"
    
    print(f"Cleaning up release branch: {branch_name}")
    
    # Delete local branch
    run_command(["git", "branch", "-d", branch_name], check=False)
    
    # Delete remote branch
    run_command(["git", "push", "origin", "--delete", branch_name], check=False)
    
    print(f"✅ Release branch {branch_name} cleaned up")


def wait_for_ci_success() -> bool:
    """Check if CI/CD pipeline is successful (simplified check)."""
    print("⚠️ Please ensure CI/CD pipeline has completed successfully before proceeding")
    print("Check: https://github.com/dmitryanchikov/mcp-optimizer/actions")
    
    response = input("Has CI/CD completed successfully? (y/N): ").lower().strip()
    return response in ['y', 'yes']


def main():
    """Main script to finalize release."""
    parser = argparse.ArgumentParser(description="Finalize MCP Optimizer release")
    parser.add_argument("--version", help="Version to finalize (auto-detected if not specified)")
    parser.add_argument("--skip-ci-check", action="store_true", help="Skip CI/CD success check")
    parser.add_argument("--skip-cleanup", action="store_true", help="Skip release branch cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")

    args = parser.parse_args()

    # Get version
    if args.version:
        version = args.version
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            print("❌ Version must be in format X.Y.Z (e.g., 0.2.0)")
            sys.exit(1)
    else:
        version = get_current_version()

    print(f"Finalizing release: v{version}")

    if args.dry_run:
        print("🔍 DRY RUN - No changes will be made")
        print("Steps that would be executed:")
        print("1. Check CI/CD success")
        print("2. Ensure on main branch")
        print("3. Check git status")
        print(f"4. Create and push tag: v{version}")
        print("5. Merge main back to develop")
        if not args.skip_cleanup:
            print(f"6. Cleanup release branch: release/v{version}")
        print("\nThis will trigger:")
        print("- PyPI package publication")
        print("- Docker image publication")
        print("- GitHub release creation")
        return

    # Check CI/CD success
    if not args.skip_ci_check:
        if not wait_for_ci_success():
            print("❌ Please wait for CI/CD to complete successfully")
            sys.exit(1)

    # Ensure on main branch
    if not ensure_on_main():
        sys.exit(1)

    # Check git status
    if not check_git_status():
        sys.exit(1)

    # Create and push release tag
    create_release_tag(version)

    print("🚀 Release tag created! CI/CD will now:")
    print("- Build and publish Python package to PyPI")
    print("- Build and publish Docker images")
    print("- Create GitHub release with artifacts")

    # Wait a moment for tag to be processed
    print("\nWaiting for tag to be processed...")
    import time
    time.sleep(5)

    # Merge back to develop
    merge_back_to_develop(version)

    # Cleanup release branch
    if not args.skip_cleanup:
        cleanup_release_branch(version)

    print(f"\n🎉 Release v{version} finalized successfully!")
    print("\nRelease artifacts will be available at:")
    print(f"- PyPI: https://pypi.org/project/mcp-optimizer/{version}/")
    print(f"- Docker: ghcr.io/dmitryanchikov/mcp-optimizer:{version}")
    print(f"- GitHub: https://github.com/dmitryanchikov/mcp-optimizer/releases/tag/v{version}")
    
    print("\nMonitor the release:")
    print("- Check GitHub Actions for deployment status")
    print("- Verify PyPI package is available")
    print("- Test Docker image pulls")


if __name__ == "__main__":
    main() 