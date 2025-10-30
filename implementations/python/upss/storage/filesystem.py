"""Filesystem storage backend for UPSS."""

import json
import hashlib
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import filelock
import uuid

from ..core.models import PromptContent
from ..core.exceptions import (
    NotFoundError,
    ConflictError,
    StorageError,
    IntegrityError,
)


class FilesystemStorage:
    """Filesystem-based storage for prompts."""

    def __init__(self, base_path: Path, enable_checksum: bool = True):
        """
        Initialize filesystem storage.

        Args:
            base_path: Base directory for prompts
            enable_checksum: Enable checksum verification
        """
        self.base_path = base_path
        self.enable_checksum = enable_checksum
        self._ensure_structure()

    def _ensure_structure(self):
        """Create required directory structure."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "metadata.json").touch(exist_ok=True)
        (self.base_path / "audit.jsonl").touch(exist_ok=True)
        (self.base_path / "roles.json").touch(exist_ok=True)

        # Initialize empty metadata if file is empty
        metadata_file = self.base_path / "metadata.json"
        if metadata_file.stat().st_size == 0:
            with open(metadata_file, "w") as f:
                json.dump({"prompts": {}}, f, indent=2)

        # Initialize empty roles if file is empty
        roles_file = self.base_path / "roles.json"
        if roles_file.stat().st_size == 0:
            with open(roles_file, "w") as f:
                json.dump({"roles": {}, "assignments": {}}, f, indent=2)

    async def load(self, name: str, version: Optional[str] = None) -> PromptContent:
        """
        Load a prompt from filesystem.

        Args:
            name: Prompt name
            version: Specific version or None for latest

        Returns:
            PromptContent object

        Raises:
            NotFoundError: If prompt not found
            IntegrityError: If checksum fails
        """
        # Load metadata
        metadata = self._load_metadata()
        if name not in metadata["prompts"]:
            raise NotFoundError(f"Prompt not found: {name}")

        prompt_meta = metadata["prompts"][name]

        # Determine version
        if version is None:
            version = prompt_meta.get("latest_version")
            if not version:
                raise NotFoundError(f"No versions found for: {name}")

        # Check if version exists
        if version not in prompt_meta.get("versions", {}):
            raise NotFoundError(f"Version {version} not found for: {name}")

        version_meta = prompt_meta["versions"][version]

        # Load content file
        content_path = self.base_path / version_meta["path"]
        if not content_path.exists():
            raise NotFoundError(f"Content file not found: {content_path}")

        with open(content_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify checksum
        if self.enable_checksum:
            calculated = hashlib.sha256(content.encode()).hexdigest()
            expected = version_meta.get("checksum")
            if calculated != expected:
                raise IntegrityError(
                    f"Checksum mismatch for {name}@{version}",
                    details={
                        "expected": expected,
                        "actual": calculated,
                    },
                )

        return PromptContent(
            id=version_meta.get("id"),
            name=name,
            content=content,
            version=version,
            category=version_meta.get("category", "user"),
            risk_level=version_meta.get("risk_level", "medium"),
            checksum=version_meta.get("checksum"),
            created_at=datetime.fromisoformat(version_meta.get("created_at")),
            updated_at=datetime.fromisoformat(version_meta.get("updated_at")),
            approved=version_meta.get("approved", False),
            approved_by=version_meta.get("approved_by"),
            approved_date=(
                datetime.fromisoformat(version_meta["approved_date"])
                if version_meta.get("approved_date")
                else None
            ),
            metadata=version_meta.get("metadata", {}),
        )

    async def create(
        self,
        name: str,
        content: str,
        version: str,
        category: str,
        risk_level: str,
        user_id: str,
        approved: bool = False,
    ) -> str:
        """
        Create a new prompt version.

        Args:
            name: Prompt name
            content: Prompt content
            version: Version string
            category: Category
            risk_level: Risk level
            user_id: Creating user
            approved: Approval status

        Returns:
            Prompt UUID

        Raises:
            ConflictError: If version exists
        """
        # Use file lock to prevent concurrent writes
        lock_file = self.base_path / ".upss.lock"
        lock = filelock.FileLock(lock_file, timeout=10)

        with lock:
            metadata = self._load_metadata()

            # Check for conflicts
            if name in metadata["prompts"]:
                if version in metadata["prompts"][name].get("versions", {}):
                    raise ConflictError(f"Version {version} already exists for {name}")
            else:
                metadata["prompts"][name] = {
                    "name": name,
                    "versions": {},
                    "latest_version": None,
                }

            # Generate UUID
            prompt_id = str(uuid.uuid4())

            # Calculate checksum
            checksum = hashlib.sha256(content.encode()).hexdigest()

            # Create content file path
            content_path = f"{name}/{version}.md"
            full_path = self.base_path / content_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Update metadata
            now = datetime.utcnow().isoformat()
            version_meta = {
                "id": prompt_id,
                "version": version,
                "category": category,
                "risk_level": risk_level,
                "checksum": checksum,
                "path": content_path,
                "created_at": now,
                "updated_at": now,
                "created_by": user_id,
                "approved": approved,
                "approved_by": None,
                "approved_date": None,
            }

            metadata["prompts"][name]["versions"][version] = version_meta
            metadata["prompts"][name]["latest_version"] = version

            self._save_metadata(metadata)

            return prompt_id

    async def rollback(self, name: str, to_version: str) -> bool:
        """
        Rollback to a previous version.

        Args:
            name: Prompt name
            to_version: Target version

        Returns:
            True if successful

        Raises:
            NotFoundError: If prompt or version not found
        """
        lock_file = self.base_path / ".upss.lock"
        lock = filelock.FileLock(lock_file, timeout=10)

        with lock:
            metadata = self._load_metadata()

            if name not in metadata["prompts"]:
                raise NotFoundError(f"Prompt not found: {name}")

            if to_version not in metadata["prompts"][name].get("versions", {}):
                raise NotFoundError(f"Version {to_version} not found for: {name}")

            # Update latest version pointer
            metadata["prompts"][name]["latest_version"] = to_version
            self._save_metadata(metadata)

            return True

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from file."""
        metadata_file = self.base_path / "metadata.json"
        with open(metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_metadata(self, metadata: Dict[str, Any]):
        """Save metadata to file."""
        metadata_file = self.base_path / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
