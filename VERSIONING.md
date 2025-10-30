# Version Management Strategy

This document outlines the versioning strategy and automation practices for the Universal Prompt Security Standard (UPSS) project.

## Table of Contents

1. [Overview](#overview)
2. [Versioning Scheme](#versioning-scheme)
3. [Repository Structure](#repository-structure)
4. [Tag Naming Conventions](#tag-naming-conventions)
5. [Automated Workflows](#automated-workflows)
6. [Release Process](#release-process)
7. [Security Considerations](#security-considerations)

---

## Overview

UPSS follows a **multi-component versioning strategy** where different parts of the project maintain independent version numbers:

- **Standard Version**: The UPSS specification and documentation
- **Python Implementation**: The Python library (`upss` package)
- **JavaScript Implementation**: The JavaScript/TypeScript library (future)

This approach allows each component to evolve at its own pace while maintaining clear traceability.

---

## Versioning Scheme

### Semantic Versioning

All components follow [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes
- **PRERELEASE**: Optional pre-release identifiers (alpha, beta, rc)
- **BUILD**: Optional build metadata

### Version Increment Guidelines

#### MAJOR Version (X.0.0)

Increment when making incompatible changes:

- Breaking API changes
- Removal of deprecated features
- Major architectural redesign
- Changes requiring migration guides

**Example**: `1.5.3` → `2.0.0`

#### MINOR Version (x.Y.0)

Increment when adding backward-compatible features:

- New functionality or APIs
- Deprecation of existing features (with backward compatibility)
- Significant performance improvements
- New optional dependencies

**Example**: `1.5.3` → `1.6.0`

#### PATCH Version (x.y.Z)

Increment for backward-compatible bug fixes:

- Bug fixes
- Security patches
- Documentation updates
- Internal refactoring without API changes

**Example**: `1.5.3` → `1.5.4`

---

## Repository Structure

```
prompt-security-standard/
├── .github/
│   └── workflows/           # CI/CD automation
│       ├── python-publish.yml
│       ├── python-ci.yml
│       └── zenodo-metadata-update.yml
├── implementations/
│   ├── python/
│   │   ├── pyproject.toml   # Version: python-vX.Y.Z
│   │   ├── CHANGELOG.md
│   │   └── upss/
│   └── javascript/          # Future: js-vX.Y.Z
├── docs/                    # Standard documentation
├── CHANGELOG.md             # Standard version changelog
├── CITATION.cff             # Standard version: vX.Y.Z
├── README.md                # Standard version: vX.Y.Z
└── VERSIONING.md            # This document
```

---

## Tag Naming Conventions

### Standard Releases

Tags for the UPSS standard specification:

```bash
v1.0.0          # Standard release
v1.1.0-beta.1   # Pre-release
v2.0.0-rc.1     # Release candidate
```

**Pattern**: `v*` excluding pre-releases and implementation tags

**Triggers**:
- Zenodo metadata update
- Documentation updates
- DOI minting

### Python Implementation

Tags for the Python library:

```bash
python-v1.0.0          # Production release
python-v1.1.0-beta.1   # Pre-release
python-v2.0.0-rc.1     # Release candidate
```

**Pattern**: `python-v*`

**Triggers**:
- PyPI publication
- Python CHANGELOG update
- pyproject.toml version bump

### JavaScript Implementation (Future)

Tags for JavaScript/TypeScript library:

```bash
js-v1.0.0          # Production release
js-v1.1.0-beta.1   # Pre-release
```

**Pattern**: `js-v*`

**Triggers**:
- npm publication
- JavaScript CHANGELOG update
- package.json version bump

---

## Automated Workflows

### 1. Python PyPI Publication

**File**: `.github/workflows/python-publish.yml`

**Triggers**:
- Git tags matching `python-v*` (e.g., `python-v1.2.3`)
- Manual dispatch via GitHub Actions UI

**Actions**:
1. Extract version from tag
2. Update `implementations/python/pyproject.toml`
3. Update `implementations/python/CHANGELOG.md`
4. Run full test suite
5. Build distribution packages (wheel + sdist)
6. Publish to PyPI
7. Create GitHub release with artifacts

**Security**:
- Uses PyPI trusted publishers (OIDC)
- No long-lived tokens
- Automated provenance generation
- SLSA attestation

### 2. Python CI (Pull Request)

**File**: `.github/workflows/python-ci.yml`

**Triggers**:
- Pull requests to `main` branch
- Changes in `implementations/python/**`

**Checks**:
1. **Linting**: `flake8` for code quality
2. **Formatting**: `black` and `isort` verification
3. **Type Checking**: `mypy` static analysis
4. **Testing**: `pytest` with coverage (minimum 80%)
5. **Security**: Dependency vulnerability scanning

**Quality Gates**:
- All tests must pass
- Coverage ≥ 80%
- No type errors
- No linting violations

### 3. Zenodo Metadata Update

**File**: `.github/workflows/zenodo-metadata-update.yml`

**Triggers**:
- Git tags matching `v*` (standard releases only)
- Excludes: `v*-*` (pre-releases) and `python-v*` (Python tags)

**Actions**:
1. Update `CITATION.cff` with new version and date
2. Update `README.md` version and last updated date
3. Update `CHANGELOG.md` with release notes
4. Publish new version to Zenodo with updated metadata
5. Generate new DOI

---

## Release Process

### Python Library Release

#### 1. Pre-Release Checklist

```bash
# Ensure you're on main and up-to-date
git checkout main
git pull origin main

# Run full test suite
cd implementations/python
python -m pytest tests/ -v --cov=upss

# Run code quality checks
black --check .
flake8 .
mypy upss/

# Verify no uncommitted changes
git status
```

#### 2. Version Decision

Determine the new version based on changes:

- Breaking changes → MAJOR
- New features → MINOR
- Bug fixes → PATCH

#### 3. Create Release Tag

```bash
# For a new version (e.g., 2.1.0)
NEW_VERSION="2.1.0"

# Create and push tag
git tag -a "python-v${NEW_VERSION}" -m "Release Python UPSS v${NEW_VERSION}"
git push origin "python-v${NEW_VERSION}"
```

#### 4. Monitor Workflow

1. Go to GitHub Actions tab
2. Watch `Python Publish` workflow
3. Verify all steps complete successfully
4. Check PyPI for new version: https://pypi.org/project/upss/

#### 5. Verify Publication

```bash
# Test installation from PyPI
pip install upss==${NEW_VERSION}

# Verify version
python -c "import upss; print(upss.__version__)"
```

### Standard Release

#### 1. Update Documentation

```bash
# Update version in relevant files
# - README.md
# - CITATION.cff
# - docs/specification.md

# Update CHANGELOG.md with release notes
```

#### 2. Create Release Tag

```bash
# For a new standard version (e.g., 1.2.0)
NEW_VERSION="1.2.0"

# Create and push tag
git tag -a "v${NEW_VERSION}" -m "Release UPSS Standard v${NEW_VERSION}"
git push origin "v${NEW_VERSION}"
```

#### 3. Create GitHub Release

1. Go to GitHub Releases
2. Draft a new release
3. Select the tag
4. Add release notes (follows CHANGELOG format)
5. Publish release

The Zenodo workflow will automatically:
- Update metadata files
- Publish to Zenodo
- Generate new DOI

---

## Security Considerations

### 1. Secrets Management

**Required Secrets** (configured in GitHub repository settings):

```yaml
PYPI_API_TOKEN:          # PyPI trusted publisher (OIDC preferred)
ZENODO_ACCESS_TOKEN:     # Zenodo API token
ZENODO_DEPOSITION_ID:    # Zenodo record ID
```

**Best Practices**:
- Use OIDC/trusted publishers when possible
- Rotate tokens annually
- Use minimal scopes
- Never commit secrets
- Use environment-specific secrets

### 2. Supply Chain Security

**Measures**:

1. **Dependency Pinning**: Use exact versions in `pyproject.toml`
2. **Vulnerability Scanning**: Automated dependency checks in CI
3. **SBOM Generation**: Software Bill of Materials in releases
4. **Provenance**: SLSA attestation for builds
5. **Code Signing**: GPG signatures on tags

### 3. Protected Branches

Configure branch protection for `main`:

```yaml
Branch Protection Rules:
  - Require pull request reviews (1+ approvers)
  - Require status checks to pass
  - Require branches to be up to date
  - Require signed commits
  - Restrict who can push
  - Do not allow force pushes
  - Do not allow deletions
```

### 4. Tag Protection

Enable tag protection rules:

```yaml
Tag Protection Rules:
  - Pattern: v*
  - Pattern: python-v*
  - Restrict tag creation to: Release managers
  - Prevent tag deletion
  - Require signed tags
```

### 5. Audit Trail

All version changes are tracked:

- Git commit history
- GitHub Actions logs
- PyPI release history
- Zenodo version history
- Audit logs in CHANGELOG files

---

## Troubleshooting

### Version Mismatch

**Problem**: Tag version doesn't match pyproject.toml

**Solution**:
```bash
# Delete incorrect tag
git tag -d python-v1.2.3
git push origin :refs/tags/python-v1.2.3

# Create correct tag
git tag -a python-v1.2.3 -m "Correct version"
git push origin python-v1.2.3
```

### Failed PyPI Publication

**Problem**: PyPI upload fails

**Solution**:
1. Check workflow logs for specific error
2. Verify version doesn't already exist on PyPI
3. Check PYPI_API_TOKEN is valid
4. Manually publish if needed:

```bash
cd implementations/python
python -m build
twine upload dist/*
```

### Workflow Triggering Issues

**Problem**: Workflow doesn't trigger on tag push

**Solution**:
1. Verify tag pattern matches workflow filter
2. Check workflow permissions
3. Ensure workflow file is on main branch
4. Manually trigger workflow if supported

---

## Best Practices

### DO ✅

- **Always** update CHANGELOG.md before releasing
- **Always** run full test suite before tagging
- **Always** use annotated tags (`git tag -a`)
- **Always** follow semantic versioning strictly
- **Document** breaking changes clearly
- **Review** automated commits before pushing
- **Test** releases in staging environments when possible
- **Communicate** releases to users via multiple channels

### DON'T ❌

- **Never** delete published versions (use yanking instead)
- **Never** reuse version numbers
- **Never** skip versions
- **Never** commit secrets or tokens
- **Never** force push to protected branches
- **Never** bypass CI checks
- **Never** release untested code
- **Don't** use lightweight tags for releases

---

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [SLSA Framework](https://slsa.dev/)
- [Trusted Publishers](https://docs.pypi.org/trusted-publishers/)

---

## Changelog

| Version | Date       | Changes                                    |
|---------|------------|--------------------------------------------|
| 1.0.0   | 2025-10-30 | Initial version management documentation   |

---

**Document Version**: 1.0.0  
**Last Updated**: October 30, 2025  
**Maintainer**: UPSS Contributors  
**Status**: Active
