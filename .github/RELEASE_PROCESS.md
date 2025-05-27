# Release Process

This document outlines the complete release process for the MCP Optimizer project, from planning to publication.

## 🎯 Release Types

### Major Release (X.0.0)
- **When**: Breaking changes, major new features, API changes
- **Planning**: Requires RFC and community discussion
- **Timeline**: Quarterly or as needed
- **Examples**: `v1.0.0`, `v2.0.0`

### Minor Release (X.Y.0)
- **When**: New features, enhancements, non-breaking changes
- **Planning**: Feature freeze 1 week before release
- **Timeline**: Monthly or bi-monthly
- **Examples**: `v1.1.0`, `v1.2.0`

### Patch Release (X.Y.Z)
- **When**: Bug fixes, security patches, documentation updates
- **Planning**: As needed
- **Timeline**: As soon as fixes are ready
- **Examples**: `v1.1.1`, `v1.2.3`

## 📅 Release Schedule

### Regular Releases
- **Minor releases**: First Monday of each month
- **Patch releases**: As needed, typically within 1-2 weeks of bug reports
- **Major releases**: Announced 4-6 weeks in advance

### Emergency Releases
- **Security patches**: Within 24-48 hours of discovery
- **Critical bugs**: Within 1 week of confirmation

## 🔒 Branch Protection & Security

### Required Branch Protection Rules

For the automated release system to work securely, the following branch protection rules **must** be configured:

#### Main Branch Protection
```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci", "security-scan", "tests"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 2,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "require_last_push_approval": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

#### Develop Branch Protection
```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci", "tests"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

#### Release/Hotfix Branch Rules
- **Naming Convention**: `release/vX.Y.Z` and `hotfix/vX.Y.Z`
- **Source Restrictions**: Release branches from `develop`, hotfix branches from `main`
- **Merge Targets**: Both types can only merge to `main` via PR
- **Auto-Delete**: Branches are automatically deleted after successful merge

### Security Implications

**Why This Approach is Secure:**
- 🔐 **No Bypass Possible**: Even repository admins cannot bypass protection rules
- 🔐 **Human Verification**: Every release requires human review and approval
- 🔐 **CI Validation**: All automated tests must pass before merge
- 🔐 **Audit Trail**: Complete GitHub audit log of all release activities
- 🔐 **Rollback Ready**: Easy to revert releases if issues are discovered

**What This Prevents:**
- ❌ Accidental releases from feature branches
- ❌ Direct pushes to main bypassing review
- ❌ Releases without proper testing
- ❌ Unauthorized version changes
- ❌ Missing or incorrect changelog entries

## 🔄 Release Workflow

### 1. Pre-Release Planning

#### Feature Freeze (Minor/Major Releases)
```bash
# 1. Announce feature freeze on develop branch
# 2. Create milestone for release
# 3. Triage remaining issues
# 4. Update project board
```

