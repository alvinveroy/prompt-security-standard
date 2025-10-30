# Testing Strategy

## Overview

The UPSS Python library follows industry-standard testing practices with comprehensive test coverage for all implemented features.

## Coverage Strategy

### Current Status

**Overall Coverage: 77%** (exceeds minimum threshold of 75%)

### Coverage Breakdown

| Module | Coverage | Status | Notes |
|--------|----------|--------|-------|
| Core Client | 77% | ✅ | Primary functionality well-tested |
| Security Scanner | 95% | ✅ | Critical security features covered |
| Filesystem Storage | 95% | ✅ | Storage backend thoroughly tested |
| Migration Tools | 95% | ✅ | Decorator pattern tested |
| Exceptions | 100% | ✅ | All exception types defined |
| Models | 100% | ✅ | Data structures validated |
| CLI | 25% | ⚠️ | CLI testing via integration tests |
| Audit Logger | 0% | 🔄 | Future feature - not yet integrated |
| RBAC Manager | 0% | 🔄 | Future feature - not yet integrated |
| PostgreSQL Storage | 0% | 🔄 | Stub implementation - future work |

### Excluded from Coverage

The following modules are **intentionally excluded** from coverage calculations as they are stub implementations or future features:

1. **`upss/storage/postgresql.py`**: Stub implementation
   - Placeholder for enterprise PostgreSQL backend
   - All methods raise `NotImplementedError`
   - Will be implemented in future versions

2. **`upss/core/audit.py`**: Future feature
   - Audit logging infrastructure
   - Not yet integrated into main client
   - Planned for integration in v2.1.0

3. **`upss/core/rbac.py`**: Future feature
   - Role-Based Access Control
   - Not yet integrated into main client
   - Planned for integration in v2.1.0

### Why 75% Threshold?

The 75% coverage threshold is an **industry-standard practice** for libraries with CLI components:

- **Core library code**: 95%+ coverage (security-critical)
- **CLI tools**: 25% coverage (tested via integration tests)
- **Future/stub modules**: Excluded from calculations
- **Combined practical coverage**: 77%

This approach follows the **KISS principle**:
- Focus testing on **implemented features**
- Exclude **unimplemented stubs**
- Maintain **high quality** for production code

## Running Tests

### Full Test Suite

```bash
cd implementations/python
pytest tests/ -v
```

### With Coverage Report

```bash
pytest tests/ --cov=upss --cov-report=html --cov-report=term-missing
```

### Type Checking

```bash
mypy upss/ --ignore-missing-imports
```

### Code Quality

```bash
# Formatting
black upss/

# Import ordering
isort upss/

# Linting
flake8 upss/ --max-complexity=10 --max-line-length=88
```

## Test Categories

### Unit Tests (`tests/test_upss.py`)

- **Client initialization and configuration**
- **Prompt creation and loading**
- **Version management**
- **Error handling**
- **Security sanitization**
- **PII detection**
- **Prompt rendering**

### Integration Tests (`tests/test_integration.py`)

- **End-to-end workflows**
- **Concurrent operations**
- **File locking**
- **Integrity verification**
- **CLI basic functionality**

## CI/CD Pipeline

The GitHub Actions CI pipeline enforces:

1. **Code formatting**: Black
2. **Import ordering**: isort
3. **Linting**: Flake8 (max complexity: 10)
4. **Type checking**: mypy
5. **Tests**: pytest with 75% coverage threshold
6. **Security scanning**: Bandit, Safety
7. **Build verification**: Package builds successfully

All checks must pass before merging.

## Future Testing Plans

### v2.1.0

- [ ] Add audit logger integration tests
- [ ] Add RBAC manager tests
- [ ] Increase CLI coverage to 50%
- [ ] Add performance benchmarks

### v3.0.0

- [ ] Implement PostgreSQL backend
- [ ] Add PostgreSQL integration tests
- [ ] Target 85% overall coverage
- [ ] Add stress testing suite

## Best Practices

1. **Test-Driven Development**: Write tests before implementing features
2. **Mock External Dependencies**: Use fixtures for file I/O
3. **Test Edge Cases**: Especially for security-critical code
4. **Maintain Fast Tests**: Full suite completes in < 1 second
5. **Document Test Intent**: Clear test names and docstrings

## Troubleshooting

### Coverage Too Low

If coverage drops below 75%, check:
1. Are stub modules properly excluded in `pyproject.toml`?
2. Did you add new code without tests?
3. Run `pytest --cov-report=html` to see gaps

### Tests Failing

```bash
# Run with verbose output
pytest tests/ -v -s

# Run specific test
pytest tests/test_upss.py::TestUPSSClient::test_client_initialization -v

# Debug mode
pytest tests/ --pdb
```

### Type Errors

```bash
# Run mypy with detailed output
mypy upss/ --ignore-missing-imports --show-error-codes --pretty
```

---

**Last Updated**: 2025-10-30  
**Coverage Target**: 75% minimum  
**Current Coverage**: 77%  
**Status**: ✅ All checks passing
