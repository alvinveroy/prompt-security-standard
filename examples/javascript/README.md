# JavaScript/Node.js UPSS Implementation

This example demonstrates how to implement the Universal Prompt Security Standard (UPSS) in a JavaScript/Node.js application.

## Structure

```
javascript/
├── upss_config.yaml          # Main UPSS configuration
├── prompts/                  # Prompt templates directory
│   ├── system/
│   │   └── assistant.md
│   └── user/
│       └── greeting.md
├── src/
│   ├── upss-loader.js       # UPSS configuration loader
│   ├── validator.js         # Configuration validator
│   ├── express-app.js       # Express.js web application
│   └── cli.js               # Command-line interface
├── package.json             # Node.js dependencies
├── tests/
│   └── upss.test.js        # Test suite
└── README.md               # This file
```

## Installation

```bash
npm install
```

## Quick Start

### 1. Review the Configuration

The `upss_config.yaml` file defines the prompt structure following UPSS standards.

### 2. Run the CLI Example

```bash
node src/cli.js
```

### 3. Run the Express Application

```bash
node src/express-app.js
```

Visit `http://localhost:3000` to interact with the application.

### 4. Validate Configuration

```bash
node src/validator.js upss_config.yaml
```

## Key Features

- **Centralized Configuration**: All prompts defined in UPSS config
- **Async/Await Support**: Modern JavaScript async patterns
- **RESTful API**: Express.js integration example
- **Validation**: Automated configuration and prompt validation
- **Caching**: In-memory prompt caching for performance
- **Audit Logging**: Track prompt access and modifications

## Testing

```bash
npm test
```

## Integration in Your Project

1. Install dependencies:
```bash
npm install js-yaml
```

2. Copy `src/upss-loader.js` and `src/validator.js` to your project

3. Create `upss_config.yaml` in your project root

4. Use the loader in your application:

```javascript
const UPSSLoader = require('./upss-loader');

const loader = new UPSSLoader('upss_config.yaml');
const prompt = await loader.getPrompt('system_assistant');
```

## License

See [LICENSE](../../LICENSE) for details.
