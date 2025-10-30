"""Exception classes for UPSS."""

from typing import Optional


class UPSSError(Exception):
    """Base exception for all UPSS errors."""

    def __init__(
        self,
        message: str,
        details: Optional[dict] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause


class ConfigurationError(UPSSError):
    """Invalid configuration detected."""

    pass


class StorageError(UPSSError):
    """File or database operation failed."""

    pass


class IntegrityError(UPSSError):
    """Checksum verification failed."""

    pass


class PermissionError(UPSSError):
    """Access denied."""

    pass


class NotFoundError(UPSSError):
    """Prompt doesn't exist."""

    pass


class ConflictError(UPSSError):
    """Duplicate name/version."""

    pass


class ComplianceError(UPSSError):
    """PII or policy violation."""

    pass


class SecurityError(UPSSError):
    """Injection attempt or suspicious activity."""

    pass
