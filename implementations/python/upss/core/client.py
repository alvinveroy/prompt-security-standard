import asyncio
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from .models import PromptContent, AuditEntry
from .exceptions import (
    UPSSError,
    NotFoundError,
    ConflictError,
    ConfigurationError,
    PermissionError,
    IntegrityError,
)
from ..storage.filesystem import FilesystemStorage
from ..security.scanner import sanitize, render, calculate_risk_score, detect_pii


class UPSSClient:
    """Client for interacting with UPSS prompt storage."""

    def __init__(
        self,
        mode: str = "filesystem",
        base_path: str = "./prompts",
        db_url: Optional[str] = None,
        enable_rbac: bool = False,
        enable_checksum: bool = True,
        block_pii: bool = False,
    ):
        """Initialize UPSS client with configuration.

        Args:
            mode: Storage mode - "filesystem" or "postgresql"
            base_path: Base path for filesystem storage
            db_url: PostgreSQL connection string for postgresql mode
            enable_rbac: Enable role-based access control
            enable_checksum: Enable checksum verification
            block_pii: Enable PII blocking
        """
        if mode not in ["filesystem", "postgresql"]:
            raise ConfigurationError(f"Invalid mode: {mode}")

        self._mode = mode
        self._base_path = Path(base_path)
        self._db_url = db_url
        self._enable_rbac = enable_rbac
        self._enable_checksum = enable_checksum
        self._block_pii = block_pii
        self._audit_log = []

        # Initialize storage
        if mode == "filesystem":
            self.storage = FilesystemStorage(
                self._base_path, enable_checksum=self._enable_checksum
            )
        else:
            raise NotImplementedError("PostgreSQL mode not yet implemented")

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def base_path(self) -> Path:
        return self._base_path

    @property
    def db_url(self) -> Optional[str]:
        return self._db_url

    @property
    def enable_rbac(self) -> bool:
        return self._enable_rbac

    @property
    def enable_checksum(self) -> bool:
        return self._enable_checksum

    @property
    def block_pii(self) -> bool:
        return self._block_pii

    async def load(
        self, name: str, user_id: str, version: Optional[str] = None
    ) -> PromptContent:
        """Load a prompt by name and optionally version.

        Args:
            name: Prompt name
            user_id: User ID requesting the prompt
            version: Specific version to load, or None for latest

        Returns:
            PromptContent object

        Raises:
            NotFoundError: If prompt not found
            PermissionError: If user lacks permissions
            IntegrityError: If checksum verification fails
        """
        # Check permissions if RBAC enabled
        if self._enable_rbac:
            # TODO: Implement RBAC permission check
            pass

        prompt_content = await self.storage.load(name, version)

        # Log access
        self._log_access(name, user_id, "load", version)

        return prompt_content

    async def create(
        self,
        name: str,
        content: str,
        user_id: str,
        version: str = "1.0.0",
        category: str = "user",
        risk_level: str = "medium",
    ) -> str:
        """Create a new prompt.

        Args:
            name: Prompt name
            content: Prompt content
            user_id: User ID creating the prompt
            version: Version string (default "1.0.0")
            category: Prompt category (default "user")
            risk_level: Risk level (default "medium")

        Returns:
            UUID of the created prompt

        Raises:
            ConflictError: If prompt with same name+version exists
            PermissionError: If user lacks permissions
        """
        # Check permissions if RBAC enabled
        if self._enable_rbac:
            # TODO: Implement RBAC permission check
            pass

        prompt_id = await self.storage.create(
            name=name,
            content=content,
            version=version,
            category=category,
            risk_level=risk_level,
            user_id=user_id,
        )

        # Log creation
        self._log_access(name, user_id, "create", version)

        return prompt_id

    def _log_access(
        self, name: str, user_id: str, action: str, version: Optional[str] = None
    ):
        """Log access to audit log."""
        entry = AuditEntry(
            timestamp=datetime.utcnow(),
            event_type=action,
            user_id=user_id,
            prompt_name=name,
            success=True,
            details={"version": version} if version else {},
        )
        self._audit_log.append(entry)

    def get_audit_log(self) -> list[AuditEntry]:
        """Get the audit log."""
        return self._audit_log.copy()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def rollback(self, name: str, to_version: str) -> bool:
        """Rollback a prompt to a previous version.

        Args:
            name: Prompt name
            to_version: Target version to rollback to

        Returns:
            True if successful

        Raises:
            NotFoundError: If prompt or version not found
        """
        # Check permissions if RBAC enabled
        if self._enable_rbac:
            # TODO: Implement RBAC permission check
            pass

        success = await self.storage.rollback(name, to_version)

        # Log rollback
        self._log_access(name, "system", "rollback", to_version)

        return success

    async def render(
        self,
        system_prompt: str,
        user_input: str,
        style: str = "xml",
        allow_unsafe: bool = False,
    ) -> str:
        """Render a prompt with security checks.

        Args:
            system_prompt: System prompt content
            user_input: User input to render
            style: Rendering style ("xml" or "markdown")
            allow_unsafe: Allow unsafe content

        Returns:
            Rendered prompt string
        """
        return render(system_prompt, user_input, style=style, allow_unsafe=allow_unsafe)

    async def sanitize(self, user_input: str) -> tuple[str, bool]:
        """Sanitize user input for security.

        Args:
            user_input: Raw user input

        Returns:
            Tuple of (sanitized_input, was_clean)
        """
        return sanitize(user_input)

    async def audit_query(self, limit: Optional[int] = None) -> List[AuditEntry]:
        """Query audit log from persistent storage.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of audit entries
        """
        audit_file = self._base_path / "audit.jsonl"
        entries = []

        if audit_file.exists():
            with open(audit_file, "r") as f:
                for line in f:
                    if limit and len(entries) >= limit:
                        break
                    try:
                        data = json.loads(line.strip())
                        entry = AuditEntry(
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            event_type=data["event_type"],
                            user_id=data["user_id"],
                            prompt_name=data["prompt_name"],
                            success=data["success"],
                            details=data.get("details", {}),
                        )
                        entries.append(entry)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

        return entries

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup if needed
        pass
