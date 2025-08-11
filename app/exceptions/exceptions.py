"""Base exceptions for the application."""

from app.exceptions.exc_base import AppExceptionError


class ServiceError(AppExceptionError):
    """Failures in external services or APIs."""

    default_message = "Service is unavailable."
    status_code = 503


class EntityDoesNotExistError(AppExceptionError):
    """Database returns nothing."""

    default_message = "Entity does not exist."
    status_code = 404


class EntityAlreadyExistsError(AppExceptionError):
    """Conflict detected, resource already exists."""

    default_message = "Entity already exists."
    status_code = 409


class InvalidOperationError(AppExceptionError):
    """Invalid operation on resource."""

    default_message = "Invalid operation."
    status_code = 400


class AuthenticationFailedError(AppExceptionError):
    """Invalid authentication credentials."""

    default_message = "Authentication failed."
    status_code = 401


class InvalidTokenError(AppExceptionError):
    """Invalid token."""

    default_message = "Invalid token."
    status_code = 401


class MemberAuthError(AppExceptionError):
    """Authentication failed for member request."""

    default_message = "Authentication failed"
    status_code = 401


class MemberNotFoundError(MemberAuthError):
    """Member ID not found in system."""

    default_message = "Member not found"
    status_code = 404

    def __init__(self, memberid: str):
        super().__init__(f"Member ID '{memberid}' not found")


class MemberInvalidSignatureError(AppExceptionError):
    """Invalid signature provided in member request."""

    default_message = "Invalid signature"
    status_code = 401


class MemberInvalidCredentialsError(AppExceptionError):
    """Invalid PIN or password provided for member."""

    default_message = "Invalid credentials"
    status_code = 401


class MemberIPNotAllowedError(AppExceptionError):
    """Request from unauthorized IP address for member."""

    default_message = "IP address not allowed"
    status_code = 403


class MemberForwardingError(AppExceptionError):
    """Error occurred while forwarding member request to upstream API."""

    default_message = "Failed to forward request to upstream API"
    status_code = 502


class MemberResponseProcessingError(AppExceptionError):
    """Error occurred while processing member API response."""

    default_message = "Failed to process API response"
    status_code = 500
