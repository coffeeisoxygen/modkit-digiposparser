"""Unit tests for response adapter classes.

Testing JSON and Plaintext response adapters, format methods,
and error handling functionality.
"""

import pytest
from app.exceptions import (
    AppExceptionError,
    JsonResponseAdapter,
    PlaintextResponseAdapter,
    ResponseAdapter,
    ServiceError,
)
from fastapi.responses import JSONResponse, PlainTextResponse


class TestResponseAdapterAbstract:
    """Test ResponseAdapter abstract base class."""

    @pytest.mark.unit
    def test_cannot_instantiate_abstract_class(self):
        # Arrange, Act & Assert
        with pytest.raises(TypeError) as exc_info:
            ResponseAdapter()  # type: ignore

        assert "Can't instantiate abstract class" in str(exc_info.value)


class TestJsonResponseAdapter:
    """Test JSON response adapter functionality."""

    def setup_method(self):
        """Setup test adapter instance."""
        self.adapter = JsonResponseAdapter()

    @pytest.mark.unit
    def test_format_success_with_dict(self):
        # Arrange
        data = {"message": "Success", "data": [1, 2, 3]}

        # Act
        response = self.adapter.format_success(data)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 200

    @pytest.mark.unit
    def test_format_success_with_non_dict(self):
        # Arrange
        data = "Simple string response"

        # Act
        response = self.adapter.format_success(data)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 200

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "test_data",
        [
            {"key": "value"},
            "string",
            [1, 2, 3],
            123,
        ],
    )
    def test_format_success_content_types(self, test_data):
        # Arrange & Act
        response = self.adapter.format_success(test_data)

        # Assert
        assert isinstance(response, JSONResponse)
        assert "application/json" in str(response.media_type)

    @pytest.mark.unit
    def test_format_error_with_custom_exception(self):
        # Arrange
        error = AppExceptionError(message="Test error", context={"field": "value"})

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500

    @pytest.mark.unit
    def test_format_error_with_standard_exception(self):
        # Arrange
        error = ValueError("Standard error")
        error.status_code = 400  # type: ignore

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

    @pytest.mark.unit
    def test_format_error_without_status_code(self):
        # Arrange
        error = RuntimeError("Runtime error")

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500  # Default status code

    @pytest.mark.unit
    def test_format_error_with_to_response_method(self):
        # Arrange
        error = ServiceError(message="Service unavailable")

        # Act
        response = self.adapter.format_error(error)

        # Assert
        # Should call error's to_response method
        assert isinstance(response, JSONResponse)
        assert response.status_code == 503


class TestPlaintextResponseAdapter:
    """Test Plaintext response adapter functionality."""

    def setup_method(self):
        """Setup test adapter instance."""
        self.adapter = PlaintextResponseAdapter()

    @pytest.mark.unit
    def test_format_success_with_string(self):
        # Arrange
        data = "Success message"

        # Act
        response = self.adapter.format_success(data)

        # Assert
        assert isinstance(response, PlainTextResponse)
        assert response.status_code == 200

    @pytest.mark.unit
    def test_format_success_with_dict_containing_message(self):
        # Arrange
        data = {"message": "Operation successful", "other": "data"}

        # Act
        response = self.adapter.format_success(data)

        # Assert
        assert isinstance(response, PlainTextResponse)
        assert response.status_code == 200

    @pytest.mark.unit
    def test_format_success_with_dict_containing_data(self):
        # Arrange
        data = {"data": "Important info", "metadata": "extra"}

        # Act
        response = self.adapter.format_success(data)

        # Assert
        assert isinstance(response, PlainTextResponse)
        assert response.status_code == 200

    @pytest.mark.unit
    def test_format_success_with_complex_dict(self):
        # Arrange
        data = {
            "user_id": "123",
            "status": "active",
            "permissions": ["read", "write"],
            "metadata": {"last_login": "2024-01-01"},
        }

        # Act
        response = self.adapter.format_success(data)

        # Assert
        assert isinstance(response, PlainTextResponse)
        assert response.status_code == 200

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "test_data",
        [
            "Simple string",
            123,
            [1, 2, 3],
            {"key": "value"},
            {"message": "Special message"},
            {"data": "Important data"},
        ],
    )
    def test_format_success_various_data_types(self, test_data):
        # Arrange & Act
        response = self.adapter.format_success(test_data)

        # Assert
        assert isinstance(response, PlainTextResponse)
        assert response.status_code == 200

    @pytest.mark.unit
    def test_format_error_with_custom_exception(self):
        # Arrange
        error = AppExceptionError(message="Custom error")

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, PlainTextResponse)
        assert response.status_code == 500

    @pytest.mark.unit
    def test_format_error_with_standard_exception(self):
        # Arrange
        error = ValueError("Standard error")
        error.status_code = 422  # type: ignore

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, PlainTextResponse)
        assert response.status_code == 422

    @pytest.mark.unit
    def test_format_error_without_status_code(self):
        # Arrange
        error = KeyError("Missing key")

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, PlainTextResponse)
        assert response.status_code == 500

    @pytest.mark.unit
    def test_format_error_with_to_plaintext_method(self):
        # Arrange
        error = ServiceError(message="Service error")

        # Act
        response = self.adapter.format_error(error)

        # Assert
        assert isinstance(response, PlainTextResponse)
        assert response.status_code == 503

    @pytest.mark.unit
    def test_dict_to_plaintext_empty_dict(self):
        # Arrange
        empty_dict = {}

        # Act
        result = self.adapter._dict_to_plaintext(empty_dict)

        # Assert
        assert not result

    @pytest.mark.unit
    def test_dict_to_plaintext_with_message_key(self):
        # Arrange
        data = {"message": "Important message", "other": "ignored"}

        # Act
        result = self.adapter._dict_to_plaintext(data)

        # Assert
        assert result == "Important message"

    @pytest.mark.unit
    def test_dict_to_plaintext_with_data_key(self):
        # Arrange
        data = {"data": "Important data", "other": "ignored"}

        # Act
        result = self.adapter._dict_to_plaintext(data)

        # Assert
        assert result == "Important data"

    @pytest.mark.unit
    def test_dict_to_plaintext_key_value_format(self):
        # Arrange
        data = {"user": "john", "status": "active", "count": 5}

        # Act
        result = self.adapter._dict_to_plaintext(data)

        # Assert
        parts = result.split("; ")
        assert len(parts) == 3
        assert "user=john" in parts
        assert "status=active" in parts
        assert "count=5" in parts

    @pytest.mark.unit
    def test_dict_to_plaintext_with_complex_values(self):
        # Arrange
        data = {
            "simple": "value",
            "list_val": [1, 2, 3],
            "dict_val": {"nested": "data"},
        }

        # Act
        result = self.adapter._dict_to_plaintext(data)

        # Assert
        assert "simple=value" in result
        assert "[1, 2, 3]" in result
        assert "{'nested': 'data'}" in result
