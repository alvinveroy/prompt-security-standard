"""Audit logging for UPSS."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..core.models import AuditEntry


class AuditLogger:
    """Handles audit logging for UPSS operations."""

    def __init__(self, audit_file: Path):
        """
        Initialize audit logger.

        Args:
            audit_file: Path to audit log file (JSONL format)
        """
        self.audit_file = audit_file
        self.audit_file.touch(exist_ok=True)

    def log(
        self,
        event_type: str,
        user_id: str,
        prompt_name: str,
        success: bool,
        details: Optional[dict] = None,
    ) -> None:
        """
        Log an audit event.

        Args:
            event_type: Type of event (read, create, update, delete, etc.)
            user_id: User performing the action
            prompt_name: Target prompt name
            success: Whether operation succeeded
            details: Additional details
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "prompt_name": prompt_name,
            "success": success,
            "details": details or {},
        }

        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def query(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[AuditEntry]:
        """
        Query audit log.

        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            List of matching audit entries
        """
        results = []

        with open(self.audit_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                entry_dict = json.loads(line)
                entry_time = datetime.fromisoformat(entry_dict["timestamp"])

                # Apply filters
                if user_id and entry_dict.get("user_id") != user_id:
                    continue
                if event_type and entry_dict.get("event_type") != event_type:
                    continue
                if start_date and entry_time < start_date:
                    continue
                if end_date and entry_time > end_date:
                    continue

                results.append(
                    AuditEntry(
                        timestamp=entry_time,
                        event_type=entry_dict["event_type"],
                        user_id=entry_dict["user_id"],
                        prompt_name=entry_dict["prompt_name"],
                        success=entry_dict["success"],
                        details=entry_dict.get("details", {}),
                    )
                )

        return results
