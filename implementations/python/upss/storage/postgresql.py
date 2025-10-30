"""PostgreSQL storage backend for UPSS."""

from pathlib import Path
from typing import Optional

from ..core.exceptions import (
    ConfigurationError,
    IntegrityError,
    NotFoundError,
)
from ..core.models import PromptContent


class PostgreSQLStorage:
    """PostgreSQL-based storage for prompts (Enterprise Edition)."""

    def __init__(self, db_url: str, base_path: Path, enable_checksum: bool = True):
        """
        Initialize PostgreSQL storage.

        Args:
            db_url: PostgreSQL connection string
            base_path: Base path for storing prompt content files
            enable_checksum: Enable checksum verification
        """
        self.db_url = db_url
        self.base_path = base_path
        self.enable_checksum = enable_checksum
        self.pool = None
        raise NotImplementedError(
            "PostgreSQL mode is not yet implemented in this version. "
            "Please use filesystem mode or contribute to implementation."
        )

    async def init_pool(self) -> None:
        """Initialize connection pool."""
        pass

    async def load(self, name: str, version: Optional[str] = None) -> PromptContent:
        """Load prompt from PostgreSQL."""
        pass

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
        """Create new prompt in PostgreSQL."""
        pass

    async def rollback(self, name: str, to_version: str) -> bool:
        """Rollback to previous version."""
        pass
