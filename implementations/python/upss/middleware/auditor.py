"""
Lightweight audit logging middleware.

This module provides simple, file-based audit logging without requiring
complex infrastructure setup.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from ..core.middleware import SecurityMiddleware, SecurityContext, SecurityResult


class LightweightAuditor(SecurityMiddleware):
    """
    Minimal audit logging middleware.
    
    Logs all prompt access to a JSONL (JSON Lines) file for audit trail.
    No complex infrastructure required - just file-based logging.
    
    Each log entry includes:
    - Timestamp (ISO 8601 format)
    - User ID
    - Prompt ID
    - Risk level
    - Environment
    - Prompt length and preview
    
    Example:
        pipeline = SecurityPipeline()
        pipeline.use(LightweightAuditor())
        
        # Or with custom log path
        pipeline.use(LightweightAuditor(log_path="logs/custom_audit.jsonl"))
    """
    
    def __init__(self, log_path: str = "logs/upss_audit.jsonl"):
        """
        Initialize the auditor.
        
        Args:
            log_path: Path to the audit log file (JSONL format)
        """
        self.log_path = Path(log_path)
        
        # Create log directory if it doesn't exist
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create log file if it doesn't exist
        if not self.log_path.exists():
            self.log_path.touch()
    
    async def process(
        self, 
        prompt: str, 
        context: SecurityContext
    ) -> SecurityResult:
        """
        Log prompt access and pass through unchanged.
        
        Args:
            prompt: The prompt text
            context: Security context
            
        Returns:
            SecurityResult marking prompt as safe (auditor doesn't block)
        """
        # Create audit entry
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": context.user_id,
            "prompt_id": context.prompt_id,
            "risk_level": context.risk_level,
            "environment": context.environment,
            "prompt_length": len(prompt),
            "prompt_preview": prompt[:100] if len(prompt) > 100 else prompt,
            "metadata": context.metadata
        }
        
        # Append to log file (JSONL format - one JSON object per line)
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_entry) + "\n")
            
            logged = True
            error = None
        except Exception as e:
            logged = False
            error = str(e)
        
        # Auditor never blocks - always returns safe
        return SecurityResult(
            prompt=prompt,
            is_safe=True,
            risk_score=0.0,
            violations=[],
            metadata={
                "audited": logged,
                "log_path": str(self.log_path),
                "error": error
            }
        )
    
    def query_logs(
        self,
        user_id: Optional[str] = None,
        prompt_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> list:
        """
        Query audit logs with filters.
        
        Args:
            user_id: Filter by user ID
            prompt_id: Filter by prompt ID
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of entries to return
            
        Returns:
            List of audit entries matching filters
        """
        if not self.log_path.exists():
            return []
        
        results = []
        
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if len(results) >= limit:
                    break
                
                try:
                    entry = json.loads(line.strip())
                    
                    # Apply filters
                    if user_id and entry.get("user_id") != user_id:
                        continue
                    
                    if prompt_id and entry.get("prompt_id") != prompt_id:
                        continue
                    
                    if start_time:
                        entry_time = datetime.fromisoformat(
                            entry["timestamp"].replace("Z", "+00:00")
                        )
                        if entry_time < start_time:
                            continue
                    
                    if end_time:
                        entry_time = datetime.fromisoformat(
                            entry["timestamp"].replace("Z", "+00:00")
                        )
                        if entry_time > end_time:
                            continue
                    
                    results.append(entry)
                    
                except (json.JSONDecodeError, KeyError):
                    # Skip malformed entries
                    continue
        
        return results
