"""Unit tests for HTML response adapters.

Testing HTML fragment generation for HTMX integration,
error formatting, and template rendering.
"""

import pytest
from app.exceptions import (
    AppExceptionError,
    ConfigErrorAdapter,
    HtmlResponseAdapter,
    ServiceError,
)
from fastapi.responses import HTMLResponse


class MockTemplate:
    """Mock template for testing."""

    def __init__(self, content: str):
        self.content = content

    def render(self, context: dict) -> str:
        """Mock render method."""
        return self.content.format(**context)


class MockTemplates:
    """Mock Jinja2Templates for testing."""

    def __init__(self, template_content: str = "Mock template"):
        self.template_content = template_content

    def get_template(self, _name: str) -> MockTemplate:
        """Mock get_template method."""
        return MockTemplate(self.template_content)


class TestHtmlResponseAdapter:
    """Test HTML response adapter functionality."""

    def setup_method(self):
        """Setup test adapter instance."""
        self.mock_templates = MockTemplates()
        self.adapter = HtmlResponseAdapter(self.mock_templates)  # type: ignore

    @pytest.mark.unit
    def test_initialization(self):
        # Arrange
        templates = MockTemplates()

        # Act
        adapter = HtmlResponseAdapter(templates)  # type: ignore

        # Assert
        assert adapter.templates == templates

    @pytest.mark.unit
    def test_format_success_with_template_data(self):
        # Arrange
        data = {
            "template": "success.html",
            "context": {"message": "Success"},
        }

        # Act
        response = self.adapter.format_success(data)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 200

    @pytest.mark.unit
    def test_format_success_with_simple_data(self):
        # Arrange
        data = "Simple success message"

        # Act
        response = self.adapter.format_success(data)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 200

    @pytest.mark.unit
    def test_format_success_with_dict_message(self):
        # Arrange
        data = {"message": "Operation completed"}

        # Act
        response = self.adapter.format_success(data)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 200

    @pytest.mark.unit
    def test_format_error_with_custom_exception(self):
        # Arrange
        error = AppExceptionError(
            message="Test error",
            context={"field": "username"},
        )

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 500

    @pytest.mark.unit
    def test_format_error_with_standard_exception(self):
        # Arrange
        error = ValueError("Standard error")
        error.status_code = 400  # type: ignore

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 400

    @pytest.mark.unit
    def test_format_error_without_status_code(self):
        # Arrange
        error = RuntimeError("Runtime error")

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 500

    @pytest.mark.unit
    def test_render_success_fragment_with_string(self):
        # Arrange
        data = "Success message"

        # Act
        result = self.adapter._render_success_fragment(data)

        # Assert
        assert "alert alert-success" in result
        assert "Success message" in result
        assert "icon-success" in result

    @pytest.mark.unit
    def test_render_success_fragment_with_dict_message(self):
        # Arrange
        data = {"message": "Custom success"}

        # Act
        result = self.adapter._render_success_fragment(data)

        # Assert
        assert "alert alert-success" in result
        assert "Custom success" in result

    @pytest.mark.unit
    def test_render_success_fragment_with_other_data(self):
        # Arrange
        data = {"other": "data"}

        # Act
        result = self.adapter._render_success_fragment(data)

        # Assert
        assert "alert alert-success" in result
        assert "Operation completed successfully" in result

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "status_code,expected_class,expected_icon",
        [
            (500, "alert-danger", "⚠️"),
            (404, "alert-warning", "❌"),
            (422, "alert-warning", "❌"),
            (200, "alert-info", "🔵"),
            (301, "alert-info", "🔵"),
        ],
    )
    def test_render_error_fragment_styling(
        self, status_code, expected_class, expected_icon
    ):
        # Arrange
        error = RuntimeError("Test error")
        error.status_code = status_code  # type: ignore

        # Act
        result = self.adapter._render_error_fragment(error)

        # Assert
        assert expected_class in result
        assert expected_icon in result
        assert "Test error" in result
        assert f"Status Code: {status_code}" in result

    @pytest.mark.unit
    def test_render_error_fragment_structure(self):
        # Arrange
        error = ValueError("Validation failed")
        error.status_code = 422  # type: ignore

        # Act
        result = self.adapter._render_error_fragment(error)

        # Assert
        assert "alert-header" in result
        assert "alert-body" in result
        assert "alert-footer" in result
        assert "ValueError" in result
        assert "Validation failed" in result

    @pytest.mark.unit
    def test_format_error_calls_to_html_when_available(self):
        # Arrange
        error = ServiceError(message="Service error")

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 503


class TestConfigErrorAdapter:
    """Test configuration-specific error adapter."""

    def setup_method(self):
        """Setup test adapter instance."""
        self.mock_templates = MockTemplates()
        self.adapter = ConfigErrorAdapter(self.mock_templates)  # type: ignore

    @pytest.mark.unit
    def test_inheritance(self):
        # Arrange & Act & Assert
        assert isinstance(self.adapter, HtmlResponseAdapter)

    @pytest.mark.unit
    def test_format_error_with_validation_errors(self):
        # Arrange
        validation_errors = [
            {"loc": ["field1"], "msg": "Field is required"},
            {"loc": ["field2", "nested"], "msg": "Invalid format"},
        ]
        error = AppExceptionError(
            message="Config validation failed",
            context={"validation_errors": validation_errors},
        )

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 500

    @pytest.mark.unit
    def test_format_error_without_validation_errors(self):
        # Arrange
        error = AppExceptionError(message="Simple config error")

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.status_code == 500

    @pytest.mark.unit
    def test_render_validation_errors_with_dict_errors(self):
        # Arrange
        validation_errors = [
            {"loc": ["username"], "msg": "Username is required"},
            {"loc": ["email", "format"], "msg": "Invalid email format"},
        ]
        error = AppExceptionError(
            message="Validation failed",
            context={"validation_errors": validation_errors},
        )

        # Act
        result = self.adapter._render_validation_errors(error)

        # Assert
        assert "Configuration Validation Failed" in result
        assert "username" in result
        assert "Username is required" in result
        assert "format" in result  # nested field
        assert "Invalid email format" in result
        assert "validation-errors" in result

    @pytest.mark.unit
    def test_render_validation_errors_with_string_errors(self):
        # Arrange
        validation_errors = ["Error 1", "Error 2"]
        error = AppExceptionError(
            message="Validation failed",
            context={"validation_errors": validation_errors},
        )

        # Act
        result = self.adapter._render_validation_errors(error)

        # Assert
        assert "Configuration Validation Failed" in result
        assert "Error 1" in result
        assert "Error 2" in result

    @pytest.mark.unit
    def test_render_validation_errors_empty_list(self):
        # Arrange
        error = AppExceptionError(
            message="Validation failed",
            context={"validation_errors": []},
        )

        # Act
        result = self.adapter._render_validation_errors(error)

        # Assert
        assert "Configuration Validation Failed" in result
        assert "validation-errors" in result

    @pytest.mark.unit
    def test_render_validation_errors_structure(self):
        # Arrange
        validation_errors = [{"loc": ["field"], "msg": "Error message"}]
        error = AppExceptionError(
            message="Test",
            context={"validation_errors": validation_errors},
        )

        # Act
        result = self.adapter._render_validation_errors(error)

        # Assert
        assert "alert alert-danger" in result
        assert "alert-header" in result
        assert "alert-body" in result
        assert "alert-footer" in result
        assert "❌" in result
        assert "Please fix the errors above" in result
