# 🚀 Release Guide for LLM Exo-Graph

This document explains how to create releases for the LLM Exo-Graph package using automated GitHub Actions.

## 📋 Prerequisites

Before creating releases, ensure you have:

1. **PyPI Account & API Token**
   - Create account at [pypi.org](https://pypi.org)
   - Generate API token at [PyPI Account Settings](https://pypi.org/manage/account/)
   - Add token to GitHub repository secrets as `PYPI_API_TOKEN`

2. **Test PyPI Account (Optional but Recommended)**
   - Create account at [test.pypi.org](https://test.pypi.org)
   - Generate API token
   - Add token to GitHub repository secrets as `TEST_PYPI_API_TOKEN`

3. **GitHub Repository Secrets**
   ```
   PYPI_API_TOKEN=pypi-xxxxxxxxxxxxxxxxxxxxx
   TEST_PYPI_API_TOKEN=pypi-xxxxxxxxxxxxxxxxxxxxx  # Optional
   ```

## 🏷️ Release Process

### 1. **Prepare for Release**

**Check Current Status:**
```bash
# Ensure you're on main branch
git checkout main
git pull origin main

# Check current version
python -c "
import sys
sys.path.insert(0, 'src')
from llm_exo_graph import __version__
print(f'Current version: {__version__}')
"

# Review recent changes
git log --oneline --since="1 month ago"
```

**Run Local Tests:**
```bash
# Install development dependencies
pip install -e ".[dev,test]"

# Run tests locally
pytest tests/ -v

# Check code quality
flake8 src tests
mypy src/llm_exo_graph
```

### 2. **Create and Push Version Tag**

**Semantic Versioning:**
- `v1.0.0` - Major release (breaking changes)
- `v0.1.0` - Minor release (new features, backward compatible)
- `v0.0.1` - Patch release (bug fixes)
- `v1.0.0-beta.1` - Pre-release (alpha, beta, rc)

**Create Release Tag:**
```bash
# Choose your version number (following semantic versioning)
NEW_VERSION="1.2.3"

git tag -a "v${NEW_VERSION}" -m "Release version ${NEW_VERSION}"
git push origin "v${NEW_VERSION}"
```

**Alternative: Create Tag with Release Notes:**
```bash
# Create annotated tag with detailed message
git tag -a "v1.2.3" -m "Release v1.2.3

New Features:
- Added custom encoder configuration
- Enhanced MCP integration with SSE
- Improved entity standardization

Bug Fixes:
- Fixed Neo4j connection timeout issue
- Resolved vector embedding inconsistencies

Breaking Changes:
- Changed ExoGraphEngine API structure"

git push origin "v1.2.3"
```

### 3. **Monitor Release Process**

After pushing the tag:

1. **Check GitHub Actions:**
   - Go to: `https://github.com/your-org/llm-exo-graph/actions`
   - Find your release workflow run
   - Monitor the progress through Test → Deploy stages

2. **Expected Workflow Steps:**
   ```
   ✅ Test Suite (Python 3.10, 3.11, 3.12)
   ✅ Deploy to PyPI
   ✅ Create GitHub Release
   ```

3. **Verify Deployment:**
   - **PyPI Package:** Check [pypi.org/project/llm-exo-graph/](https://pypi.org/project/llm-exo-graph/)
   - **GitHub Release:** Check repository releases page
   - **Installation Test:** `pip install llm-exo-graph==1.2.3`

## 🔍 Release Verification

After successful release:

```bash
# Test installation in clean environment
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows

# Install and test the new version
pip install llm-exo-graph==1.2.3
python -c "
import llm_exo_graph
print(f'Successfully installed v{llm_exo_graph.__version__}')

from llm_exo_graph import ExoGraphEngine
print('✅ Core imports working')
"

# Clean up
deactivate
rm -rf test_env
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

**1. Release Workflow Fails**
```bash
# Check the logs in GitHub Actions
# Common issues:
# - Test failures
# - Version format errors
# - PyPI token issues

# Fix and create new tag
git tag -d v1.2.3  # Delete local tag
git push origin :refs/tags/v1.2.3  # Delete remote tag
# Fix issues, then create new tag
git tag -a "v1.2.4" -m "Release v1.2.4 (fixed issues)"
git push origin "v1.2.4"
```

**2. PyPI Upload Fails**
```bash
# Common causes:
# - Version already exists on PyPI
# - Invalid API token
# - Package validation errors

# Solution: Increment version and retry
git tag -a "v1.2.4" -m "Release v1.2.4"
git push origin "v1.2.4"
```

**3. Test Failures**
```bash
# Run tests locally to debug
pytest tests/ -v --tb=short

# Check specific Python version issues
python3.10 -m pytest tests/
python3.11 -m pytest tests/
```

**4. Version Mismatch**
```bash
# Ensure version in code matches tag
# The workflow automatically updates src/llm_exo_graph/__init__.py
# But check manually if issues occur:

# Check current version
grep "__version__" src/llm_exo_graph/__init__.py

# Update manually if needed
sed -i 's/__version__ = ".*"/__version__ = "1.2.3"/' src/llm_exo_graph/__init__.py
```

## 📊 Release Checklist

Use this checklist for each release:

- [ ] **Pre-Release**
  - [ ] All tests passing locally
  - [ ] Documentation updated
  - [ ] CHANGELOG.md updated (if exists)
  - [ ] Version number decided (semantic versioning)
  - [ ] No uncommitted changes

- [ ] **Release**
  - [ ] Created version tag (`git tag -a "vX.Y.Z"`)
  - [ ] Pushed tag to origin (`git push origin "vX.Y.Z"`)
  - [ ] GitHub Actions workflow triggered

- [ ] **Post-Release**
  - [ ] GitHub Actions completed successfully
  - [ ] Package available on PyPI
  - [ ] GitHub release created
  - [ ] Installation test passed
  - [ ] Documentation reflects new version

## 🔄 Release Frequency

**Recommended Schedule:**
- **Patch releases** (bug fixes): As needed
- **Minor releases** (new features): Monthly or bi-monthly
- **Major releases** (breaking changes): Quarterly or when significant changes accumulate

**Version Strategy:**
- Start with `v0.1.0` for initial public release
- Use `v1.0.0` when API is stable
- Pre-releases: `v1.0.0-beta.1`, `v1.0.0-rc.1`

## 📝 Example Release Commands

**Quick Patch Release:**
```bash
git checkout main && git pull
git tag -a "v1.2.4" -m "Fix: Neo4j connection timeout"
git push origin "v1.2.4"
```

**Feature Release:**
```bash
git checkout main && git pull
git tag -a "v1.3.0" -m "Feature: Add custom encoder configuration"
git push origin "v1.3.0"
```

**Major Release:**
```bash
git checkout main && git pull
git tag -a "v2.0.0" -m "Major: New API structure and enhanced features"
git push origin "v2.0.0"
```

## 🚨 Emergency Procedures

**Hotfix Release:**
```bash
# For critical bugs that need immediate fixing
git checkout main
git pull origin main

# Apply the hotfix
git commit -m "hotfix: critical security vulnerability"

# Create patch release immediately
git tag -a "v1.2.5" -m "Hotfix: Security vulnerability patch"
git push origin main "v1.2.5"
```

**Rollback Release:**
```bash
# If a release has critical issues
# 1. Remove the problematic release from PyPI (if possible)
# 2. Create a fixed version
git revert [problematic-commit]
git tag -a "v1.2.6" -m "Rollback: Fix critical issue in v1.2.5"
git push origin "v1.2.6"
```

---

## 🎯 Summary

The automated release process:
1. **Create tag:** `git tag -a "vX.Y.Z" -m "Release vX.Y.Z"`
2. **Push tag:** `git push origin "vX.Y.Z"`
3. **Wait:** GitHub Actions handles the rest automatically
4. **Verify:** Check PyPI and GitHub releases

For questions or issues, check the GitHub Actions logs or create an issue in the repository.