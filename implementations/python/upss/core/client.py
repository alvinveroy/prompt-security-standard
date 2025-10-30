import asyncio
import hashlib
import json
from pathlib import Path
from typing import Optional

from .models import PromptContent, AuditEntry
from .exceptions import (
    UPSSError,
    NotFoundError,
    ConflictError,
    ConfigurationError,
    PermissionError,
    IntegrityError
)


class UPSSClient:
    """Client for interacting with UPSS prompt storage."""
    
    def __init__(
        self,
        mode: str = "filesystem",
        base_path: str = "./prompts",
        db_url: Optional[str] = None,
        enable_rbac: bool = False,
        enable_checksum: bool = True,
        block_pii: bool = False
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
            self._base_path.mkdir(parents=True, exist_ok=True)
    
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
    
    async def load(self, name: str, user_id: str, version: Optional[str] = None) -> PromptContent:
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
        
        if self._mode == "filesystem":
            return await self._load_filesystem(name, user_id, version)
        else:
            raise NotImplementedError("PostgreSQL mode not yet implemented")
    
    async def _load_filesystem(self, name: str, user_id: str, version: Optional[str]) -> PromptContent:
        """Load prompt from filesystem storage."""
        prompt_dir = self._base_path / name
        
        if not prompt_dir.exists():
            raise NotFoundError(f"Prompt not found: {name}")
        
        # Find version to load
        if version is None:
            # Load latest version
            version_file = prompt_dir / "latest.json"
            if not version_file.exists():
                raise NotFoundError(f"No versions found for prompt: {name}")
            
            with open(version_file, 'r') as f:
                latest_info = json.load(f)
                version = latest_info['version']
        
        # Load specific version
        version_dir = prompt_dir / version
        if not version_dir.exists():
            raise NotFoundError(f"Version {version} not found for prompt: {name}")
        
        # Load content
        content_file = version_dir / "content.md"
        metadata_file = version_dir / "metadata.json"
        
        if not content_file.exists() or not metadata_file.exists():
            raise NotFoundError(f"Prompt files missing for {name}@{version}")
        
        with open(content_file, 'r') as f:
            content = f.read()
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Verify checksum if enabled
        if self._enable_checksum:
            calculated_checksum = hashlib.sha256(content.encode()).hexdigest()
            if calculated_checksum != metadata.get('checksum'):
                raise IntegrityError("Checksum verification failed")
        
        prompt_content = PromptContent(
            name=name,
            version=version,
            content=content,
            metadata=metadata
        )
        
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
        risk_level: str = "medium"
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
        
        if self._mode == "filesystem":
            return await self._create_filesystem(name, content, user_id, version, category, risk_level)
        else:
            raise NotImplementedError("PostgreSQL mode not yet implemented")
    
    async def _create_filesystem(
        self,
        name: str,
        content: str,
        user_id: str,
        version: str,
        category: str,
        risk_level: str
    ) -> str:
        """Create prompt in filesystem storage."""
        import uuid
        
        prompt_dir = self._base_path / name
        version_dir = prompt_dir / version
        
        # Check if version already exists
        if version_dir.exists():
            raise ConflictError(f"Prompt {name}@{version} already exists")
        
        # Create directories
        prompt_dir.mkdir(exist_ok=True)
        version_dir.mkdir(exist_ok=True)
        
        # Calculate checksum
        checksum = hashlib.sha256(content.encode()).hexdigest()
        
        # Create metadata
        metadata = {
            'uuid': str(uuid.uuid4()),
            'name': name,
            'version': version,
            'category': category,
            'risk_level': risk_level,
            'checksum': checksum,
            'created_by': user_id,
            'created_at': asyncio.get_event_loop().time()
        }
        
        # Write files
        content_file = version_dir / "content.md"
        metadata_file = version_dir / "metadata.json"
        
        with open(content_file, 'w') as f:
            f.write(content)
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update latest version
        latest_file = prompt_dir / "latest.json"
        with open(latest_file, 'w') as f:
            json.dump({'version': version}, f, indent=2)
        
        # Log creation
        self._log_access(name, user_id, "create", version)
        
        return metadata['uuid']
    
    def _log_access(self, name: str, user_id: str, action: str, version: Optional[str] = None):
        """Log access to audit log."""
        entry = AuditEntry(
            timestamp=asyncio.get_event_loop().time(),
            user_id=user_id,
            prompt_name=name,
            version=version,
            action=action
        )
        self._audit_log.append(entry)
    
    def get_audit_log(self) -> list[AuditEntry]:
        """Get the audit log."""
        return self._audit_log.copy()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup if needed
        pass
