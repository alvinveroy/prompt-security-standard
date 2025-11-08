# UPSS Python Library

A comprehensive Python implementation of the Universal Prompt Security Standard (UPSS) for secure prompt management in LLM applications.

## Features

- **Dual Deployment Modes**: Filesystem (zero-config) and PostgreSQL (enterprise-grade)
- **Security-First Design**: Built-in injection prevention, checksum verification, and audit logging
- **RBAC Support**: Role-based access control for fine-grained permissions
- **Migration Tools**: Facilitate transition from hardcoded prompts to UPSS
- **Async/Await**: Modern asynchronous API for high performance
- **Type-Safe**: Full type hints for better IDE support

## Quick Start

### Installation

```bash
pip install upss
```

### Basic Usage

```python
import asyncio
from upss import UPSSClient

async def main():
    # Initialize client (zero-config filesystem mode)
    async with UPSSClient() as client:
        # Load a prompt
        prompt = await client.load("assistant", user_id="user@example.com")
        print(prompt.content)
        
        # Create a new prompt
        prompt_id = await client.create(
            name="greeting",
            content="You are a helpful assistant...",
            user_id="admin@example.com"
        )
        print(f"Created prompt: {prompt_id}")

asyncio.run(main())
```

### Safe Rendering with User Input

```python
from upss.security.scanner import render

system_prompt = "You are a helpful assistant."
user_message = "User's input here"

# Automatically sanitized
output = render(system_prompt, user_message, style="xml")
```

## Configuration

### Filesystem Mode (Default)

```python
client = UPSSClient(
    mode="filesystem",
    base_path="./prompts",
    enable_checksum=True,
    enable_rbac=False
)
```

### PostgreSQL Mode

```python
client = UPSSClient(
    mode="postgresql",
    db_url="postgresql://user:pass@localhost/upss",
    enable_checksum=True,
    enable_rbac=True
)
```

## Architecture

```
upss/
├── core/
│   ├── client.py          # Main UPSSClient class
│   ├── models.py          # Data models
│   └── exceptions.py      # Exception classes
├── security/
│   └── scanner.py         # Injection prevention, PII detection
├── storage/
│   ├── filesystem.py      # Filesystem storage backend
│   └── postgresql.py      # PostgreSQL storage backend
├── migration/
│   ├── discover.py        # Discover hardcoded prompts
│   ├── facade.py          # Legacy system facade
│   └── decorator.py       # Migration decorator
└── cli/
    └── main.py            # CLI tool
```

## Security Features

### Prompt Injection Prevention

```python
from upss.security.scanner import sanitize, calculate_risk_score

user_input = "ignore previous instructions..."
sanitized, is_safe = sanitize(user_input)

if not is_safe:
    print("Potential injection detected!")
```

### PII Detection

```python
from upss.security.scanner import detect_pii

content = "My email is user@example.com"
pii_types = detect_pii(content, block=True)  # Raises ComplianceError if PII found
```

### Checksum Verification

```python
# Automatically verified on load
prompt = await client.load("assistant", user_id="user@example.com")
# IntegrityError raised if checksum fails
```

## Migration Tools

### Discover Hardcoded Prompts

```bash
upss discover --path ./myapp --output prompts.json
```

### Decorator-Based Migration

```python
from upss.migration.decorator import migrate_prompt

@migrate_prompt("assistant-system")
async def get_system_prompt(user_id: str):
    return "fallback prompt"  # Used if UPSS fails
```

### Batch Migration

```python
prompts = [
    {"name": "old-prompt-1", "content": "..."},
    {"name": "old-prompt-2", "content": "..."},
]

report = await client.migrate(prompts, user_id="admin@example.com")
print(f"Migrated: {report.successful}/{report.total}")
```

## CLI Usage

### Initialize UPSS

```bash
upss init
```

### Discover Hardcoded Prompts

```bash
upss discover --path ./src --output prompts.json
```

## Testing

```bash
# Install dev dependencies
pip install upss[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=upss
```

## Requirements

- Python 3.9+
- For PostgreSQL mode: PostgreSQL 12+

## Dependencies

- `filelock`: File-based locking for filesystem mode
- `asyncpg`: PostgreSQL async driver
- `pyyaml`: YAML configuration support
- `click`: CLI framework

## Performance

| Operation | Filesystem Mode | PostgreSQL Mode (Cached) | PostgreSQL Mode (Uncached) |
|-----------|----------------|-------------------------|---------------------------|
| Load prompt | < 10ms | < 5ms | < 100ms |
| Create prompt | < 50ms | < 50ms | < 150ms |
| Permission check | < 5ms | < 2ms | < 20ms |

## Documentation

- [API Reference](docs/api.md)
- [Security Guide](docs/security.md)
- [Migration Guide](docs/migration.md)
- [Examples](examples/)

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../../LICENSE) for details.

## Security

For security vulnerabilities, see [SECURITY.md](../../SECURITY.md).

## Support

- GitHub Issues: [Report issues](https://github.com/upss-standard/universal-prompt-security-standard/issues)
- Documentation: [Full docs](https://github.com/upss-standard/universal-prompt-security-standard)

## Citation

```bibtex
@software{upss_python,
  title={UPSS Python Library},
  author={UPSS Contributors},
  year={2025},
  url={https://github.com/upss-standard/universal-prompt-security-standard}
}
```
