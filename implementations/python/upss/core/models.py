"""Data models for UPSS."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class PromptContent:
    """Represents a prompt with its content and metadata."""

    id: str
    name: str
    content: str
    version: str
    category: str
    risk_level: str
    checksum: str
    created_at: datetime
    updated_at: datetime
    approved: bool = False
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditEntry:
    """Represents an audit log entry."""

    timestamp: datetime
    event_type: str
    user_id: str
    prompt_name: str
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MigrationReport:
    """Report for batch migration operations."""

    total: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
