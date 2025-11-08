# UPSS v1.1.0 Middleware Architecture

## Overview

UPSS v1.1.0 introduces a modular middleware architecture that allows you to compose security primitives based on your specific needs. Instead of a monolithic security framework, you can now pick and choose the security features you need and add them incrementally.

> **Note:** This is a preview of the new middleware architecture. The v1.x `UPSSClient` remains the primary interface and is fully supported.

## Quick Start

```python
from upss import SecurityPipeline, SecurityContext, BasicSanitizer

# Create a pipeline with basic security
pipeline = SecurityPipeline()
pipeline.use(BasicSanitizer())

# Process a prompt
context = SecurityContext(user_id="alice", prompt_id="greeting")
result = await pipeline.execute(user_prompt, context)

if result.is_safe:
    # Use the secure prompt
    response = await llm.generate(result.prompt)
else:
    # Handle security violations
    print(f"Security issues: {result.violations}")
```

## Core Concepts

### SecurityContext

Contains information about the security operation:

```python
context = SecurityContext(
    user_id="alice",              # Required: User identifier
    prompt_id="summarization",    # Required: Prompt identifier
    risk_level="medium",          # Optional: low, medium, high (default: medium)
    environment="production",     # Optional: development, staging, production (default: production)
    metadata={"role": "admin"}    # Optional: Additional context
)
```

### SecurityResult

The result of processing a prompt through the pipeline:

```python
result = await pipeline.execute(prompt, context)

# Check if prompt is safe
if result.is_safe:
    print("Prompt passed all security checks")

# Get risk score (0.0 = safe, 1.0 = maximum risk)
print(f"Risk score: {result.risk_score}")

# Get violations
for violation in result.violations:
    print(f"Violation: {violation}")

# Get the processed prompt (may be modified by middleware)
secure_prompt = result.prompt

# Get metadata from middleware
print(result.metadata)
```

### SecurityPipeline

Composes multiple security middleware into a processing pipeline:

```python
pipeline = SecurityPipeline()

# Add middleware (executes in order)
pipeline.use(InputValidator())
pipeline.use(BasicSanitizer())
pipeline.use(LightweightAuditor())

# Or use fluent interface
pipeline = (SecurityPipeline()
           .use(InputValidator())
           .use(BasicSanitizer())
           .use(LightweightAuditor()))

# Execute pipeline
result = await pipeline.execute(prompt, context)
```

## Available Middleware

### Essential Primitives (Start Here)

#### BasicSanitizer

Blocks common prompt injection patterns.

**What it does:**
- Detects injection patterns (ignore previous, act as, etc.)
- Redacts suspicious content
- Returns risk score based on violations

**Usage:**
```python
from upss import BasicSanitizer

pipeline.use(BasicSanitizer())

# Or with custom patterns
pipeline.use(BasicSanitizer(
    block_patterns=[
        r"custom_pattern_1",
        r"custom_pattern_2"
    ]
))
```

**Patterns blocked by default:**
- Instruction override: "ignore previous instructions", "disregard above"
- Role confusion: "you are now", "act as if", "pretend to be"
- System injection: "system:", "<|im_start|>"
- Privilege escalation: "admin mode", "sudo mode", "god mode"

#### LightweightAuditor

Logs all prompt access for audit trail.

**What it does:**
- Logs timestamp, user, prompt ID, risk level
- Stores in JSONL format (one JSON object per line)
- Provides query interface for audit logs
- Never blocks prompts (always returns safe)

**Usage:**
```python
from upss import LightweightAuditor

pipeline.use(LightweightAuditor())

# Or with custom log path
auditor = LightweightAuditor(log_path="logs/custom_audit.jsonl")
pipeline.use(auditor)

# Query logs
results = auditor.query_logs(
    user_id="alice",
    limit=100
)
```

#### InputValidator

Validates prompt inputs at runtime.

**What it does:**
- Checks for null bytes
- Detects control characters
- Validates UTF-8 encoding
- Enforces length limits
- Detects empty prompts

**Usage:**
```python
from upss import InputValidator

pipeline.use(InputValidator())

# Or with custom max length
pipeline.use(InputValidator(max_length=5000))
```

#### SimpleRBAC

Role-based access control.

**What it does:**
- Enforces access based on user roles
- Maps roles to allowed prompt categories
- Blocks unauthorized access

**Usage:**
```python
from upss import SimpleRBAC

pipeline.use(SimpleRBAC())

# Or with custom roles
pipeline.use(SimpleRBAC(roles_config={
    "admin": {"system", "user", "fallback"},
    "developer": {"user", "fallback"},
    "user": {"user"}
}))

# Use with context metadata
context = SecurityContext(
    user_id="alice",
    prompt_id="system-prompt",
    metadata={"role": "user", "category": "system"}
)
```

**Default roles:**
- `admin`: Can access all categories (system, user, fallback, internal)
- `developer`: Can access user, fallback, internal
- `user`: Can only access user prompts

## Progressive Adoption

### Phase 1: Basic Safety (Day 1)

Start with essential security:

```python
pipeline = SecurityPipeline()
pipeline.use(BasicSanitizer())  # Block 90% of injection attacks
```

### Phase 2: Team Usage (Week 1)

Add audit and access control:

```python
pipeline = SecurityPipeline()
pipeline.use(InputValidator())      # Validate inputs
pipeline.use(BasicSanitizer())      # Block injections
pipeline.use(LightweightAuditor())  # Track usage
```

### Phase 3: Production Ready (Month 1)

Add role-based access:

```python
pipeline = SecurityPipeline()
pipeline.use(InputValidator())
pipeline.use(BasicSanitizer())
pipeline.use(SimpleRBAC())          # Enforce access control
pipeline.use(LightweightAuditor())
```

