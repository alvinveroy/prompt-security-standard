# Python UPSS Implementation

This example demonstrates how to implement the Universal Prompt Security Standard (UPSS) in a Python application.

## Structure

```
python/
├── upss_config.yaml          # Main UPSS configuration
├── prompts/                  # Prompt templates directory
│   ├── system/
│   │   └── assistant.md
│   └── user/
│       └── greeting.md
├── upss_loader.py           # UPSS configuration loader
├── example_app.py           # Basic application example
├── flask_app.py             # Flask web application example
├── validator.py             # Configuration validator
├── requirements.txt         # Python dependencies
└── tests/                   # Test suite
    └── test_upss.py

```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Review the Configuration

The `upss_config.yaml` file defines the prompt structure:

```yaml
upss_version: "1.0.0"
prompts:
  system_assistant:
    path: "prompts/system/assistant.md"
    type: "system"
    version: "1.0.0"
```

### 2. Run the Basic Example

```bash
python example_app.py
```

### 3. Run the Flask Application

```bash
python flask_app.py
```

Visit `http://localhost:5000` to interact with the application.

### 4. Validate Configuration

```bash
python validator.py upss_config.yaml
```

## Key Features

- **Centralized Configuration**: All prompts defined in UPSS config
- **Version Control**: Track prompt changes with Git
- **Validation**: Automated validation of configuration and prompts
- **Security**: No hardcoded prompts in application code
- **Auditability**: Clear audit trail of prompt usage

## Testing

```bash
python -m pytest tests/
```

## Integration in Your Project

1. Copy `upss_loader.py` and `validator.py` to your project
2. Create `upss_config.yaml` in your project root
3. Organize prompts in the `prompts/` directory
4. Use the loader in your application:

```python
from upss_loader import UPSSLoader

loader = UPSSLoader("upss_config.yaml")
prompt = loader.get_prompt("system_assistant")
```

## License

See [LICENSE](../../LICENSE) for details.
