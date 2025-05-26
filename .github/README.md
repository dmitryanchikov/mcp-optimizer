# GitHub Configuration

This directory contains GitHub-specific configuration files and documentation for the MCP Optimizer project.

## 📁 Directory Structure

### Workflow Files
- **`workflows/ci.yml`** - Main CI/CD pipeline for testing, building, and releasing
- **`workflows/auto-finalize-release.yml`** - Robust multi-method release detection and finalization

### Policy Documentation
- **`REPOSITORY_SETUP.md`** - Complete repository setup guide including Git Flow, branch protection, and security configuration
- **`RELEASE_PROCESS.md`** - Detailed release process from planning to publication


### Templates
- **`pull_request_template.md`** - Comprehensive PR template with checklists and guidelines

### Configuration
- **`CODEOWNERS`** - Defines code ownership and automatic review assignments

## 🔄 Git Flow Overview

Our project follows a standard Git Flow model:

```
main (production)
├── release/v1.2.0 (release preparation)
│   └── develop (integration)
│       ├── feature/new-tool (feature development)
│       ├── feature/bug-fix (bug fixes)
│       └── feature/documentation (docs updates)
└── hotfix/v1.1.1 (emergency fixes)
```

### Branch Types
- **`main`**: Production-ready code, protected
- **`develop`**: Integration branch for features
- **`feature/*`**: New features and improvements
- **`release/*`**: Release preparation and testing
- **`hotfix/*`**: Critical production fixes

## 🚀 CI/CD Pipeline

### Triggers
- **Tests**: All branches and PRs
- **Security**: All branches and PRs
- **Build**: `main`, `develop`, `release/*`, `hotfix/*`
- **Release**: Version tags on `main`
- **Release Candidates**: `release/*` branches

### Jobs
1. **Test** - Unit tests, integration tests, type checking
2. **Security** - Security scanning with Bandit
3. **Build** - Docker image building and publishing
4. **Release** - PyPI publishing and GitHub releases
5. **Release Candidate** - Pre-release builds for testing

## 📋 Contributing Workflow

1. **Fork** the repository
2. **Create** feature branch from `develop`
3. **Develop** your changes with tests
4. **Test** locally and ensure quality
5. **Submit** PR to `develop` using the template
6. **Review** process with code owners
7. **Merge** after approval and CI success

## 🛡️ Branch Protection

### `main` Branch
- Requires 2 reviewers
- All status checks must pass
- No direct pushes allowed
- Linear history required

### `develop` Branch  
- Requires 1 reviewer
- All status checks must pass
- Administrators can bypass

### `release/*` Branches
- Requires 1 reviewer
- All status checks must pass
- Builds release candidates

## 📞 Support

For questions about GitHub configuration:
- Review the policy documents in this directory
- Check existing GitHub Discussions
- Contact maintainers via issues

---

**Note**: These configurations ensure code quality, security, and proper release management for the open source project. 