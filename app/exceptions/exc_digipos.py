"""Digipos Domain-Specific Exceptions.

Provides specialized exceptions for the Digipos service with appropriate
status codes and messages for common authentication and validation scenarios.
"""

from app.exceptions.exc_base import BaseExcpError


class DigiposAuthenticationError(BaseExcpError):
    """Authentication failed for Digipos request."""

    default_message = "Authentication failed"
    status_code = 401


class DigiposMemberNotFoundError(BaseExcpError):
    """Member ID not found in system."""

    default_message = "Member not found"
    status_code = 404


class DigiposInvalidSignatureError(BaseExcpError):
    """Invalid signature provided in request."""

    default_message = "Invalid signature"
    status_code = 401


class DigiposInvalidCredentialsError(BaseExcpError):
    """Invalid PIN or password provided."""

    default_message = "Invalid credentials"
    status_code = 401


class DigiposIPNotAllowedError(BaseExcpError):
    """Request from unauthorized IP address."""

    default_message = "IP address not allowed"
    status_code = 403


class DigiposForwardingError(BaseExcpError):
    """Error occurred while forwarding request to Telkomsel API."""

    default_message = "Failed to forward request to upstream API"
    status_code = 502


class DigiposResponseProcessingError(BaseExcpError):
    """Error occurred while processing API response."""

    default_message = "Failed to process API response"
    status_code = 500


class DigiposValidationError(BaseExcpError):
    """Request validation failed."""

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
