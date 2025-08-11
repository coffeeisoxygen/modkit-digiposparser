"""Base exceptions for the application."""

from typing import TYPE_CHECKING

from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from app.exceptions.canvas.exc_adapter import ResponseAdapter

APP_NAME = "MODKIT-SERVICE"


class BaseExcpError(Exception):
    """Base exception for our application."""

    default_message: str = "An application error occurred."
    status_code: int = 500

    def __init__(
        self,
        message: str | None = None,
        name: str | None = APP_NAME,
        context: dict | None = None,
    ):
        self.message = message or self.default_message
        self.name = name
        self.context = context or {}
        super().__init__(f"[{self.status_code}] {self.message}")

    def to_dict(self):
        return {
            "error": self.name,
            "message": self.message,
            "status_code": self.status_code,
            "context": self.context,
        }

    def to_response(self):
        return JSONResponse(
            status_code=self.status_code,
            content=self.to_dict(),
        )

    def to_plaintext(self) -> str:
        return f"[{self.status_code}] {self.message}"

    def adapt_to(self, adapter: "ResponseAdapter"):
        """Adapter pattern - let adapter decide response format.

        Args:
            adapter: The response adapter to use for formatting

        Returns:
            Formatted response according to adapter implementation
        """
        return adapter.format_error(self)
