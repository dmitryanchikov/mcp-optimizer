## 📋 Pull Request Description

### Summary
<!-- Provide a brief summary of the changes in this PR -->

### Type of Change
<!-- Mark the relevant option with an "x" -->
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update (changes to documentation only)
- [ ] 🔧 Refactoring (code changes that neither fix a bug nor add a feature)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test addition or improvement
- [ ] 🔨 Build/CI changes
- [ ] 🎨 Style changes (formatting, missing semi colons, etc)

### Related Issues
<!-- Link to related issues using keywords like "Fixes #123", "Closes #456", "Relates to #789" -->
- Fixes #
- Closes #
- Relates to #

## 🔄 Branch Information

### Source Branch
<!-- Specify the source branch for this PR -->
- **From**: `feature/branch-name` | `hotfix/branch-name` | `release/vX.Y.Z`

### Target Branch
<!-- Specify the target branch for this PR -->
- **To**: `main` | `develop`

### Branch Type Validation
<!-- Confirm the PR follows the correct Git Flow pattern -->
- [ ] Feature branch → `develop`
- [ ] Release branch → `main`
- [ ] Hotfix branch → `main` (and separate PR to `develop`)
- [ ] Documentation/chore → `develop`

## 🧪 Testing

### Test Coverage
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All existing tests pass
- [ ] New tests cover the changes
- [ ] Manual testing completed

### Test Results
<!-- Provide test results or link to CI/CD results -->
```bash
# Paste test results here or link to CI/CD run
```

### Manual Testing Checklist
- [ ] Feature works as expected
- [ ] No regression in existing functionality
- [ ] Error handling works correctly
- [ ] Performance is acceptable
- [ ] Documentation examples work

## 📚 Documentation

### Documentation Updates
- [ ] Code comments added/updated
- [ ] API documentation updated
- [ ] README.md updated (if needed)
- [ ] CHANGELOG.md updated (see [Changelog Guidelines](../CONTRIBUTING.md#-changelog-guidelines))
- [ ] Examples updated/added
- [ ] Migration guide provided (for breaking changes)

### Documentation Links
<!-- Provide links to relevant documentation -->
- API docs: 
- Examples: 
- Migration guide: 

## 🔍 Code Quality

### Code Review Checklist
- [ ] Code follows project style guidelines
- [ ] Code is self-documenting with clear variable/function names
- [ ] Complex logic is commented
- [ ] No hardcoded values (use constants/config)
- [ ] Error handling is appropriate
- [ ] Security considerations addressed
- [ ] Performance implications considered

### Static Analysis
- [ ] Linting passes (`ruff check`)
- [ ] Formatting is correct (`ruff format`)
- [ ] Type checking passes (`mypy`)
- [ ] Security scan passes (`bandit`)
- [ ] No new warnings introduced

## 🚀 Deployment

### Deployment Considerations
- [ ] Database migrations included (if applicable)
- [ ] Configuration changes documented
- [ ] Environment variables updated
- [ ] Dependencies updated in requirements
- [ ] Backward compatibility maintained
- [ ] Rollback plan considered

### Release Notes
<!-- For release branches, provide release notes -->
```markdown
### New Features
- 

### Bug Fixes
- 

### Breaking Changes
- 

### Dependencies
- 
```

## 🔒 Security

### Security Checklist
- [ ] No sensitive data exposed
- [ ] Input validation implemented
- [ ] Authentication/authorization considered
- [ ] Dependencies are secure
- [ ] No hardcoded secrets
- [ ] Security scan passes

### Security Impact
<!-- Describe any security implications -->
- **Impact**: None | Low | Medium | High
- **Description**: 

## 📊 Performance

### Performance Impact
- [ ] No performance regression
- [ ] Performance improvements measured
- [ ] Memory usage considered
- [ ] Database query optimization (if applicable)
- [ ] Caching strategy implemented (if applicable)

### Benchmarks
<!-- Provide performance benchmarks if applicable -->
```
Before: 
After: 
Improvement: 
```

## 🎯 Reviewer Guidelines

### Focus Areas
<!-- Guide reviewers on what to focus on -->
- [ ] Logic correctness
- [ ] Error handling
- [ ] Performance implications
- [ ] Security considerations
- [ ] API design
- [ ] Documentation clarity

### Review Checklist for Reviewers
- [ ] Code is readable and maintainable
- [ ] Tests are comprehensive
- [ ] Documentation is accurate
- [ ] No obvious bugs or issues
- [ ] Follows project conventions
- [ ] Security best practices followed

## 📝 Additional Notes

### Implementation Details
<!-- Provide any additional context about the implementation -->

### Known Limitations
<!-- List any known limitations or future improvements needed -->

### Dependencies
<!-- List any new dependencies or version updates -->

### Migration Instructions
<!-- For breaking changes, provide migration instructions -->

---

## ✅ Pre-Merge Checklist

### Author Checklist
- [ ] All tests pass locally
- [ ] Code is properly formatted
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (see [Changelog Guidelines](../CONTRIBUTING.md#-changelog-guidelines))
- [ ] Commit messages follow conventional format
- [ ] Branch is up to date with target branch
- [ ] No merge conflicts
- [ ] Self-review completed

### Reviewer Checklist
- [ ] Code review completed
- [ ] Tests reviewed and adequate
- [ ] Documentation reviewed
- [ ] Security considerations reviewed
- [ ] Performance impact assessed
- [ ] Breaking changes identified and documented

### Maintainer Checklist
- [ ] CI/CD pipeline passes
- [ ] Security scan passes
- [ ] Performance benchmarks acceptable
- [ ] Documentation builds successfully
- [ ] Release notes updated (if applicable)
- [ ] Ready for merge

---

**Note**: Please ensure all checkboxes are completed before requesting review. For urgent hotfixes, mark the PR with the "urgent" label and notify maintainers directly. 