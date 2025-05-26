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
- [ ] CHANGELOG.md prepared
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
# Update CHANGELOG.md with release notes
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
# Add entry to CHANGELOG.md

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

---

**Note**: This process is continuously improved based on community feedback and project needs. Suggestions for improvements are welcome through GitHub Discussions. 