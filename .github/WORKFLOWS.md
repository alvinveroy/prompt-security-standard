# GitHub Actions Workflows

This document describes the automated CI/CD workflows for the UPSS project.

## Overview

The project uses three main GitHub Actions workflows:

1. **Python CI** - Continuous Integration for pull requests
2. **Python Publish** - Automated PyPI package publication
3. **Zenodo Metadata Update** - Automated DOI and metadata management

---

## 1. Python CI Workflow

**File**: `.github/workflows/python-ci.yml`

### Purpose

Ensures code quality and correctness for all Python changes through automated testing and validation.

### Triggers

- **Pull Requests** to `main` or `develop` branches
- **Push** to `main` or `develop` branches
- **Manual** dispatch via GitHub Actions UI

Only triggers when files change in:
- `implementations/python/**`
- `.github/workflows/python-ci.yml`

### Jobs

#### 1. Lint and Format Check

**Purpose**: Verify code style and formatting consistency

**Tools**:
- **Black**: Code formatter (line length: 88)
- **isort**: Import statement sorter
- **Flake8**: Style guide enforcement (PEP 8)

**Configuration**:
```toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311', 'py312']

[tool.isort]
profile = "black"
line_length = 88
```

**To fix locally**:
```bash
cd implementations/python
black upss/
isort upss/
flake8 upss/
```

#### 2. Type Checking

**Purpose**: Static type analysis

**Tool**: **mypy**

**Configuration**:
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**To check locally**:
```bash
cd implementations/python
mypy upss/ --ignore-missing-imports
```

#### 3. Test Suite

**Purpose**: Run tests across multiple Python versions

**Matrix**:
- Python 3.9, 3.10, 3.11, 3.12

**Tool**: **pytest** with **pytest-cov**

**Coverage Requirements**:
- Minimum: 80%
- Target: 95%+

