"""Normalized OSF SDK exceptions."""

from __future__ import annotations


class OSFError(Exception):
    """Base class for OSF package errors."""


class OSFConfigError(OSFError):
    """Raised when auth or config resolution fails."""


class OSFTransportError(OSFError):
    """Raised when an HTTP request cannot complete successfully."""

    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class OSFAuthError(OSFTransportError):
    """Raised for authentication and authorization errors."""


class OSFNotFoundError(OSFTransportError):
    """Raised when an OSF resource does not exist or is inaccessible."""


class OSFRateLimitError(OSFTransportError):
    """Raised when OSF rate limits a request."""


class OSFValidationError(OSFTransportError):
    """Raised when OSF rejects a malformed or conflicting request."""


class OSFClientError(OSFTransportError):
    """Backward-compatible alias for legacy callers."""
