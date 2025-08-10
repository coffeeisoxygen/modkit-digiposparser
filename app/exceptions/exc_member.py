"""Member Domain-Specific Exceptions.

Provides specialized exceptions for member authentication, validation,
and access scenarios.
"""

from app.exceptions.exc_base import BaseExcpError


class MemberAuthError(BaseExcpError):
    """Authentication failed for member request."""

    default_message = "Authentication failed"
    status_code = 401


class MemberNotFoundError(BaseExcpError):
    """Member ID not found in system."""

    default_message = "Member not found"
    status_code = 404


class MemberInvalidSignatureError(BaseExcpError):
    """Invalid signature provided in member request."""

    default_message = "Invalid signature"
    status_code = 401


class MemberInvalidCredentialsError(BaseExcpError):
    """Invalid PIN or password provided for member."""

    default_message = "Invalid credentials"
    status_code = 401


class MemberIPNotAllowedError(BaseExcpError):
    """Request from unauthorized IP address for member."""

    default_message = "IP address not allowed"
    status_code = 403


class MemberForwardingError(BaseExcpError):
    """Error occurred while forwarding member request to upstream API."""

    default_message = "Failed to forward request to upstream API"
    status_code = 502


class MemberResponseProcessingError(BaseExcpError):
    """Error occurred while processing member API response."""

    default_message = "Failed to process API response"
    status_code = 500


class MemberValidationError(BaseExcpError):
    """Member request validation failed."""

    default_message = "Request validation failed"
    status_code = 422

    def __init__(self, field: str, message: str, **kwargs):
        """Initialize with field-specific validation error.

        Args:
            field: The field that failed validation
            message: The validation error message
            **kwargs: Additional context
        """
        full_message = f"Validation error in field '{field}': {message}"
        context = kwargs.get("context", {})
        context.update({"field": field, "validation_message": message})
        super().__init__(message=full_message, context=context, **kwargs)
