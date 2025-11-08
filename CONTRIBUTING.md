# Contributing to Universal Prompt Security Standard (UPSS)

Thank you for your interest in contributing to UPSS! This document provides guidelines and best practices for contributing to the Universal Prompt Security Standard project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Documentation Guidelines](#documentation-guidelines)
- [Testing Requirements](#testing-requirements)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Community Guidelines](#community-guidelines)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior through GitHub Issues or contact the maintainer directly.

## Getting Started

### Prerequisites

- Git
- Node.js 18+ (for TypeScript examples)
- Python 3.9+ (for Python examples)
- Java 17+ (for Java examples)
- Familiarity with security best practices
- Understanding of LLM and prompt engineering concepts

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/prompt-security-standard.git
cd prompt-security-standard
```

3. Add upstream remote:

```bash
git remote add upstream https://github.com/alvinveroy/prompt-security-standard.git
```

4. Create a feature branch:

```bash
git checkout -b type/scope/description
```

### Branch Naming Convention

Use the following format for branch names:

```
type/scope/description
```

**Types:**
- `feat`: New feature or enhancement
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Scopes:**
- `config`: Configuration files
- `prompts`: Prompt templates and examples
- `security`: Security controls and features
- `tools`: Tooling and utilities
- `ci`: CI/CD pipeline
- `examples`: Reference implementations

**Examples:**
- `feat/security/add-encryption-support`
- `docs/implementation/update-installation-guide`
- `fix/config/resolve-checksum-validation`

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Code Contributions**
   - Reference implementations
   - Security tools and utilities
   - Integration libraries
   - Test suites

2. **Documentation**
   - Improving existing documentation
   - Writing guides and tutorials
   - Translating documentation
   - Creating diagrams and visualizations

3. **Security Research**
   - Identifying vulnerabilities
   - Proposing security enhancements
   - Conducting security audits
   - Threat modeling

4. **Community Support**
   - Answering questions in discussions
   - Reviewing pull requests
   - Helping with issue triage
   - Organizing community events

## Development Workflow

### 1. Sync with Upstream

Before starting work, sync your fork:

```bash
git checkout main
git pull --rebase upstream main
git push origin main
```

### 2. Create Feature Branch

```bash
git checkout -b feat/security/new-feature
```

### 3. Make Changes

- Write clear, self-documenting code
- Follow coding standards (see below)
- Add or update tests as needed
- Update documentation

### 4. Commit Changes

Follow the [commit message format](#commit-message-format):

```bash
git add .
git commit -m "feat(security): add encryption support for prompts"
```

### 5. Push to Your Fork

```bash
git push origin feat/security/new-feature
```

### 6. Create Pull Request

- Go to GitHub and create a pull request
- Fill out the pull request template
- Link related issues
- Request reviews from maintainers

## Coding Standards

### General Principles

- **Clarity over Cleverness:** Write code that is easy to understand
- **Security First:** Always consider security implications
- **DRY (Don't Repeat Yourself):** Avoid code duplication
- **KISS (Keep It Simple):** Prefer simple solutions
- **YAGNI (You Aren't Gonna Need It):** Don't add unnecessary features

### Language-Specific Standards

#### TypeScript/JavaScript

- Use TypeScript for type safety
- Follow Airbnb JavaScript Style Guide
- Use ES6+ features
- Prefer functional programming patterns
- Use meaningful variable and function names

```typescript
// Good
async function loadPromptWithValidation(promptId: string): Promise<Prompt> {
  const config = await loadConfiguration();
  const prompt = await loadPromptById(promptId);
  await validateChecksum(prompt);
  return prompt;
}

// Avoid
async function lp(id: string): Promise<any> {
  const c = await lc();
  const p = await lpbi(id);
  await vc(p);
  return p;
}
```

#### Python

- Follow PEP 8 style guide
- Use type hints (Python 3.9+)
- Write docstrings for all public functions
- Use meaningful variable names
- Prefer composition over inheritance

```python
# Good
def load_prompt_with_validation(prompt_id: str) -> Prompt:
    """
    Load and validate a prompt by ID.
    
    Args:
        prompt_id: Unique identifier for the prompt
        
    Returns:
        Validated Prompt object
        
    Raises:
        ValidationError: If prompt validation fails
    """
    config = load_configuration()
    prompt = load_prompt_by_id(prompt_id)
    validate_checksum(prompt)
    return prompt
```

#### Java

- Follow Google Java Style Guide
- Use Java 17+ features
- Write Javadoc for public APIs
- Use dependency injection
- Prefer immutability

```java
// Good
public class PromptLoader {
    private final ConfigurationService configService;
    private final ValidationService validationService;
    
    public PromptLoader(ConfigurationService configService, 
                       ValidationService validationService) {
        this.configService = configService;
        this.validationService = validationService;
    }
    
    public Prompt loadPromptWithValidation(String promptId) 
            throws ValidationException {
        Configuration config = configService.load();
        Prompt prompt = loadPromptById(promptId);
        validationService.validateChecksum(prompt);
        return prompt;
    }
}
```

### Security Standards

- **No Hardcoded Secrets:** Use environment variables or secure vaults
- **Input Validation:** Always validate and sanitize inputs
- **Error Handling:** Don't expose sensitive information in errors
- **Logging:** Log security events, but not sensitive data
- **Dependencies:** Keep dependencies up to date

```typescript
// Good: Secure configuration loading
const apiKey = process.env.API_KEY || loadFromSecureVault();

// Bad: Hardcoded secret
const apiKey = "sk-1234567890abcdef";
```

## Documentation Guidelines

### Markdown Standards

- Use clear, concise language
- Follow Google Developer Documentation Style Guide
- Use proper heading hierarchy
- Include code examples where appropriate
- Add table of contents for long documents

### Documentation Structure

```markdown
# Title

Brief description (1-2 sentences)

## Overview

Detailed overview with context

## Prerequisites

List prerequisites

## Step-by-Step Instructions

Numbered steps with code examples

## Common Issues

Troubleshooting section

## Related Documentation

Links to related docs
```

### Code Documentation

- Document all public APIs
- Include usage examples
- Explain complex algorithms
- Document security considerations
- Keep documentation up to date with code changes

## Testing Requirements

### Unit Tests

- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

```typescript
describe('PromptLoader', () => {
  describe('loadPromptWithValidation', () => {
    it('should load and validate prompt successfully', async () => {
      // Arrange
      const promptId = 'test-prompt';
      const expectedPrompt = createMockPrompt();
      
      // Act
      const result = await loader.loadPromptWithValidation(promptId);
      
      // Assert
      expect(result).toEqual(expectedPrompt);
    });
    
    it('should throw ValidationError for invalid checksum', async () => {
      // Arrange
      const promptId = 'invalid-prompt';
      
      // Act & Assert
      await expect(
        loader.loadPromptWithValidation(promptId)
      ).rejects.toThrow(ValidationError);
    });
  });
});
```

### Integration Tests

- Test integration between components
- Use test containers when possible
- Clean up resources after tests
- Test error scenarios

### Security Tests

- Test input validation
- Test authentication and authorization
- Test injection attack prevention
- Test encryption and signing

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `build`: Build system changes
- `revert`: Revert previous commit

### Scope

The scope is optional and indicates the area of change:
- `config`
- `security`
- `prompts`
- `tools`
- `examples`
- `docs`

### Subject

- Use imperative mood ("add" not "added")
- Don't capitalize first letter
- No period at the end
- Maximum 72 characters

### Body

- Explain what and why, not how
- Wrap at 72 characters
- Separate from subject with blank line

### Footer

- Reference issues: `Closes #123`
- Breaking changes: `BREAKING CHANGE: description`

### Examples

```
feat(security): add checksum validation for prompts

Implement SHA-256 checksum validation to ensure prompt integrity.
This prevents unauthorized modifications and detects tampering.

Closes #45
```

```
fix(config): resolve JSON schema validation error

The schema was incorrectly validating the prompts array.
Updated the schema to allow optional fields.

Fixes #67
```

```
docs(implementation): update installation instructions

Add prerequisites section and clarify dependency installation
steps for Python and Node.js environments.
```

## Pull Request Process

### Before Submitting

1. **Sync with upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests:**
   ```bash
   npm test  # or pytest, mvn test, etc.
   ```

3. **Check linting:**
   ```bash
   npm run lint
   ```

4. **Update documentation:**
   - Update relevant docs
   - Add changelog entry if needed

### Pull Request Template

When creating a pull request, include:

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Security enhancement
- [ ] Performance improvement

## Related Issues

Closes #issue_number

## Testing

Describe testing performed

## Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No breaking changes (or documented)
- [ ] Security implications considered
```

### Review Process

1. **Automated Checks:**
   - CI/CD pipeline must pass
   - Code coverage maintained
   - Security scans pass

2. **Peer Review:**
   - At least one approval required
   - Address review comments
   - Resolve merge conflicts

3. **Maintainer Review:**
   - Final review by maintainer
   - Merge when approved

### After Merge

- Delete feature branch
- Update local main branch
- Close related issues

## Issue Reporting

### Before Creating an Issue

1. Search existing issues
2. Check documentation
3. Verify with latest version

### Issue Template

```markdown
## Description

Clear description of the issue

## Steps to Reproduce

1. Step one
2. Step two
3. Step three

## Expected Behavior

What should happen

## Actual Behavior

What actually happens

## Environment

- OS: [e.g., Ubuntu 22.04]
- Version: [e.g., 1.0.0]
- Language: [e.g., Node.js 18.x]

## Additional Context

Screenshots, logs, or other relevant information
```

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `security`: Security-related issues
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `question`: Further information requested

## Community Guidelines

### Communication Channels

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** General discussions and questions

### Best Practices

1. **Be Respectful:**
   - Treat everyone with respect
   - Welcome newcomers
   - Assume good intentions

2. **Be Helpful:**
   - Answer questions when you can
   - Share knowledge and experience
   - Help review pull requests

3. **Be Professional:**
   - Keep discussions on topic
   - Provide constructive feedback
   - Focus on the work, not the person

4. **Be Patient:**
   - Maintainers are volunteers
   - Response times may vary
   - Multiple perspectives take time

### Recognition

We recognize contributors through:
- Contributors listed in CHANGELOG.md
- Acknowledgment in release notes
- Credit in documentation and examples

## Getting Help

If you need help:

1. **Documentation:** Check existing documentation first
2. **Discussions:** Search or start a discussion on GitHub
3. **Slack:** Ask in the community Slack workspace
4. **Issues:** Open an issue if you found a bug

For security vulnerabilities, see [SECURITY.md](SECURITY.md).

## License

By contributing to UPSS, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Thank you for contributing to UPSS! Your efforts help make AI systems more secure for everyone.
