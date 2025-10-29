# UPSS Implementation Guide

**Version:** 1.0.0  
**Last Updated:** October 29, 2025

This guide provides step-by-step instructions for implementing the Universal Prompt Security Standard (UPSS) in your organization.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Phase 1: Planning](#phase-1-planning)
- [Phase 2: Infrastructure Setup](#phase-2-infrastructure-setup)
- [Phase 3: Prompt Migration](#phase-3-prompt-migration)
- [Phase 4: Security Implementation](#phase-4-security-implementation)
- [Phase 5: Integration](#phase-5-integration)
- [Phase 6: Validation](#phase-6-validation)
- [Phase 7: Deployment](#phase-7-deployment)
- [Phase 8: Operations](#phase-8-operations)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

Implementing UPSS involves transforming your current prompt management approach from code-embedded prompts to a secure, externalized configuration system.

### Implementation Timeline

- **Small Projects (1-10 prompts):** 1-2 weeks
- **Medium Projects (10-50 prompts):** 3-6 weeks
- **Large Projects (50+ prompts):** 8-12 weeks
- **Enterprise Deployments:** 12-24 weeks

### Success Criteria

Your implementation is successful when:
- All prompts are externalized from code
- Security controls are in place and validated
- Audit trail is operational
- Team is trained and following procedures
- Compliance requirements are met

## Prerequisites

### Technical Requirements

**Required:**
- Version control system (Git recommended)
- CI/CD pipeline
- Secrets management solution
- Logging and monitoring infrastructure

**Recommended:**
- Container orchestration (Kubernetes, Docker Swarm)
- API gateway
- Service mesh
- Security scanning tools

### Team Requirements

**Required Roles:**
- Security Engineer
- Software Developer
- DevOps Engineer
- Compliance Officer

**Recommended Roles:**
- Security Architect
- Prompt Engineer
- QA Engineer
- Technical Writer

### Knowledge Requirements

- Security best practices
- LLM and prompt engineering
- Your application architecture
- Compliance requirements

## Phase 1: Planning

### Step 1.1: Assessment

**Inventory Existing Prompts**

```bash
# Search for hardcoded prompts in codebase
grep -r "system.*prompt" src/
grep -r "You are" src/
grep -r "assistant.*instruction" src/
```

Create an inventory:

```csv
Prompt ID,Location,Category,Risk Level,Owner,Status
user_welcome,src/handlers/user.ts,user,low,team-frontend,active
admin_system,src/admin/system.ts,system,critical,team-backend,active
```

**Identify Security Gaps**

Checklist:
- [ ] Prompts are hardcoded in source files
- [ ] No version control for prompts
- [ ] No audit trail for changes
- [ ] No input validation
- [ ] No integrity verification
- [ ] No access controls
- [ ] No encryption at rest

**Define Requirements**

Document:
- Security requirements (mandatory controls)
- Compliance requirements (regulations)
- Operational requirements (SLAs, availability)
- Integration requirements (existing systems)

### Step 1.2: Architecture Design

**Design Directory Structure**

```
config/
├── prompts/
│   ├── system/
│   ├── user/
│   ├── fallback/
│   └── templates/
├── prompts.json
└── prompts.schema.json
```

**Design Configuration Schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "prompts", "settings"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "prompts": {
      "type": "object",
      "patternProperties": {
        "^[a-zA-Z][a-zA-Z0-9]*$": {
          "type": "object",
          "required": ["path", "version", "category", "riskLevel", "checksum"],
          "properties": {
            "path": {"type": "string"},
            "version": {"type": "string"},
            "category": {"enum": ["system", "user", "fallback"]},
            "riskLevel": {"enum": ["low", "medium", "high", "critical"]},
            "checksum": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"}
          }
        }
      }
    }
  }
}
```

### Step 1.3: Risk Assessment

**Classify Prompts by Risk**

| Risk Level | Criteria | Example |
|------------|----------|---------|
| Critical | System-level, production, sensitive data | Admin prompts, authentication |
| High | User-facing, business logic | Customer service, transactions |
| Medium | Internal tools, non-sensitive | Reports, summaries |
| Low | Development, testing | Debug prompts, examples |

**Threat Modeling**

Identify threats:
- Prompt injection attacks
- Unauthorized modifications
- Information disclosure
- Supply chain compromise
- Insider threats

Map mitigations to each threat.

### Step 1.4: Project Planning

**Create Implementation Roadmap**

```
Week 1-2:   Infrastructure setup
Week 3-4:   Pilot implementation (5-10 prompts)
Week 5-6:   Full migration
Week 7-8:   Security implementation
Week 9-10:  Integration testing
Week 11-12: Deployment and training
```

**Resource Allocation**

- Development: 40% of time
- Security: 30% of time
- Testing: 20% of time
- Documentation: 10% of time

## Phase 2: Infrastructure Setup

### Step 2.1: Directory Structure

**Create Directory Structure**

```bash
mkdir -p config/prompts/{system,user,fallback,templates}
mkdir -p docs/{implementation,security,governance}
mkdir -p tests/{unit,integration,security}
mkdir -p examples/{nodejs,python,java}
```

**Initialize Configuration Files**

```bash
touch config/prompts.json
touch config/prompts.schema.json
touch .env.example
```

### Step 2.2: Version Control Setup

**Initialize Git Repository**

```bash
git init
git add .gitignore
git commit -m "chore: initialize UPSS structure"
```

**Configure .gitignore**

```
# Environment files
.env
.env.local
.env.*.local

# Secrets
secrets/
*.key
*.pem

# Build outputs
dist/
build/
node_modules/

# IDE
.vscode/
.idea/
*.swp
```

**Create Branch Protection**

Configure branch protection for `main`:
- Require pull request reviews (minimum 2)
- Require status checks to pass
- Require signed commits
- Restrict push access

### Step 2.3: Secrets Management

**Choose Secrets Manager**

Options:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Google Secret Manager
- Kubernetes Secrets

**Initialize Secrets**

```bash
# Example using AWS Secrets Manager
aws secretsmanager create-secret \
  --name upss/prompt-encryption-key \
  --secret-string "$(openssl rand -base64 32)"
```

### Step 2.4: CI/CD Pipeline

**Configure GitHub Actions**

Create `.github/workflows/upss-validation.yml`:

```yaml
name: UPSS Validation

on:
  pull_request:
    paths:
      - 'config/prompts/**'
      - 'config/prompts.json'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Validate JSON Schema
        run: |
          npm install -g ajv-cli
          ajv validate -s config/prompts.schema.json -d config/prompts.json
      
      - name: Verify Checksums
        run: |
          node scripts/verify-checksums.js
      
      - name: Security Scan
        run: |
          npm install -g snyk
          snyk test
      
      - name: Audit Log
        run: |
          node scripts/audit-log.js
```

## Phase 3: Prompt Migration

### Step 3.1: Extract Prompts

**Identify Prompts in Code**

```typescript
// Before: Hardcoded prompt
const systemPrompt = `You are a helpful assistant that provides accurate information.
Never share personal information.
Always be respectful and professional.`;

// After: Prompt ID reference
const systemPrompt = await promptLoader.load('helpfulAssistant');
```

**Create Prompt Files**

For each identified prompt, create a markdown file:

`config/prompts/system/helpful-assistant.md`:

```markdown
---
version: 1.0.0
category: system
riskLevel: medium
author: team-ai
createdDate: 2025-10-29
reviewDate: 2025-10-29
checksum: sha256:pending
tags:
  - assistant
  - general
---

# Helpful Assistant System Prompt

You are a helpful assistant that provides accurate and reliable information to users.

## Core Principles

1. **Accuracy:** Provide factually correct information
2. **Privacy:** Never share or request personal information
3. **Professionalism:** Maintain respectful and professional tone
4. **Safety:** Refuse harmful or dangerous requests

## Response Guidelines

- Be concise and clear
- Cite sources when applicable
- Admit when uncertain
- Suggest alternatives when appropriate

## Prohibited Actions

- Do not execute code
- Do not access external systems
- Do not share personal data
- Do not provide harmful information
```

### Step 3.2: Generate Checksums

**Create Checksum Generation Script**

`scripts/generate-checksums.js`:

```javascript
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

function generateChecksum(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const hash = crypto.createHash('sha256');
  hash.update(content);
  return `sha256:${hash.digest('hex')}`;
}

function updatePromptChecksum(promptFile) {
  const content = fs.readFileSync(promptFile, 'utf8');
  const checksum = generateChecksum(promptFile);
  
  const updated = content.replace(
    /checksum: sha256:[a-f0-9]{64}|checksum: pending/,
    `checksum: ${checksum}`
  );
  
  fs.writeFileSync(promptFile, updated);
  return checksum;
}

// Process all prompts
const promptsDir = 'config/prompts';
const prompts = fs.readdirSync(promptsDir, { recursive: true })
  .filter(file => file.endsWith('.md'));

prompts.forEach(prompt => {
  const fullPath = path.join(promptsDir, prompt);
  const checksum = updatePromptChecksum(fullPath);
  console.log(`Updated ${prompt}: ${checksum}`);
});
```

**Run Checksum Generation**

```bash
node scripts/generate-checksums.js
```

### Step 3.3: Update Configuration

**Populate prompts.json**

```json
{
  "version": "1.0.0",
  "metadata": {
    "lastUpdated": "2025-10-29T00:00:00Z",
    "author": "team-ai",
    "environment": "production"
  },
  "prompts": {
    "helpfulAssistant": {
      "path": "system/helpful-assistant.md",
      "version": "1.0.0",
      "category": "system",
      "riskLevel": "medium",
      "checksum": "sha256:abc123...",
      "approvedBy": "security-team@example.com",
      "approvedDate": "2025-10-29T00:00:00Z",
      "description": "General purpose helpful assistant prompt",
      "tags": ["assistant", "general"]
    }
  },
  "settings": {
    "enableValidation": true,
    "requireChecksum": true,
    "allowHotReload": false,
    "maxPromptSize": 32768,
    "logAccess": true,
    "auditRetention": "365d"
  }
}
```

## Phase 4: Security Implementation

### Step 4.1: Implement Access Control

**Define Roles**

```yaml
roles:
  prompt-viewer:
    permissions:
      - read:prompts
  
  prompt-developer:
    permissions:
      - read:prompts
      - create:prompts:draft
      - update:prompts:draft
  
  prompt-approver:
    permissions:
      - read:prompts
      - approve:prompts
  
  prompt-admin:
    permissions:
      - read:prompts
      - create:prompts
      - update:prompts
      - delete:prompts
      - manage:access
```

**Implement RBAC**

```typescript
class PromptAccessControl {
  constructor(private authService: AuthService) {}
  
  async checkPermission(
    user: User,
    action: string,
    resource: string
  ): Promise<boolean> {
    const roles = await this.authService.getUserRoles(user);
    
    for (const role of roles) {
      const permissions = this.getRolePermissions(role);
      if (permissions.includes(`${action}:${resource}`)) {
        return true;
      }
    }
    
    return false;
  }
  
  async requirePermission(
    user: User,
    action: string,
    resource: string
  ): Promise<void> {
    const hasPermission = await this.checkPermission(user, action, resource);
    if (!hasPermission) {
      throw new UnauthorizedError(
        `User lacks permission: ${action}:${resource}`
      );
    }
  }
}
```

### Step 4.2: Implement Encryption

**Encrypt Prompts at Rest**

```typescript
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto';

class PromptEncryption {
  private algorithm = 'aes-256-gcm';
  private key: Buffer;
  
  constructor(keyBase64: string) {
    this.key = Buffer.from(keyBase64, 'base64');
  }
  
  encrypt(plaintext: string): EncryptedData {
    const iv = randomBytes(16);
    const cipher = createCipheriv(this.algorithm, this.key, iv);
    
    let encrypted = cipher.update(plaintext, 'utf8', 'base64');
    encrypted += cipher.final('base64');
    
    const authTag = cipher.getAuthTag();
    
    return {
      ciphertext: encrypted,
      iv: iv.toString('base64'),
      authTag: authTag.toString('base64')
    };
  }
  
  decrypt(data: EncryptedData): string {
    const decipher = createDecipheriv(
      this.algorithm,
      this.key,
      Buffer.from(data.iv, 'base64')
    );
    
    decipher.setAuthTag(Buffer.from(data.authTag, 'base64'));
    
    let decrypted = decipher.update(data.ciphertext, 'base64', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }
}
```

### Step 4.3: Implement Audit Logging

**Create Audit Logger**

```typescript
interface AuditEvent {
  timestamp: Date;
  eventType: string;
  actor: string;
  resource: string;
  action: string;
  result: 'success' | 'failure';
  metadata: Record<string, any>;
}

class AuditLogger {
  constructor(private logService: LogService) {}
  
  async log(event: AuditEvent): Promise<void> {
    const logEntry = {
      ...event,
      timestamp: event.timestamp.toISOString(),
      hash: this.generateHash(event)
    };
    
    await this.logService.write('audit', logEntry);
  }
  
  async logPromptAccess(
    user: User,
    promptId: string,
    action: 'load' | 'update' | 'delete'
  ): Promise<void> {
    await this.log({
      timestamp: new Date(),
      eventType: 'prompt.access',
      actor: user.email,
      resource: promptId,
      action: action,
      result: 'success',
      metadata: {
        userAgent: user.userAgent,
        ipAddress: user.ipAddress
      }
    });
  }
  
  private generateHash(event: AuditEvent): string {
    const crypto = require('crypto');
    const data = JSON.stringify(event);
    return crypto.createHash('sha256').update(data).digest('hex');
  }
}
```

### Step 4.4: Implement Checksum Verification

**Create Checksum Validator**

```typescript
class ChecksumValidator {
  async validate(promptPath: string, expectedChecksum: string): Promise<boolean> {
    const content = await fs.promises.readFile(promptPath, 'utf8');
    const actualChecksum = this.generateChecksum(content);
    
    if (actualChecksum !== expectedChecksum) {
      await this.auditLogger.log({
        timestamp: new Date(),
        eventType: 'security.checksum_mismatch',
        actor: 'system',
        resource: promptPath,
        action: 'validate',
        result: 'failure',
        metadata: {
          expected: expectedChecksum,
          actual: actualChecksum
        }
      });
      
      return false;
    }
    
    return true;
  }
  
  private generateChecksum(content: string): string {
    const crypto = require('crypto');
    const hash = crypto.createHash('sha256');
    hash.update(content);
    return `sha256:${hash.digest('hex')}`;
  }
}
```

## Phase 5: Integration

### Step 5.1: Create Prompt Loader

**Implement Prompt Loader**

```typescript
interface PromptLoaderConfig {
  configPath: string;
  enableValidation: boolean;
  requireChecksum: boolean;
  enableCaching: boolean;
}

class PromptLoader {
  private config: Configuration;
  private cache: Map<string, Prompt>;
  private checksumValidator: ChecksumValidator;
  private accessControl: PromptAccessControl;
  private auditLogger: AuditLogger;
  
  constructor(options: PromptLoaderConfig) {
    this.cache = new Map();
    this.checksumValidator = new ChecksumValidator();
    this.accessControl = new PromptAccessControl();
    this.auditLogger = new AuditLogger();
    
    this.loadConfiguration(options.configPath);
  }
  
  async load(promptId: string, user: User): Promise<string> {
    // Check permissions
    await this.accessControl.requirePermission(user, 'read', 'prompts');
    
    // Check cache
    if (this.cache.has(promptId)) {
      return this.cache.get(promptId)!.content;
    }
    
    // Load configuration
    const promptConfig = this.config.prompts[promptId];
    if (!promptConfig) {
      throw new Error(`Prompt not found: ${promptId}`);
    }
    
    // Load prompt file
    const promptPath = path.join('config/prompts', promptConfig.path);
    const content = await fs.promises.readFile(promptPath, 'utf8');
    
    // Validate checksum
    if (this.config.settings.requireChecksum) {
      const isValid = await this.checksumValidator.validate(
        promptPath,
        promptConfig.checksum
      );
      
      if (!isValid) {
        throw new SecurityError('Checksum validation failed');
      }
    }
    
    // Parse prompt (extract content from markdown)
    const prompt = this.parsePrompt(content);
    
    // Cache
    if (this.config.settings.enableCaching) {
      this.cache.set(promptId, prompt);
    }
    
    // Audit log
    await this.auditLogger.logPromptAccess(user, promptId, 'load');
    
    return prompt.content;
  }
  
  private parsePrompt(markdown: string): Prompt {
    // Extract frontmatter and content
    const parts = markdown.split('---');
    const frontmatter = yaml.parse(parts[1]);
    const content = parts.slice(2).join('---').trim();
    
    return {
      metadata: frontmatter,
      content: content
    };
  }
}
```

### Step 5.2: Update Application Code

**Replace Hardcoded Prompts**

```typescript
// Before
const response = await openai.chat.completions.create({
  model: 'gpt-4',
  messages: [
    {
      role: 'system',
      content: 'You are a helpful assistant...'
    },
    {
      role: 'user',
      content: userMessage
    }
  ]
});

// After
const promptLoader = new PromptLoader({ configPath: './config/prompts.json' });
const systemPrompt = await promptLoader.load('helpfulAssistant', currentUser);

const response = await openai.chat.completions.create({
  model: 'gpt-4',
  messages: [
    {
      role: 'system',
      content: systemPrompt
    },
    {
      role: 'user',
      content: userMessage
    }
  ]
});
```

## Phase 6: Validation

### Step 6.1: Security Testing

**Run Security Tests**

```bash
# Checksum validation
npm run test:security:checksum

# Access control testing
npm run test:security:access

# Encryption testing
npm run test:security:encryption

# Injection testing
npm run test:security:injection
```

**Security Test Example**

```typescript
describe('PromptLoader Security', () => {
  it('should reject tampered prompts', async () => {
    // Arrange
    const loader = new PromptLoader({ requireChecksum: true });
    const promptPath = 'config/prompts/system/test-prompt.md';
    
    // Tamper with file
    const original = await fs.promises.readFile(promptPath, 'utf8');
    await fs.promises.writeFile(promptPath, original + '\n// malicious code');
    
    // Act & Assert
    await expect(loader.load('testPrompt', user))
      .rejects.toThrow('Checksum validation failed');
    
    // Cleanup
    await fs.promises.writeFile(promptPath, original);
  });
});
```

### Step 6.2: Compliance Validation

Use the [Security Checklist](security-checklist.md) to validate compliance.

### Step 6.3: Performance Testing

**Test Prompt Loading Performance**

```typescript
describe('PromptLoader Performance', () => {
  it('should load prompts within acceptable time', async () => {
    const loader = new PromptLoader({ enableCaching: true });
    
    const start = Date.now();
    await loader.load('helpfulAssistant', user);
    const duration = Date.now() - start;
    
    expect(duration).toBeLessThan(100); // 100ms threshold
  });
  
  it('should benefit from caching', async () => {
    const loader = new PromptLoader({ enableCaching: true });
    
    // First load
    const start1 = Date.now();
    await loader.load('helpfulAssistant', user);
    const duration1 = Date.now() - start1;
    
    // Second load (cached)
    const start2 = Date.now();
    await loader.load('helpfulAssistant', user);
    const duration2 = Date.now() - start2;
    
    expect(duration2).toBeLessThan(duration1 * 0.1);
  });
});
```

## Phase 7: Deployment

### Step 7.1: Staged Rollout

**Development Environment**

```bash
# Deploy to development
git checkout develop
git merge feature/upss-implementation
npm run deploy:dev
```

**Staging Environment**

```bash
# Deploy to staging
git checkout staging
git merge develop
npm run deploy:staging

# Run smoke tests
npm run test:smoke
```

**Production Environment**

```bash
# Deploy to production
git checkout main
git merge staging
npm run deploy:production

# Monitor
npm run monitor:production
```

### Step 7.2: Rollback Plan

**Prepare Rollback**

```bash
# Tag current version
git tag -a v1.0.0-pre-upss -m "Before UPSS implementation"
git push origin v1.0.0-pre-upss

# Create rollback script
cat > scripts/rollback.sh << 'EOF'
#!/bin/bash
git checkout v1.0.0-pre-upss
npm run deploy:production
EOF

chmod +x scripts/rollback.sh
```

## Phase 8: Operations

### Step 8.1: Monitoring

**Configure Monitoring**

```yaml
monitors:
  - name: Prompt Load Time
    metric: prompt.load.duration
    threshold: 100ms
    alert: team-ops@example.com
  
  - name: Checksum Validation Failures
    metric: security.checksum.failures
    threshold: 1
    alert: team-security@example.com
  
  - name: Unauthorized Access Attempts
    metric: security.access.denied
    threshold: 5
    alert: team-security@example.com
```

### Step 8.2: Maintenance

**Regular Maintenance Tasks**

```bash
# Weekly: Review audit logs
npm run audit:review

# Monthly: Update dependencies
npm update
npm audit fix

# Quarterly: Security review
npm run security:review

# Annually: Compliance audit
npm run compliance:audit
```

## Troubleshooting

### Common Issues

**Issue: Checksum Validation Fails**

```
Error: Checksum validation failed for prompt 'helpfulAssistant'
Expected: sha256:abc123...
Actual:   sha256:def456...
```

Solution:
```bash
# Regenerate checksums
node scripts/generate-checksums.js

# Update configuration
node scripts/update-config.js
```

**Issue: Permission Denied**

```
Error: User lacks permission: read:prompts
```

Solution:
```typescript
// Grant necessary permissions
await accessControl.grantRole(user, 'prompt-viewer');
```

**Issue: Prompt Not Found**

```
Error: Prompt not found: 'nonexistentPrompt'
```

Solution:
```bash
# Verify prompt exists
ls config/prompts/**/*.md | grep nonexistent

# Add to configuration
vim config/prompts.json
```

## Best Practices

1. **Version Control:** Always use version control for prompts
2. **Code Review:** Require peer review for all prompt changes
3. **Testing:** Test prompts before production deployment
4. **Monitoring:** Monitor prompt usage and performance
5. **Documentation:** Keep documentation up to date
6. **Security:** Follow all mandatory security controls
7. **Backup:** Maintain regular backups of prompts
8. **Training:** Ensure team is trained on UPSS procedures

## Next Steps

After completing implementation:

1. Review [Security Checklist](security-checklist.md)
2. Set up [Governance](governance.md) processes
3. Verify [Compliance](compliance.md) alignment
4. Train team on procedures
5. Schedule regular security reviews

## Support

For implementation support:
- GitHub Discussions: https://github.com/alvinveroy/prompt-security-standard/discussions
- Email: support@upss-standard.org
