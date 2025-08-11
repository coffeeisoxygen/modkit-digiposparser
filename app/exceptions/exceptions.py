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
