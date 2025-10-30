"""
Universal Prompt Security Standard (UPSS) - Python Implementation

A secure, production-ready library for managing LLM prompts following the UPSS framework.
"""

__version__ = "2.0.0"
__author__ = "UPSS Contributors"

from .core.client import UPSSClient
from .core.exceptions import (
    UPSSError,
    ConfigurationError,
    StorageError,
    IntegrityError,
    PermissionError,
    NotFoundError,
    ConflictError,
    ComplianceError,
    SecurityError,
)
from .core.models import PromptContent, AuditEntry, MigrationReport

__all__ = [
    "UPSSClient",
    "UPSSError",
    "ConfigurationError",
    "StorageError",
    "IntegrityError",
    "PermissionError",
    "NotFoundError",
    "ConflictError",
    "ComplianceError",
    "SecurityError",
    "PromptContent",
    "AuditEntry",
    "MigrationReport",
]
