# Changelog

All notable changes to the Universal Prompt Security Standard (UPSS) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Python library implementation (v2.0.0) in `implementations/python/`
  - Core UPSSClient with filesystem and PostgreSQL mode support
  - Security features: sanitize(), render(), pattern detection, PII detection
  - Integrity features: SHA-256 checksum verification, rollback support
  - RBAC (Role-Based Access Control) for filesystem and PostgreSQL modes
  - Audit logging with JSONL format
  - Migration tools: discover, decorator-based migration
  - CLI tool: `upss init`, `upss discover`, `upss migrate`
  - Comprehensive test suite
  - Full documentation and examples

## [1.0.1] - 2025-10-29

### Release Notes
## What's Changed
* feat(ci): auto-update version in README, CITATION, and CHANGELOG on release by @alvinveroy in https://github.com/alvinveroy/prompt-security-standard/pull/17


**Full Changelog**: https://github.com/alvinveroy/prompt-security-standard/compare/v1.0.0...v1.0.1
### Added
- Initial draft of the Universal Prompt Security Standard (UPSS)

[1.0.1]: https://github.com/alvinveroy/prompt-security-standard/releases/tag/v1.0.1
