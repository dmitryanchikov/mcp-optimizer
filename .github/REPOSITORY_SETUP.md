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

**⚠️ CRITICAL**: These protection rules are **required** for the secure automated release system to function properly.

Navigate to **Settings** → **Branches** and add the following rules:

#### Main Branch Protection
**Branch name pattern:** `main`

**Protection settings:**
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **2**
  - ✅ Dismiss stale PR approvals when new commits are pushed
  - ✅ Require review from code owners
  - ✅ Require approval of the most recent reviewable push
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - **Required status checks:**
    - `ci`
    - `security-scan` 
    - `tests`
- ✅ **Require conversation resolution before merging**
- ✅ **Require signed commits**
- ✅ **Require linear history**
- ✅ **Do not allow bypassing the above settings**
- ✅ **Restrict pushes that create files**
- ❌ Allow force pushes
- ❌ Allow deletions

#### Develop Branch Protection
**Branch name pattern:** `develop`

**Protection settings:**
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **1**
  - ✅ Dismiss stale PR approvals when new commits are pushed
  - ✅ Require review from code owners
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - **Required status checks:**
    - `ci`
    - `tests`
- ✅ **Require conversation resolution before merging**
- ✅ **Require signed commits**
- ❌ Do not allow bypassing the above settings (allow for maintainers)
- ❌ Allow force pushes
- ❌ Allow deletions

#### Release Branch Protection
**Branch name pattern:** `release/*`

**Protection settings:**
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **1**
  - ✅ Require review from code owners
- ✅ **Require status checks to pass before merging**
  - **Required status checks:**
    - `ci`
    - `tests`
    - `security-scan`
- ✅ **Require conversation resolution before merging**
- ❌ Allow force pushes
- ❌ Allow deletions

#### Hotfix Branch Protection
**Branch name pattern:** `hotfix/*`

**Protection settings:**
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **2** (higher security for hotfixes)
  - ✅ Require review from code owners
- ✅ **Require status checks to pass before merging**
  - **Required status checks:**
    - `ci`
    - `tests`
    - `security-scan`
- ✅ **Require conversation resolution before merging**
- ❌ Allow force pushes
- ❌ Allow deletions

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

#### Test Release Detection
```bash
# Create a test release branch
git checkout develop
git checkout -b release/v999.999.999
echo 'version = "999.999.999"' >> pyproject.toml
git add pyproject.toml
git commit -m "chore: prepare test release"
git push origin release/v999.999.999

# Create PR to main - should trigger detection when merged
```

### 8. Validation Checklist

- [ ] Cannot push directly to `main`
- [ ] Cannot push directly to `develop`
- [ ] PRs to `main` require 2 approvals
- [ ] PRs to `develop` require 1 approval
- [ ] All status checks must pass
- [ ] Code owner reviews are required
- [ ] Release branch merges trigger automation
- [ ] Non-release merges do not trigger automation
- [ ] Hotfix branches require 2 approvals
- [ ] Security scans are required for releases

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

#### Status Checks Not Appearing
- Ensure the workflow names in `.github/workflows/ci.yml` match the required status check names
- Verify workflows are running successfully
- Check Actions permissions

#### CI/CD Not Triggering
- Check Actions permissions
- Verify workflow file syntax
- Ensure secrets are properly configured

#### Code Owners Not Working
- Verify `.github/CODEOWNERS` file exists and is properly formatted
- Ensure code owners have repository access
- Check that file paths are correct

#### Release Detection Not Working
- Check that branch names follow exact pattern `release/vX.Y.Z` or `hotfix/vX.Y.Z`
- Verify merge commit messages contain the expected pattern
- Ensure the auto-finalize-release workflow is enabled

#### Admins Can Bypass Rules
- Ensure "Do not allow bypassing the above settings" is enabled for critical branches
- Review admin permissions and consider using teams instead

### Emergency Override

In case of emergency, repository admins can temporarily:

1. Disable branch protection
2. Make emergency changes
3. Re-enable protection immediately

**⚠️ Warning:** This should only be used in critical situations and must be documented.

## 📞 Support

For setup issues:
- Check GitHub documentation
- Review error messages in Actions
- Contact repository maintainers
- Create issue with "infrastructure" label

## 🔒 Security Benefits

This branch protection setup provides:

- **No False Positives:** Only release/hotfix branch merges trigger automation
- **Human Oversight:** Every release requires PR review and approval
- **CI Validation:** All tests must pass before merge is possible
- **Audit Trail:** Complete GitHub audit log of all activities
- **Rollback Safety:** Easy to revert if issues discovered
- **Admin Enforcement:** Even repository admins cannot bypass protection rules

---

**Note**: This setup ensures proper Git Flow implementation, maintains code quality standards, and provides secure automated release detection for the open source project. 