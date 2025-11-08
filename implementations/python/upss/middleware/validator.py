"""
Runtime input validation middleware.

This module provides validation of prompt inputs at runtime to catch
malformed or malicious content.
"""

from ..core.middleware import SecurityMiddleware, SecurityContext, SecurityResult


class InputValidator(SecurityMiddleware):
    """
    Runtime input validation middleware.
    
    Validates prompt inputs for:
    - Null bytes
    - Control characters
    - Encoding issues
    - Length limits
    
    Example:
        pipeline = SecurityPipeline()
        pipeline.use(InputValidator())
        
        # Or with custom max length
        pipeline.use(InputValidator(max_length=5000))
    """
    
    def __init__(self, max_length: int = 10000):
        """
        Initialize the validator.
        
        Args:
            max_length: Maximum allowed prompt length
        """
        self.max_length = max_length
    
    async def process(
        self, 
        prompt: str, 
        context: SecurityContext
    ) -> SecurityResult:
        """
        Validate prompt input.
        
        Args:
            prompt: The prompt text to validate
            context: Security context
            
        Returns:
            SecurityResult indicating whether input is valid
        """
        violations = []
        
        # Check for null bytes
        if "\x00" in prompt:
            violations.append("Null bytes detected in prompt")
        
        # Check for control characters (except tab, newline, carriage return)
        control_chars = [chr(i) for i in range(32) if i not in (9, 10, 13)]
        found_control_chars = [c for c in control_chars if c in prompt]
        if found_control_chars:
            violations.append(
                f"Control characters detected: {[ord(c) for c in found_control_chars]}"
            )
        
        # Check encoding
        try:
            prompt.encode('utf-8')
        except UnicodeEncodeError as e:
            violations.append(f"Invalid UTF-8 encoding: {str(e)}")
        
        # Check length
        if len(prompt) > self.max_length:
            violations.append(
                f"Prompt exceeds maximum length: {len(prompt)} > {self.max_length}"
            )
        
        # Check if prompt is empty or only whitespace
        if not prompt.strip():
            violations.append("Prompt is empty or contains only whitespace")
        
        # Calculate risk score
        risk_score = min(len(violations) * 0.4, 1.0)
        
        return SecurityResult(
            prompt=prompt,
            is_safe=len(violations) == 0,
            risk_score=risk_score,
            violations=violations,
            metadata={
                "validation": "complete",
                "prompt_length": len(prompt),
                "max_length": self.max_length
            }
        )
