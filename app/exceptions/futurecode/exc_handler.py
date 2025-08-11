"""Response Handler Decorator.

Provides decorator for injecting response adapters into FastAPI endpoints.
Handles both success and error responses with flexible formatting.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

from app.exceptions.futurecode.exc_adapter import (
    JsonResponseAdapter,
    PlaintextResponseAdapter,
    ResponseAdapter,
)
from app.exceptions.exc_base import AppExceptionError
from fastapi.exceptions import RequestValidationError


def with_response_adapter(adapter_class: type[ResponseAdapter]):
    """Decorator to inject response adapter into endpoint.

    This decorator wraps FastAPI endpoints and automatically handles:
    - Success responses (formatted via adapter)
    - Custom application exceptions (AppExceptionError)
    - Pydantic validation errors (from request models)
    - Generic Python exceptions

    Args:
        adapter_class: The ResponseAdapter class to use for formatting

    Returns:
        Decorated function that handles responses via the adapter

    Example:
        @app.get("/digipos/trx")
        @with_response_adapter(PlaintextResponseAdapter)
        async def digipos_endpoint(request: Request, data: DigiposListRequest):
            return "Success response"  # Will be formatted as plaintext
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            adapter = adapter_class()

            try:
                # Call the original endpoint function
                result = await func(*args, **kwargs)
                return adapter.format_success(result)

            except RequestValidationError as e:
                # Handle FastAPI/Pydantic validation errors
                error_details = []
                for error in e.errors():
                    field = error.get("loc", ["unknown"])[-1]
                    message = error.get("msg", "Validation error")
                    error_details.append(f"{field}: {message}")

                error_msg = "; ".join(error_details)

                # Create a mock exception with required methods
                class ValidationError(Exception):
                    def __init__(self, msg: str, original_error: Exception):
                        self.message = msg
                        self.original_error = original_error
                        self.status_code = 422
                        super().__init__(msg)

                    def to_plaintext(self) -> str:
                        return f"Validation Error: {self.message}"

                    def __str__(self) -> str:
                        return self.message

                validation_error = ValidationError(error_msg, e)
                return adapter.format_error(validation_error)

            except ValidationError as e:
                # Handle direct Pydantic validation errors
                error_msg = "; ".join([
                    f"{err['loc'][-1]}: {err['msg']}" for err in e.errors()
                ])

                class PydanticValidationErrorWrapper(Exception):
                    def __init__(self, msg: str):
                        self.message = msg
                        self.status_code = 422
                        super().__init__(msg)

                    def to_plaintext(self) -> str:
                        return f"Validation Error: {self.message}"

                    def __str__(self) -> str:
                        return self.message

                validation_error = PydanticValidationErrorWrapper(error_msg)
                return adapter.format_error(validation_error)

            except AppExceptionError as e:
                # Handle our custom application exceptions
                return adapter.format_error(e)

            except Exception as generic_exception:
                # Handle any other unexpected exceptions
                class GenericExceptionError(Exception):
                    def __init__(self, original_error: Exception):
                        self.original_error = original_error
                        self.status_code = 500
                        self.message = str(original_error)
                        super().__init__(self.message)

                    def to_plaintext(self) -> str:
                        return f"Internal Error: {self.message}"

                    def __str__(self) -> str:
                        return self.message

                generic_error = GenericExceptionError(generic_exception)
                return adapter.format_error(generic_error)

        return wrapper

    return decorator


def with_plaintext_response(func: Callable) -> Callable:
    """Convenience decorator for plaintext responses.

    Equivalent to @with_response_adapter(PlaintextResponseAdapter)
    """
    return with_response_adapter(PlaintextResponseAdapter)(func)


def with_json_response(func: Callable) -> Callable:
    """Convenience decorator for JSON responses.

    Equivalent to @with_response_adapter(JsonResponseAdapter)
    """
    return with_response_adapter(JsonResponseAdapter)(func)
