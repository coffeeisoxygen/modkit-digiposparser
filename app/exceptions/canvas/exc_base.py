"""Base exceptions for the application."""

from typing import TYPE_CHECKING

from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from app.exceptions.futurecode.exc_adapter import ResponseAdapter

APP_NAME = "MODKIT-SERVICE"


class AppExceptionError(Exception):
    """Base application exception with adapter support."""

    default_message: str = "An application error occurred."
    status_code: int = 500

    def __init__(
        self,
        message: str | None = None,
        name: str = APP_NAME,
        context: dict | None = None,
        cause: Exception | None = None,  # simpan original exception
    ):
        self.message = message or self.default_message
        self.name = name
        self.context = context or {}
        self.__cause__ = cause  # built-in Python cause chaining
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "error": self.name,
            "message": self.message,
            "status_code": self.status_code,
            "context": self.context,
        }

    def to_response(self) -> JSONResponse:
        """Return JSON response."""
        return JSONResponse(
            status_code=self.status_code,
            content=self.to_dict(),
        )

    def to_plaintext(self) -> str:
        """Return plain text version of the error."""
        return f"[{self.status_code}] {self.message}"

    def to_html(self) -> str:
        """Return HTML fragment for HTMX responses."""
        alert_class = "alert-danger" if self.status_code >= 500 else "alert-warning"
        icon = "⚠️" if self.status_code >= 500 else "❌"

        context_info = ""
        if self.context:
            context_items = []
            for key, value in self.context.items():
                context_items.append(f"<li><strong>{key}:</strong> {value}</li>")
            if context_items:
                context_info = f"""
                <div class="error-context mt-2">
                    <small class="text-muted">Context:</small>
                    <ul class="small">{"".join(context_items)}</ul>
                </div>
                """

        return f"""
        <div class="alert {alert_class}" role="alert">
            <div class="d-flex align-items-center">
                <span class="me-2">{icon}</span>
                <div>
                    <div class="fw-bold">{self.__class__.__name__}</div>
                    <div>{self.message}</div>
                    {context_info}
                </div>
            </div>
        </div>
        """

    def adapt_to(self, adapter: "ResponseAdapter"):
        """Let adapter decide response format."""
        return adapter.format_error(self)


# ======================
# Specific exception types
# ======================


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