## Creating Custom Middleware

You can create your own security middleware by extending `SecurityMiddleware`:

```python
from upss import SecurityMiddleware, SecurityContext, SecurityResult

class CustomBusinessLogic(SecurityMiddleware):
    """Custom middleware for business-specific rules."""
    
    async def process(
        self, 
        prompt: str, 
        context: SecurityContext
    ) -> SecurityResult:
        violations = []
        
        # Example: Block prompts mentioning competitors
        competitors = ["CompetitorA", "CompetitorB"]
        for competitor in competitors:
            if competitor.lower() in prompt.lower():
                violations.append(f"Mention of competitor: {competitor}")
        
        # Example: Require approval for high-value operations
        high_value_keywords = ["delete", "transfer", "payment"]
        if any(kw in prompt.lower() for kw in high_value_keywords):
            if not context.metadata.get("approved"):
                violations.append("High-value operation requires approval")
        
        return SecurityResult(
            prompt=prompt,
            is_safe=len(violations) == 0,
            risk_score=0.8 if violations else 0.0,
            violations=violations,
            metadata={"custom_check": "complete"}
        )

# Use your custom middleware
pipeline = SecurityPipeline()
pipeline.use(CustomBusinessLogic())
```

## Framework Integration

### FastAPI

```python
from fastapi import FastAPI, HTTPException
from upss import SecurityPipeline, SecurityContext, BasicSanitizer
from pydantic import BaseModel

app = FastAPI()
pipeline = SecurityPipeline().use(BasicSanitizer())

class PromptRequest(BaseModel):
    prompt: str
    user_id: str

@app.post("/chat")
async def chat(request: PromptRequest):
    context = SecurityContext(
        user_id=request.user_id,
        prompt_id="chat"
    )
    
    result = await pipeline.execute(request.prompt, context)
    
    if not result.is_safe:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Prompt failed security validation",
                "violations": result.violations
            }
        )
    
    # Use secure prompt with LLM
    response = await llm.generate(result.prompt)
    return {"response": response}
```

### Flask

```python
from flask import Flask, request, jsonify
from upss import SecurityPipeline, SecurityContext, BasicSanitizer

app = Flask(__name__)
pipeline = SecurityPipeline().use(BasicSanitizer())

@app.route("/chat", methods=["POST"])
async def chat():
    data = request.json
    
    context = SecurityContext(
        user_id=data["user_id"],
        prompt_id="chat"
    )
    
    result = await pipeline.execute(data["prompt"], context)
    
    if not result.is_safe:
        return jsonify({
            "error": "Security validation failed",
            "violations": result.violations
        }), 400
    
    response = await llm.generate(result.prompt)
    return jsonify({"response": response})
```

## Performance

### Benchmarks

- **BasicSanitizer**: <5ms average latency
- **InputValidator**: <2ms average latency
- **LightweightAuditor**: <3ms average latency (file I/O)
- **SimpleRBAC**: <1ms average latency

### Optimization Tips

1. **Order matters**: Put faster middleware first
2. **Use caching**: Cache pipeline instances
3. **Async all the way**: Use async/await throughout
4. **Batch processing**: Process multiple prompts concurrently

```python
# Cache pipeline instance
from functools import lru_cache

@lru_cache(maxsize=1)
def get_pipeline():
    pipeline = SecurityPipeline()
    pipeline.use(BasicSanitizer())
    return pipeline

# Batch processing
import asyncio

results = await asyncio.gather(*[
    pipeline.execute(prompt, context)
    for prompt in prompts
])
```

## Migration from v1.x

If you're using UPSS v1.x, here's how to migrate:

### Before (v1.x)

```python
from upss import UPSSClient

client = UPSSClient(
    mode="filesystem",
    enable_rbac=True,
    enable_checksum=True
)

prompt = await client.load("greeting", user_id="alice")
```

### After (v2.0)

```python
from upss import SecurityPipeline, SecurityContext, BasicSanitizer, SimpleRBAC

# Create pipeline with equivalent security
pipeline = SecurityPipeline()
pipeline.use(BasicSanitizer())
pipeline.use(SimpleRBAC())

# Load and process prompt
context = SecurityContext(
    user_id="alice",
    prompt_id="greeting",
    metadata={"role": "user", "category": "user"}
)

result = await pipeline.execute(prompt_content, context)

if result.is_safe:
    # Use secure prompt
    pass
```

**Note:** v1.x `UPSSClient` is still available for backward compatibility.

## Best Practices

1. **Start Simple**: Begin with `BasicSanitizer` only
2. **Add Incrementally**: Add more middleware as needs grow
3. **Test Thoroughly**: Test with both safe and malicious prompts
4. **Monitor Performance**: Track latency and throughput
5. **Review Audit Logs**: Regularly review security events
6. **Update Patterns**: Keep injection patterns up to date
7. **Custom Middleware**: Create business-specific security rules

## Troubleshooting

### Pipeline blocks safe prompts

- Review violation messages in `result.violations`
- Check if patterns are too broad
- Consider using custom patterns with `BasicSanitizer`

### Performance issues

- Check middleware order (put faster middleware first)
- Use pipeline caching
- Consider async batch processing
- Profile individual middleware

### Audit logs not created

- Check file permissions
- Verify log directory exists
- Check disk space
- Review error in `result.metadata`

## Examples

See the `examples/python/` directory for complete examples:

- `basic_middleware_usage.py` - Basic usage demonstration
- `custom_middleware.py` - Creating custom middleware
- `fastapi_integration.py` - FastAPI integration
- `flask_integration.py` - Flask integration

## Contributing

We welcome contributions of new security middleware! See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../../LICENSE) for details.
