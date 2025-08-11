"""HTML Response Adapter for HTMX Integration.

Extends the response adapter pattern to support HTML fragments
for HTMX admin interface error handling.
"""

from typing import Any

from app.exceptions.futurecode.exc_adapter import ResponseAdapter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


class HtmlResponseAdapter(ResponseAdapter):
    """HTML response adapter for HTMX admin interface."""

    def __init__(self, templates: Jinja2Templates):
        self.templates = templates

    def format_success(self, data: Any) -> HTMLResponse:
        """Format success data as HTML fragment."""
        if isinstance(data, dict) and "template" in data:
            # If data specifies template to use
            template_name = data["template"]
            context = data.get("context", {})
            html_content = self.templates.get_template(template_name).render(context)
        else:
            # Default success fragment
            html_content = self._render_success_fragment(data)

        return HTMLResponse(content=html_content)

    def format_error(self, error: Exception) -> HTMLResponse:
        """Format error as HTML fragment for HTMX."""
        # Get user-friendly error message
        if hasattr(error, "to_html"):
            html_content = error.to_html()  # type: ignore
        else:
            html_content = self._render_error_fragment(error)

        status_code = getattr(error, "status_code", 500)
        return HTMLResponse(content=html_content, status_code=status_code)

    def _render_success_fragment(self, data: Any) -> str:
        """Render success message as HTML fragment."""
        if isinstance(data, str):
            message = data
        elif isinstance(data, dict) and "message" in data:
            message = data["message"]
        else:
            message = "Operation completed successfully"

        return f"""
        <div class="alert alert-success" role="alert">
            <svg class="icon icon-success" width="16" height="16" viewBox="0 0 16 16">
                <path d="M13.854 3.646a.5.5 0 0 1 0 .708L6.5 11.207l-3.354-3.353a.5.5 0 1 1 .708-.708L6.5 9.793l6.646-6.647a.5.5 0 0 1 .708 0z"/>
            </svg>
            {message}
        </div>
        """

    def _render_error_fragment(self, error: Exception) -> str:
        """Render error as HTML fragment."""
        error_type = error.__class__.__name__
        message = str(error)
        status_code = getattr(error, "status_code", 500)

        # Different styling based on error type
        if status_code >= 500:
            alert_class = "alert-danger"
            icon = "⚠️"
        elif status_code >= 400:
            alert_class = "alert-warning"
            icon = "❌"
        else:
            alert_class = "alert-info"
            icon = "🔵"

        return f"""
        <div class="alert {alert_class}" role="alert">
            <div class="alert-header">
                <span class="alert-icon">{icon}</span>
                <strong>{error_type}</strong>
            </div>
            <div class="alert-body">
                {message}
            </div>
            <div class="alert-footer text-muted">
                <small>Status Code: {status_code}</small>
            </div>
        </div>
        """


class ConfigErrorAdapter(HtmlResponseAdapter):
    """Specialized HTML adapter for configuration errors."""

    def format_error(self, error: Exception) -> HTMLResponse:
        """Format configuration-specific errors with more detail."""
        if hasattr(error, "context") and "validation_errors" in error.context:  # type: ignore
            return self._render_validation_errors(error)  # type: ignore

        return super().format_error(error)

    def _render_validation_errors(self, error: Exception) -> str:
        """Render validation errors for configuration uploads."""
        validation_errors = error.context.get("validation_errors", [])  # type: ignore

        error_items = []
        for err in validation_errors:
            field = (
                err.get("loc", ["unknown"])[-1] if isinstance(err, dict) else str(err)
            )
            message = err.get("msg", str(err)) if isinstance(err, dict) else str(err)
            error_items.append(f"<li><strong>{field}:</strong> {message}</li>")

        errors_html = "".join(error_items)

        return f"""
        <div class="alert alert-danger" role="alert">
            <div class="alert-header">
                <span class="alert-icon">❌</span>
                <strong>Configuration Validation Failed</strong>
            </div>
            <div class="alert-body">
                <p>The uploaded configuration contains the following errors:</p>
                <ul class="validation-errors">
                    {errors_html}
                </ul>
            </div>
            <div class="alert-footer">
                <small>Please fix the errors above and try again.</small>
            </div>
        </div>
        """
