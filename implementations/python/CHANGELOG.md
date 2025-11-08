# Changelog

All notable changes to the UPSS Python implementation will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial changelog for Python implementation

## [2.0.0] - 2025-10-30

### Added
- Core UPSS client with filesystem and PostgreSQL storage support
- Prompt versioning and rollback capabilities
- Checksum verification for data integrity
- Audit logging for all operations
- Security scanning with sanitization and PII detection
- Risk scoring for prompts
- CLI tools for prompt management and migration
- Role-based access control (RBAC) framework
- Support for multiple storage backends
- Comprehensive test suite with >95% coverage
- Type hints throughout the codebase

### Changed
- Improved error handling with custom exception hierarchy
- Enhanced file locking mechanism for concurrent operations
- Optimized metadata storage format

### Security
- Implemented cryptographic checksum verification
- Added sanitization for prompt injection prevention
- Integrated PII detection and blocking
- Secure file handling with proper permissions

## [1.0.0] - 2025-10-29

### Added
- Initial release of UPSS Python implementation
- Basic prompt storage and retrieval
- Version management
- Filesystem storage backend
- Basic CLI interface

---

[Unreleased]: https://github.com/upss-standard/universal-prompt-security-standard/compare/python-v2.0.0...HEAD
[2.0.0]: https://github.com/upss-standard/universal-prompt-security-standard/releases/tag/python-v2.0.0
[1.0.0]: https://github.com/upss-standard/universal-prompt-security-standard/releases/tag/python-v1.0.0
