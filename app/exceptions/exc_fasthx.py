"""FastHX Integration for Exception Handling.

Provides specialized decorators for HTMX endpoints with exception handling.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

from app.exceptions.exc_base import AppExceptionError
from app.exceptions.exc_html_adapter import (
    ConfigErrorAdapter,
    HtmlResponseAdapter,
)
from fastapi.templating import Jinja2Templates


def with_htmx_error_handling(templates: Jinja2Templates):
    """Decorator for HTMX endpoints with HTML error handling.

    This decorator should be used with FastHX decorators for admin interface
    endpoints that need to return HTML fragments on errors.

    Usage:
        @app.post("/admin/modules/upload")
        @jinja.hx("fragments/upload_result.html")
        @with_htmx_error_handling(templates)
        async def upload_modules(config_data: str = Form(...)):
            return {"success": True, "message": "Config uploaded"}
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)

            except AppExceptionError as e:
                # Use HTML adapter for HTMX responses
                html_adapter = HtmlResponseAdapter(templates)
                return html_adapter.format_error(e)

            except Exception as e:
                # Handle unexpected errors
                html_adapter = HtmlResponseAdapter(templates)

                # Create AppExceptionError for consistent handling
                app_error = AppExceptionError(
                    message=f"Unexpected error: {e!s}",
                    context={"original_error": str(e)},
                    cause=e,
                )

                return html_adapter.format_error(app_error)

        return wrapper

    return decorator


def with_config_error_handling(templates: Jinja2Templates):
    """Specialized decorator for configuration upload endpoints.

    Provides enhanced error handling for configuration validation errors
    with detailed field-level feedback.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)

            except AppExceptionError as e:
                # Use specialized config error adapter
                config_adapter = ConfigErrorAdapter(templates)
                return config_adapter.format_error(e)

            except Exception as e:
                config_adapter = ConfigErrorAdapter(templates)

                # Enhanced error context for config errors
                app_error = AppExceptionError(
                    message="Configuration processing failed",
                    context={"error_type": e.__class__.__name__, "details": str(e)},
                    cause=e,
                )

                return config_adapter.format_error(app_error)

        return wrapper

    return decorator
