"""Response Adapter Pattern Implementation.

Provides flexible response formatting for different client requirements:
- JSON responses for standard FastAPI clients
- Plaintext responses for Otomax integration
"""

from abc import ABC, abstractmethod
from typing import Any

from fastapi.responses import JSONResponse, PlainTextResponse


class ResponseAdapter(ABC):
    """Abstract base class for response formatting adapters.

    Implements the Adapter pattern to allow flexible response formatting
    without changing the core business logic.
    """

    @abstractmethod
    def format_success(self, data: Any) -> Any:
        """Format successful response data.

        Args:
            data: The response data to format

        Returns:
            Formatted response appropriate for the client
        """
        pass

    @abstractmethod
    def format_error(self, error: Exception) -> Any:
        """Format error response.

        Args:
            error: The exception to format

        Returns:
            Formatted error response appropriate for the client
        """
        pass


class JsonResponseAdapter(ResponseAdapter):
    """JSON response adapter for standard FastAPI clients."""

    def format_success(self, data: Any) -> JSONResponse:
        """Format success data as JSON response."""
        if isinstance(data, dict):
            return JSONResponse(content=data)
        return JSONResponse(content={"data": data})

    def format_error(self, error: Exception) -> JSONResponse:
        """Format error as JSON response."""
        # Check if it's our custom exception with JSON support
        if hasattr(error, "to_response"):
            return error.to_response()  # type: ignore

        # Handle status code
        status_code = getattr(error, "status_code", 500)

        # Create JSON error response
        return JSONResponse(
            content={
                "error": error.__class__.__name__,
                "message": str(error),
                "status_code": status_code,
            },
            status_code=status_code,
        )


class PlaintextResponseAdapter(ResponseAdapter):
    """Plaintext response adapter for Otomax integration."""

    def format_success(self, data: Any) -> PlainTextResponse:
        """Format success data as plaintext response."""
        if isinstance(data, str):
            content = data
        elif isinstance(data, dict):
            # Convert dict to readable plaintext
            content = self._dict_to_plaintext(data)
        else:
            content = str(data)

        return PlainTextResponse(content=content)

    def format_error(self, error: Exception) -> PlainTextResponse:
        """Format error as plaintext response."""
        # Check if it's our custom exception with plaintext support
        if hasattr(error, "to_plaintext"):
            content = error.to_plaintext()  # type: ignore
        else:
            content = f"Error: {error!s}"

        status_code = getattr(error, "status_code", 500)
        return PlainTextResponse(content=content, status_code=status_code)

    def _dict_to_plaintext(self, data: dict) -> str:
        """Convert dictionary to readable plaintext format.

        This method handles the conversion of structured data
        to plaintext format suitable for Otomax consumption.
        """
        if not data:
            return ""

        # Handle common response patterns
        if "message" in data:
            return data["message"]

        if "data" in data:
            return str(data["data"])

        # Convert dict to key=value format
        parts = []
        for key, value in data.items():
            if isinstance(value, dict | list):
                value = str(value)
            parts.append(f"{key}={value}")

        return "; ".join(parts)
