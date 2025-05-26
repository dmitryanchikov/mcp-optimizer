# Repository Setup Guide

This guide helps repository administrators configure the MCP Optimizer repository according to our Git Flow policy.

## 🚀 Initial Setup Checklist

### 1. Create Required Branches
```bash
# Ensure main branch exists (should be default)
git checkout main

# Create develop branch from main
git checkout -b develop
git push origin develop

# Set develop as default branch for new PRs (optional)
# This can be done in GitHub Settings > Branches
```

### 2. Configure Branch Protection Rules

Navigate to **Settings** → **Branches** and add the following rules:

#### Main Branch Protection
- **Branch name pattern**: `main`
- **Require pull request reviews**: ✅ (2 reviewers)
- **Dismiss stale reviews**: ✅
- **Require review from code owners**: ✅
- **Require status checks**: ✅
  - `test (3.11)`
  - `test (3.12)`
  - `security`
  - `build`
- **Require branches to be up to date**: ✅
- **Require linear history**: ✅
- **Restrict pushes to administrators**: ✅
- **Do not allow force pushes**: ✅
- **Do not allow deletions**: ✅

#### Develop Branch Protection
- **Branch name pattern**: `develop`
- **Require pull request reviews**: ✅ (1 reviewer)
- **Dismiss stale reviews**: ✅
- **Require status checks**: ✅
  - `test (3.11)`
  - `test (3.12)`
  - `security`
- **Require branches to be up to date**: ✅
- **Allow administrators to bypass**: ✅
- **Do not allow force pushes**: ✅
- **Do not allow deletions**: ✅

#### Release Branch Protection
- **Branch name pattern**: `release/*`
- **Require pull request reviews**: ✅ (1 reviewer)
- **Require review from code owners**: ✅
- **Require status checks**: ✅
  - `test (3.11)`
  - `test (3.12)`
  - `security`
  - `build`
- **Allow administrators to bypass**: ✅
- **Allow deletions**: ✅ (for cleanup)

### 3. Configure Repository Settings

#### General Settings
Navigate to **Settings** → **General**:
- **Default branch**: `main`
- **Allow merge commits**: ✅
- **Allow squash merging**: ✅
- **Allow rebase merging**: ✅
- **Automatically delete head branches**: ✅
- **Allow auto-merge**: ✅

#### Security Settings
Navigate to **Settings** → **Security & analysis**:
- **Dependency graph**: ✅
- **Dependabot alerts**: ✅
- **Dependabot security updates**: ✅
- **Dependabot version updates**: ✅
- **Code scanning**: ✅
- **Secret scanning**: ✅
- **Secret scanning push protection**: ✅

### 4. Configure Actions

#### Actions Permissions
Navigate to **Settings** → **Actions** → **General**:
- **Actions permissions**: Allow all actions and reusable workflows
- **Fork pull request workflows**: Require approval for first-time contributors
- **Workflow permissions**: Read and write permissions

#### Required Secrets
Navigate to **Settings** → **Secrets and variables** → **Actions**:
- `PYPI_API_TOKEN` - For PyPI publishing
- `GITHUB_TOKEN` - Automatically provided

### 5. Set Up Teams and Permissions

#### Create Teams
Navigate to **Organization** → **Teams** (if using organization):
- **Maintainers** (Admin access)
- **Core Contributors** (Write access)
- **Community** (Triage access)

#### Assign Permissions
Navigate to **Settings** → **Manage access**:
- Add teams with appropriate permissions
- Ensure code owners have necessary access

### 6. Configure Issue and PR Templates

The following templates are already configured:
- `.github/pull_request_template.md` - PR template
- `.github/CODEOWNERS` - Code ownership
- `.github/ISSUE_TEMPLATE/` - Issue templates (if needed)

### 7. Verify Configuration

#### Test Branch Protection
```bash
# Try to push directly to main (should fail)
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test direct push"
git push origin main  # Should be rejected

# Clean up
git reset --hard HEAD~1
```

#### Test PR Workflow
```bash
# Create test feature branch
git checkout develop
git checkout -b feature/test-setup
echo "# Test Setup" > test-setup.md
git add test-setup.md
git commit -m "feat: add test setup file"
git push origin feature/test-setup

# Create PR to develop branch
# Verify that:
# - PR template is loaded
# - Code owners are requested for review
# - Status checks are required
# - Merge is blocked until requirements are met
```

## 🔧 Automation Scripts

### GitHub CLI Setup
```bash
#!/bin/bash
# setup-repository.sh

REPO="dmitryanchikov/mcp-optimizer"

echo "Setting up repository: $REPO"

# Create develop branch if it doesn't exist
gh api repos/$REPO/git/refs/heads/develop 2>/dev/null || {
    echo "Creating develop branch..."
    MAIN_SHA=$(gh api repos/$REPO/git/refs/heads/main --jq '.object.sha')
    gh api repos/$REPO/git/refs \
        --method POST \
        --field ref="refs/heads/develop" \
        --field sha="$MAIN_SHA"
}

# Set up branch protection for main
echo "Setting up main branch protection..."
gh api repos/$REPO/branches/main/protection \
    --method PUT \
    --field required_status_checks='{"strict":true,"contexts":["test (3.11)","test (3.12)","security","build"]}' \
    --field enforce_admins=true \
    --field required_pull_request_reviews='{"required_approving_review_count":2,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
    --field restrictions=null

# Set up branch protection for develop
echo "Setting up develop branch protection..."
gh api repos/$REPO/branches/develop/protection \
    --method PUT \
    --field required_status_checks='{"strict":true,"contexts":["test (3.11)","test (3.12)","security"]}' \
    --field enforce_admins=false \
    --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
    --field restrictions=null

echo "Repository setup complete!"
```

### Make Script Executable
```bash
chmod +x setup-repository.sh
./setup-repository.sh
```

## 📋 Post-Setup Verification

### Checklist
- [ ] `main` branch is protected
- [ ] `develop` branch is protected
- [ ] `release/*` pattern is protected
- [ ] Security features are enabled
- [ ] Actions permissions are configured
- [ ] Secrets are set up
- [ ] Teams and permissions are assigned
- [ ] Templates are working
- [ ] Test PR workflow works

### Common Issues

#### Branch Protection Not Working
- Ensure you have admin permissions
- Check that status check names match CI job names
- Verify that required contexts exist

#### CI/CD Not Triggering
- Check Actions permissions
- Verify workflow file syntax
- Ensure secrets are properly configured

#### Code Owners Not Working
- Verify CODEOWNERS file syntax
- Ensure code owners have repository access
- Check that file paths are correct

## 📞 Support

For setup issues:
- Check GitHub documentation
- Review error messages in Actions
- Contact repository maintainers
- Create issue with "infrastructure" label

---

**Note**: This setup ensures proper Git Flow implementation and maintains code quality standards for the open source project. 