#### Release Preparation Checklist
- [ ] All planned features merged to `develop`
- [ ] All tests passing on `develop`
- [ ] Security scan completed
- [ ] Performance benchmarks run
- [ ] Documentation updated
- [ ] CHANGELOG.md prepared (see [Changelog Guidelines](../CONTRIBUTING.md#-changelog-guidelines))
- [ ] Version number decided

### 2. Release Branch Creation

#### Using Release Script (Recommended)
```bash
# Ensure you're on develop branch
git checkout develop

# Create minor release (auto-increment version)
uv run python scripts/release.py --type minor

# Or create specific version
uv run python scripts/release.py 1.2.0

# For hotfix from main
uv run python scripts/release.py --hotfix --type patch

# Dry run to preview changes
uv run python scripts/release.py --type minor --dry-run
```

#### Manual Process
```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# Update version in pyproject.toml
# Update CHANGELOG.md with release notes (see Changelog Guidelines in CONTRIBUTING.md)
# Commit changes
git add .
git commit -m "chore: prepare release v1.2.0"

# Push release branch
git push origin release/v1.2.0
```

### 3. Release Candidate Testing

#### Automated Testing
- Full test suite execution
- Integration tests
- Security scans
- Performance benchmarks
- Docker image build and test

#### Manual Testing
- [ ] Installation from source
- [ ] Basic functionality verification
- [ ] Example scripts execution
- [ ] Documentation accuracy
- [ ] Breaking change verification (if any)

#### Release Candidate Builds
```bash
# CI/CD automatically builds:
# - Docker images tagged as v1.2.0-rc.1
# - Python packages (not published to PyPI)
# - Documentation preview
```

### 4. Release Finalization - AUTOMATED

#### Create Release PR
```bash
# Create PR from release/v1.2.0 to main
gh pr create --base main --head release/v1.2.0 --title "Release v1.2.0"
```

#### PR Review Process
- [ ] Code review by maintainers
- [ ] Final testing verification
- [ ] Release notes review
- [ ] Breaking changes documentation
- [ ] Migration guide (if needed)

#### Merge PR - Automatic Finalization! 🤖
```bash
# After PR merge, automatically happens:
# ✅ Create tag v1.2.0
# ✅ Publish to PyPI
# ✅ Publish Docker images
# ✅ Create GitHub Release
# ✅ Merge main back to develop
# ✅ Cleanup release branch

# NO NEED to run finalize_release.py manually anymore!
```

#### 🔒 Secure Hybrid Release Detection

The automation uses a **simple and secure hybrid approach** that combines GitHub branch protection with automated release detection:

##### How It Works

**1. Branch Protection (Primary Security)**
- ✅ **Protected Branches**: `main` and `develop` branches are protected
- ✅ **Required Reviews**: All PRs require approval from code owners
- ✅ **Status Checks**: All CI/CD checks must pass before merge
- ✅ **No Direct Pushes**: Only PR merges allowed to `main`
- ✅ **Admin Enforcement**: Even admins must follow the rules

**2. Release Detection (Simple & Reliable)**
```bash
# Only triggers on merges from protected release branches:
# Pattern: "Merge pull request #123 from user/release/v1.2.3"
# Pattern: "Merge pull request #456 from user/hotfix/v1.2.4"
```

**3. Security Benefits**
- 🛡️ **No False Positives**: Only release/hotfix branch merges trigger automation
- 🛡️ **Human Oversight**: Every release requires PR review and approval
- 🛡️ **CI Validation**: All tests must pass before merge is possible
- 🛡️ **Audit Trail**: Complete history of who approved what and when
- 🛡️ **Rollback Safety**: Easy to revert if issues are discovered

**4. Validation Checks**
All detected releases must pass validation:
- ✅ **Version Format**: Must match semantic versioning `X.Y.Z`
- ✅ **No Duplicates**: Fails if release tag already exists
- ✅ **Branch Verification**: Must be merging to `main` branch
- ✅ **Version Consistency**: Version in branch name must match `pyproject.toml`
    B -->|Not Found| D[Check Hotfix Branch Merge]
    D -->|Found| E[Extract version, mark as hotfix]
    D -->|Not Found| F[Check Version Change]
    F -->|Changed| G[Validate Changelog Entry]
    G -->|Valid| H[Use pyproject.toml version]
    G -->|Invalid| I[Check Commit Message]
    F -->|Unchanged| I[Check Commit Message]
    I -->|Match| J[Extract version from message]
    I -->|No Match| K[Skip Release]
    
    C --> L[Validate Version Format]
    E --> L
    H --> L
    J --> L
    L -->|Valid| M[Check Tag Exists]
    L -->|Invalid| K
    M -->|New| N[Finalize Release]
    M -->|Exists| K
```

##### Benefits of Multi-Method Approach
- ✅ **99%+ Detection Rate**: Multiple fallback methods ensure reliability
- ✅ **Merge Strategy Agnostic**: Works with squash, merge, rebase strategies
- ✅ **Human Error Resistant**: Less dependent on manual commit message formatting
- ✅ **Workflow Flexible**: Supports different development styles and emergency scenarios
- ✅ **Backward Compatible**: Still supports legacy commit message format
- ✅ **Transparent**: Clear logging shows which detection method was used
- ✅ **Safe**: Multiple validation layers prevent false positives

##### Error Handling & Safety
- **Graceful Degradation**: Falls back to next detection method if one fails
- **Clear Logging**: GitHub Actions logs show detection results and reasoning
- **Failure Transparency**: Explains why detection failed with actionable guidance
- **Manual Override**: `scripts/finalize_release.py` available as backup
- **Conservative Approach**: Better to miss a release than create a false one

##### Testing & Validation
The detection system includes comprehensive testing via `scripts/test_release_detection.py`:
- Tests all detection patterns and edge cases
- Validates version format requirements
- Simulates complete detection logic
- Ensures reliability across different scenarios

#### Fallback: Manual Finalization
```bash
# If automation fails:
git checkout main
git pull origin main
uv run python scripts/finalize_release.py --version 1.2.0
```

### 5. Automated Publication

#### Triggered by Tag Creation
The CI/CD pipeline automatically:
1. **Builds final artifacts**:
   - Python wheel and source distribution
   - Docker images for multiple architectures
   - Documentation

2. **Publishes to registries**:
   - PyPI (Python Package Index)
   - GitHub Container Registry (Docker images)
   - GitHub Releases (artifacts and release notes)

3. **Updates documentation**:
   - Deploys latest docs
   - Updates version references

### 6. Post-Release Tasks - AUTOMATED

#### Automatic Tasks (executed automatically)
```bash
# ✅ Merge main back to develop (automatic)
# ✅ Delete release branch (automatic)
# ✅ Create GitHub Release (automatic)
# ✅ Publish artifacts (automatic)
```

#### Manual Tasks
```bash
# Monitor automatic finalization
gh run list --repo dmitryanchikov/mcp-optimizer --workflow="Auto-Finalize Release"

# Check publication
curl -s https://pypi.org/pypi/mcp-optimizer/json | jq '.info.version'
```

#### Communication
- [ ] Announce release on GitHub Discussions
- [ ] Update project README if needed
- [ ] Notify community channels
- [ ] Update dependent projects

#### Monitoring
- [ ] Monitor PyPI download stats
- [ ] Check for immediate bug reports
- [ ] Monitor Docker image pulls
- [ ] Review user feedback

## 📝 Release Notes Template

```markdown
# Release v1.2.0

## 🚀 New Features
- **Feature Name**: Brief description of the feature
- **Another Feature**: Description with usage example

## 🐛 Bug Fixes
- **Issue #123**: Description of the bug fix
- **Security Fix**: Description of security improvement

## 📚 Documentation
- Updated installation guide
- Added new examples for feature X

## 🔧 Internal Changes
- Updated dependencies
- Improved test coverage
- Performance optimizations

## 💥 Breaking Changes
- **API Change**: Description of breaking change and migration path
- **Configuration**: Changes to configuration format

## 📦 Dependencies
- Updated OR-Tools to v9.8.0
- Added new dependency: package-name v1.0.0

## 🙏 Contributors
Thanks to all contributors who made this release possible:
- @username1
- @username2

## 📈 Statistics
- **Commits**: 45
- **Files changed**: 23
- **Contributors**: 5
- **Issues closed**: 12

## 🔗 Links
- [Full Changelog](https://github.com/dmitryanchikov/mcp-optimizer/compare/v1.1.0...v1.2.0)
- [Documentation](https://mcp-optimizer.readthedocs.io/)
- [PyPI Package](https://pypi.org/project/mcp-optimizer/1.2.0/)
```

## 🚨 Hotfix Process

### Emergency Release Workflow
```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/v1.1.1

# 2. Fix the critical issue
# Make minimal changes to resolve the issue

# 3. Update version and changelog
# Edit pyproject.toml
# Add entry to CHANGELOG.md (see Changelog Guidelines in CONTRIBUTING.md)

# 4. Commit and push
git add .
git commit -m "fix: resolve critical security vulnerability"
git push origin hotfix/v1.1.1

# 5. Create PRs
# PR to main (for immediate release)
# PR to develop (to include fix in next release)

# 6. After merge to main, tag immediately
git checkout main
git pull origin main
git tag -a v1.1.1 -m "Hotfix v1.1.1"
git push origin v1.1.1
```

### Hotfix Criteria
- **Security vulnerabilities**: Any severity level
- **Data corruption bugs**: Critical data loss or corruption
- **Service unavailability**: Complete service failure
- **Critical performance**: >50% performance degradation

## 🔍 Quality Gates

### Pre-Release Checks
- [ ] All tests pass (unit, integration, e2e)
- [ ] Code coverage ≥ 90%
- [ ] No critical security vulnerabilities
- [ ] Performance benchmarks within acceptable range
- [ ] Documentation builds successfully
- [ ] Examples work correctly

### Release Validation
- [ ] Package installs correctly from PyPI
- [ ] Docker image runs successfully
- [ ] Basic functionality works
- [ ] No regression in performance
- [ ] Documentation is accessible

## 📊 Release Metrics

### Success Criteria
- **Installation success rate**: >95%
- **Test pass rate**: 100%
- **Documentation build**: Success
- **Security scan**: No critical issues
- **Performance**: No regression >10%

### Monitoring
- PyPI download statistics
- Docker image pull counts
- GitHub release download counts
- Issue reports post-release
- Community feedback

## 🛠️ Release Scripts and Automation

### Release Scripts
The project includes automated scripts for managing releases:

#### `scripts/release.py` - Create Release Branches
Automates creation of release or hotfix branches with proper version management.

**Usage Examples:**
```bash
# Create minor release (auto-increment from current version)
uv run python scripts/release.py --type minor

# Create specific version
uv run python scripts/release.py 1.2.0

# Create hotfix from main
uv run python scripts/release.py --hotfix --type patch

# Preview changes (dry run)
uv run python scripts/release.py --type minor --dry-run

# Skip tests (emergency use only)
uv run python scripts/release.py --skip-tests
```

#### `scripts/finalize_release.py` - Finalize Releases (AUTOMATED!)
Creates release tags and handles post-release cleanup. **Now runs automatically after PR merge!**

**Usage Examples:**
```bash
# Auto-detect version (recommended)
uv run python scripts/finalize_release.py

# Specific version
uv run python scripts/finalize_release.py --version 1.2.0

# Skip CI check (if confident CI passed)
uv run python scripts/finalize_release.py --skip-ci-check

# Keep release branch (don't cleanup)
uv run python scripts/finalize_release.py --skip-cleanup

# Preview only
uv run python scripts/finalize_release.py --dry-run
```

#### `scripts/test_release_detection.py` - Test Detection System
Comprehensive test suite for validating the hybrid release detection logic.

**Usage Examples:**
```bash
# Run all detection tests
uv run python scripts/test_release_detection.py

# Test specific patterns
python scripts/test_release_detection.py --pattern release_branch

# Validate detection logic
python scripts/test_release_detection.py --simulate
```

**Test Coverage:**
- ✅ **Branch Merge Patterns**: Tests release/* and hotfix/* branch merge detection
- ✅ **Version Validation**: Validates semantic versioning requirements
- ✅ **Edge Cases**: Tests invalid formats and non-release scenarios
- ✅ **Security Validation**: Ensures only authorized merges trigger releases
- ✅ **Regression Testing**: Ensures changes don't break detection

**When to Use:**
- Before modifying detection logic in `.github/workflows/auto-finalize-release.yml`
- After updating release scripts or workflows
- When troubleshooting release detection issues
- For validating branch protection rule changes
- During security audits of the release process

### Script Features
- **Version Management**: Auto-increment or manual version specification
- **Branch Validation**: Ensures correct source branch (develop/main)
- **Test Integration**: Runs full test suite before release
- **Git Flow Compliance**: Follows proper branching strategy
- **CI/CD Integration**: Triggers automated builds and publishing
- **Safety Checks**: Git working directory validation, version format validation

### Required Tools
- **uv**: Dependency management and packaging
- **GitHub Actions**: CI/CD automation
- **Docker**: Container builds
- **Ruff**: Code formatting and linting
- **MyPy**: Type checking
- **Pytest**: Testing framework

### Automation Features
- Automatic version bumping in `pyproject.toml`
- Automatic changelog updates
- Comprehensive test execution
- Proper Git tagging
- Branch cleanup after release
- CI/CD integration

## 📞 Support and Escalation

### Release Issues
1. **Minor issues**: Create GitHub issue
2. **Major issues**: Contact maintainers directly
3. **Security issues**: Follow security policy
4. **Emergency**: Create hotfix following emergency process

### Contacts
- **Release Manager**: @maintainer-username
- **Security Team**: security@mcp-optimizer.com
- **Community**: GitHub Discussions

## 🔧 Merge Conflict Resolution

This section covers resolving merge conflicts that may occur during the automatic merge back from `main` to `develop` after a release.

### When Conflicts Occur

Merge conflicts can happen when:
- Hotfixes were applied directly to `main`
- Parallel development occurred on `develop` during release process
- Version conflicts between release and ongoing development
- Documentation or configuration changes conflict

### Automatic Detection & Issue Creation

When a merge conflict occurs during the automated release process:

1. **Automatic Issue Creation**: A GitHub issue is automatically created with:
   - Title: `Merge conflict: release vX.Y.Z main→develop`
   - Labels: `merge-conflict`, `release`
   - Detailed resolution steps

2. **Process Halts**: The release finalization continues, but the merge back to develop fails gracefully

### Resolution via Pull Request (Required)

Since direct pushes to `develop` are prohibited by repository settings, all conflict resolution must be done via Pull Request:

#### Step 1: Create Resolution Branch
```bash
git checkout main
git pull origin main
git checkout -b merge/release-vX.Y.Z-to-develop
```

#### Step 2: Attempt Merge
```bash
git merge develop --no-ff
```

#### Step 3: Resolve Conflicts
When conflicts occur, Git will show:
```
Auto-merging file.py
CONFLICT (content): Merge conflict in file.py
Automatic merge failed; fix conflicts and then commit the result.
```

#### Step 4: Edit Conflicted Files
Open each conflicted file and look for conflict markers:
```python
<<<<<<< HEAD
# Code from main branch
def function_main_version():
    pass
=======
# Code from develop branch  
def function_develop_version():
    pass
>>>>>>> develop
```

**Resolution Strategy:**
- **Keep main changes** for bug fixes and security patches
- **Keep develop changes** for new features that don't conflict
- **Merge both** when both changes are needed
- **Consult team** for complex conflicts

#### Step 5: Complete Resolution
```bash
git add <resolved-files>
git commit -m "chore: merge release vX.Y.Z back to develop"
git push origin merge/release-vX.Y.Z-to-develop
```

#### Step 6: Create Pull Request
```bash
gh pr create \
  --base develop \
  --head merge/release-vX.Y.Z-to-develop \
  --title "Merge release vX.Y.Z back to develop" \
  --body "Resolves merge conflicts from release vX.Y.Z"
```

### Common Conflict Scenarios

#### Version Conflicts
**Problem**: `pyproject.toml` version conflicts
```toml
<<<<<<< HEAD
version = "0.3.0"
=======
version = "0.3.1-dev"
>>>>>>> develop
```

**Resolution**: Keep develop version (higher version number)
```toml
version = "0.3.1-dev"
```

#### Changelog Conflicts
**Problem**: `CHANGELOG.md` conflicts
```markdown
<<<<<<< HEAD
## [0.3.0] - 2024-01-15
=======
## [Unreleased]
- New feature in development

## [0.3.0] - 2024-01-15
>>>>>>> develop
```

**Resolution**: Merge both sections
```markdown
## [Unreleased]
- New feature in development

## [0.3.0] - 2024-01-15
```

#### Code Conflicts
**Problem**: Function/class conflicts
- **Strategy**: Prefer main branch for bug fixes
- **Strategy**: Prefer develop branch for new features
- **Strategy**: Merge both if compatible

### Prevention Strategies

#### 1. Minimize Direct Main Commits
- Use hotfix branches instead of direct commits to main
- Follow GitFlow process strictly

#### 2. Regular Sync
- Regularly merge main to develop during development
- Keep develop up-to-date with main

#### 3. Coordinate Releases
- Communicate release timing to team
- Avoid major develop changes during release process

### Getting Help

#### Automatic Support
- Check the auto-created GitHub issue for specific conflict details
- Review the GitHub Actions logs for context

#### Manual Support
- Ask in team chat for complex conflicts
- Consult with release manager for critical decisions
- Use `git log --oneline --graph` to understand branch history

#### Emergency Escalation
If conflicts are too complex or risky:
1. Create a backup branch: `git checkout -b backup-develop-$(date +%Y%m%d)`
2. Reset develop to known good state
3. Manually apply necessary changes
4. Coordinate with team for verification

### Verification After Resolution

#### 1. Run Tests
```bash
uv run pytest tests/ -v
```

#### 2. Check Linting
```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

#### 3. Verify Version
```bash
grep version pyproject.toml
```

#### 4. Check CI
Monitor GitHub Actions after merging PR to ensure all checks pass.

---

**Note**: This process is continuously improved based on community feedback and project needs. Suggestions for improvements are welcome through GitHub Discussions. 