**Configuration**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --cov=upss --cov-report=html --cov-report=term"
```

**To run locally**:
```bash
cd implementations/python
pytest tests/ -v --cov=upss --cov-report=html
```

View coverage report: `implementations/python/htmlcov/index.html`

#### 4. Security Checks

**Purpose**: Identify security vulnerabilities

**Tools**:
- **Safety**: Dependency vulnerability scanner
- **Bandit**: Python security linter

**To check locally**:
```bash
cd implementations/python
pip install safety bandit
pip freeze > requirements.txt
safety check --file requirements.txt
bandit -r upss/
```

#### 5. Build Check

**Purpose**: Verify package can be built and distributed

**Tools**:
- **build**: PEP 517 build tool
- **twine**: Package validation

**To check locally**:
```bash
cd implementations/python
python -m pip install build twine
python -m build
twine check dist/*
```

#### 6. CI Summary

**Purpose**: Aggregate all check results

Displays a summary table with pass/fail status for all jobs.

### Quality Gates

All jobs must pass for PR approval:
- ✅ Lint & Format
- ✅ Type Checking
- ✅ Tests (all Python versions)
- ✅ Security Checks
- ✅ Build Validation

### Artifacts

Generated artifacts (retained 7 days):
- `test-results-py{version}` - JUnit XML and HTML coverage
- `mypy-report` - Type checking report
- `security-reports` - Bandit JSON report
- `python-dist-packages` - Built wheel and sdist

---

## 2. Python Publish Workflow

**File**: `.github/workflows/python-publish.yml`

### Purpose

Automates the publication of the UPSS Python package to PyPI.

### Triggers

#### Git Tags
```bash
git tag -a python-v1.2.3 -m "Release Python UPSS v1.2.3"
git push origin python-v1.2.3
```

**Pattern**: `python-v*` (e.g., `python-v1.2.3`, `python-v2.0.0-beta.1`)

#### Manual Dispatch
Via GitHub Actions UI with version input (e.g., `1.2.3`)

### Jobs

#### 1. Validate Version

**Purpose**: Ensure version follows semantic versioning

**Validation**:
- Format: `MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]`
- Examples: `1.0.0`, `2.1.0-beta.1`, `3.0.0-rc.1+build.123`

**Pre-release Detection**:
Automatically detects pre-releases (containing `-`, `alpha`, `beta`, `rc`)

#### 2. Update Version Files

**Purpose**: Automatically bump version in project files

**Updated Files**:

1. **`implementations/python/pyproject.toml`**
   ```toml
   [project]
   version = "X.Y.Z"
   ```

2. **`implementations/python/CHANGELOG.md`**
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD
   
   ### Changed
   - Version bump to X.Y.Z
   ```

**Commit Message**:
```
chore(python): bump version to X.Y.Z [skip ci]
```

**Note**: The `[skip ci]` tag prevents infinite workflow loops.

#### 3. Test

**Purpose**: Run full test suite before publishing

**Matrix**: Python 3.9, 3.10, 3.11, 3.12

**Steps**:
- Linting (flake8)
- Type checking (mypy)
- Unit tests with coverage
- Coverage upload to Codecov

#### 4. Build

**Purpose**: Create distribution packages

**Outputs**:
- Source distribution (`upss-X.Y.Z.tar.gz`)
- Wheel distribution (`upss-X.Y.Z-py3-none-any.whl`)

**Validation**: `twine check` ensures package metadata is valid

#### 5. Publish to PyPI

**Purpose**: Upload package to Python Package Index

**Method**: PyPA official GitHub Action with **Trusted Publishing** (OIDC)

**Security**:
- No API tokens required
- Uses GitHub's OIDC identity
- Automatic provenance generation
- SLSA attestation

**Setup Required** (one-time):
1. Go to PyPI project settings
2. Enable "Trusted Publishing"
3. Configure GitHub as publisher:
   - Owner: `alvinveroy`
   - Repository: `prompt-security-standard`
   - Workflow: `python-publish.yml`
   - Environment: `pypi`

**Environment**: `pypi` (configured in repository settings)

#### 6. Create GitHub Release

**Purpose**: Document release on GitHub

**Details**:
- Tag: `python-vX.Y.Z`
- Title: `Python UPSS vX.Y.Z`
- Body: Extracted from CHANGELOG.md
- Assets: Distribution packages (wheel + sdist)
- Pre-release: Automatically set for versions with `-` suffix

### Usage

#### Standard Release

```bash
# Ensure on main branch and up-to-date
git checkout main
git pull origin main

# Run tests locally
cd implementations/python
pytest tests/ -v --cov=upss

# Code quality checks
black --check upss/
flake8 upss/
mypy upss/

# Create and push tag
git tag -a python-v2.1.0 -m "Release Python UPSS v2.1.0"
git push origin python-v2.1.0

# Monitor workflow
# Visit: https://github.com/upss-standard/universal-prompt-security-standard/actions
```

#### Pre-release

```bash
# Create pre-release tag
git tag -a python-v2.1.0-beta.1 -m "Pre-release Python UPSS v2.1.0-beta.1"
git push origin python-v2.1.0-beta.1

# Will be marked as pre-release on both PyPI and GitHub
```

### Verification

After workflow completes:

1. **PyPI**: https://pypi.org/project/upss/
2. **GitHub Releases**: https://github.com/upss-standard/universal-prompt-security-standard/releases
3. **Test Installation**:
   ```bash
   pip install upss==X.Y.Z
   python -c "import upss; print(upss.__version__)"
   ```

---

## 3. Zenodo Metadata Update Workflow

**File**: `.github/workflows/zenodo-metadata-update.yml`

### Purpose

Automates DOI minting and metadata updates for UPSS standard releases (not Python library releases).

### Triggers

#### Git Tags (Recommended)
```bash
git tag -a v1.2.0 -m "Release UPSS Standard v1.2.0"
git push origin v1.2.0
```

**Pattern**:
- ✅ `v*` - Standard releases (e.g., `v1.0.0`, `v1.2.0`)
- ❌ `v*-*` - Pre-releases (e.g., `v1.0.0-beta`, `v1.0.0-rc.1`)
- ❌ `python-v*` - Python library tags (e.g., `python-v2.0.0`)

#### GitHub Release Published
Creating a release via GitHub UI also triggers the workflow.

### Jobs

#### Update Zenodo

**Steps**:

1. **Extract Release Information**
   - Version from tag (e.g., `v1.2.0` → `1.2.0`)
   - Release date (UTC)

2. **Update CITATION.cff**
   ```yaml
   version: 1.2.0
   date-released: 2025-10-30
   ```

3. **Update README.md**
   ```markdown
   **Version:** 1.2.0
   **Last Updated:** October 30, 2025
   ```

4. **Update CHANGELOG.md**
   - Extracts release notes from GitHub release body
   - Inserts new version section after "Unreleased"
   - Adds comparison link

5. **Commit Version Updates**
   ```
   chore(release): update version to v1.2.0 [skip ci]
   ```
   Pushes to `main` branch

6. **Prepare Zenodo Metadata**
   - Loads `config/zenodo/metadata.json`
   - Replaces placeholders:
     - `{{VERSION}}` → version
     - `{{PUBLICATION_DATE}}` → date
     - `{{RELEASE_BODY}}` → release notes

7. **Update Zenodo Deposition**
   - Creates new version on Zenodo
   - Handles existing drafts (deletes if necessary)
   - Updates metadata
   - Publishes new version
   - Generates new DOI

### Configuration

#### Required Secrets

Set in repository settings (`Settings → Secrets → Actions`):

```yaml
ZENODO_ACCESS_TOKEN:     # Personal access token from Zenodo
ZENODO_DEPOSITION_ID:    # ID of the Zenodo record
```

**Getting Zenodo Token**:
1. Log into Zenodo (https://zenodo.org)
2. Go to Account → Applications → Personal access tokens
3. Create new token with scopes: `deposit:actions`, `deposit:write`
4. Copy token to GitHub repository secret

**Getting Deposition ID**:
1. Create initial record on Zenodo manually
2. Extract ID from record URL: `zenodo.org/deposit/XXXXXXX`
3. Add to GitHub repository secret

#### Metadata Template

**File**: `config/zenodo/metadata.json`

Example:
```json
{
  "metadata": {
    "title": "Universal Prompt Security Standard (UPSS)",
    "upload_type": "software",
    "publication_date": "{{PUBLICATION_DATE}}",
    "version": "{{VERSION}}",
    "description": "...",
    "creators": [...],
    "keywords": [...],
    "license": "MIT",
    ...
  }
}
```

**Placeholders**:
- `{{VERSION}}` - Replaced with release version
- `{{PUBLICATION_DATE}}` - Replaced with release date
- `{{RELEASE_BODY}}` - Replaced with GitHub release notes

### Usage

#### Creating a Standard Release

```bash
# Ensure on main and updated
git checkout main
git pull origin main

# Update relevant documentation if needed
# - README.md
# - docs/specification.md
# - CHANGELOG.md

# Commit changes
git add .
git commit -m "docs: update for v1.2.0 release"
git push origin main

# Create tag
git tag -a v1.2.0 -m "Release UPSS Standard v1.2.0"
git push origin v1.2.0

# OR create via GitHub UI:
# Go to Releases → Draft a new release
# Create tag: v1.2.0
# Fill in release notes
# Publish release
```

#### Monitoring

1. Go to GitHub Actions
2. Watch "Update Zenodo Metadata" workflow
3. Check for successful completion
4. Verify new DOI in workflow output

#### Verification

1. **GitHub**: Check updated files (CITATION.cff, README.md, CHANGELOG.md)
2. **Zenodo**: Visit Zenodo record for new version
3. **DOI**: Test new DOI resolves correctly

---

## Security Best Practices

### 1. Secrets Management

**DO**:
- ✅ Use OIDC/Trusted Publishers (PyPI)
- ✅ Rotate tokens annually
- ✅ Use minimal required scopes
- ✅ Store secrets in GitHub encrypted storage
- ✅ Use environment-specific secrets

**DON'T**:
- ❌ Commit tokens to repository
- ❌ Share tokens between projects
- ❌ Use overly permissive scopes
- ❌ Log secrets in workflow output

### 2. Branch Protection

Configure in repository settings:

```yaml
Branch: main
  ✅ Require pull request reviews (1+ approvers)
  ✅ Require status checks to pass
  ✅ Require branches to be up to date
  ✅ Require signed commits
  ✅ Restrict who can push
  ❌ Allow force pushes
  ❌ Allow deletions
```

### 3. Tag Protection

```yaml
Tag Pattern: v*
  ✅ Restrict tag creation to maintainers
  ❌ Allow tag deletion

Tag Pattern: python-v*
  ✅ Restrict tag creation to maintainers
  ❌ Allow tag deletion
```

### 4. Workflow Permissions

All workflows use **least privilege**:

```yaml
permissions:
  contents: read      # Default read-only
  id-token: write     # Only for OIDC (PyPI)
  contents: write     # Only for commits/releases
```

### 5. Supply Chain Security

**Implemented**:
- Dependency pinning in `pyproject.toml`
- Vulnerability scanning (Safety, Bandit)
- SBOM generation in releases
- SLSA provenance attestation
- GPG signed commits and tags

---

## Troubleshooting

### Python CI Failures

#### Lint Errors
```bash
# Run locally to see issues
cd implementations/python
black --check upss/
isort --check upss/
flake8 upss/

# Auto-fix
black upss/
isort upss/
```

#### Test Failures
```bash
# Run specific test
pytest tests/test_client.py::test_load -v

# Run with debugging
pytest tests/ -v -s --pdb

# Check coverage
pytest tests/ --cov=upss --cov-report=html
open htmlcov/index.html
```

#### Type Errors
```bash
# Check specific file
mypy upss/core/client.py

# Ignore missing imports temporarily
mypy upss/ --ignore-missing-imports
```

### Python Publish Failures

#### Tag Format Error
```bash
# Delete wrong tag
git tag -d python-v1.2.3
git push origin :refs/tags/python-v1.2.3

# Create correct tag
git tag -a python-v1.2.3 -m "Release"
git push origin python-v1.2.3
```

#### PyPI Upload Error
```bash
# Check if version already exists
pip index versions upss

# Manually publish (if needed)
cd implementations/python
python -m build
twine upload dist/*
```

#### Test Failure in Workflow
```bash
# Ensure all tests pass locally first
pytest tests/ -v --cov=upss

# Check for environment-specific issues
# - File paths
# - Async handling
# - Resource cleanup
```

### Zenodo Update Failures

#### Missing Secrets
```
Warning: ZENODO_ACCESS_TOKEN not set
```

**Solution**: Add secrets in repository settings

#### Metadata JSON Error
```
Error: config/zenodo/metadata.json not found
```

**Solution**: Ensure file exists and is valid JSON

#### API Rate Limit
```
Error: HTTP 429 Too Many Requests
```

**Solution**: Wait 1 hour and retry

---

## Maintenance

### Updating Workflows

1. Edit workflow files in `.github/workflows/`
2. Test in a fork or feature branch
3. Create PR with workflow changes
4. Review and merge after testing

### Updating Python Dependencies

```bash
cd implementations/python

# Update in pyproject.toml
[project.dependencies]
filelock = ">=3.13.0"  # Updated version

# Reinstall
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

### Monitoring Workflow Health

Regular checks:
- Review failed workflow runs
- Update action versions (e.g., `actions/checkout@v4` → `v5`)
- Monitor dependency vulnerabilities
- Check for deprecated features

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Trusted Publishers (OIDC)](https://docs.pypi.org/trusted-publishers/)
- [Zenodo API Documentation](https://developers.zenodo.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Last Updated**: October 30, 2025  
**Maintained By**: UPSS Contributors
