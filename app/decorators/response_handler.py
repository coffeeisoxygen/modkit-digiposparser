"""Response Handler Decorator.

Provides decorator for injecting response adapters into FastAPI endpoints.
Handles both success and error responses with flexible formatting.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

from app.adapters.response_adapter import ResponseAdapter
from app.custom.exceptions import BaseExcpError
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError


def with_response_adapter(adapter_class: type[ResponseAdapter]):
    """Decorator to inject response adapter into endpoint.

    This decorator wraps FastAPI endpoints and automatically handles:
    - Success responses (formatted via adapter)
    - Custom application exceptions (BaseExcpError)
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
                validation_error = type(
                    "ValidationError",
                    (),
                    {
                        "to_plaintext": lambda: f"Validation Error: {error_msg}",
                        "to_response": lambda: adapter.format_error(e),
                        "status_code": 422,
                        "__str__": lambda: error_msg,
                    },
                )()

                return adapter.format_error(validation_error)

            except ValidationError as e:
                # Handle direct Pydantic validation errors
                error_msg = "; ".join([
                    f"{err['loc'][-1]}: {err['msg']}" for err in e.errors()
                ])

                validation_error = type(
                    "ValidationError",
                    (),
                    {
                        "to_plaintext": lambda: f"Validation Error: {error_msg}",
                        "status_code": 422,
                        "__str__": lambda: error_msg,
                    },
                )()

                return adapter.format_error(validation_error)

            except BaseExcpError as e:
                # Handle our custom application exceptions
                return adapter.format_error(e)

            except Exception:
                # Handle any other unexpected exceptions
                generic_error = type(
                    "GenericError",
                    (),
                    {
                        "to_plaintext": lambda: f"Internal Error: {e!s}",
                        "status_code": 500,
                        "__str__": lambda: str(e),
                    },
                )()

                return adapter.format_error(generic_error)

        return wrapper

    return decorator


def with_plaintext_response(func: Callable) -> Callable:
    """Convenience decorator for plaintext responses.

    Equivalent to @with_response_adapter(PlaintextResponseAdapter)
    """
    from app.adapters.response_adapter import PlaintextResponseAdapter

    return with_response_adapter(PlaintextResponseAdapter)(func)


def with_json_response(func: Callable) -> Callable:
    """Convenience decorator for JSON responses.

    Equivalent to @with_response_adapter(JsonResponseAdapter)
    """
    from app.adapters.response_adapter import JsonResponseAdapter

    return with_response_adapter(JsonResponseAdapter)(func)
