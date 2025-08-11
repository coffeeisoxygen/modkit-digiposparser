"""Unit tests for base exception classes.

Testing base exception functionality, custom exception types,
and response formatting methods.
"""

import pytest
from app.exceptions import (
    APP_NAME,
    AppExceptionError,
    AuthenticationFailedError,
    EntityAlreadyExistsError,
    EntityDoesNotExistError,
    InvalidOperationError,
    InvalidTokenError,
    ServiceError,
)
from fastapi.responses import JSONResponse


class TestAppExceptionError:
    """Test base AppExceptionError class."""

    @pytest.mark.unit
    def test_default_initialization(self):
        # Arrange & Act
        error = AppExceptionError()

        # Assert
        assert error.message == "An application error occurred."
        assert error.name == APP_NAME
        assert error.context == {}
        assert error.status_code == 500
        assert error.__cause__ is None

    @pytest.mark.unit
    def test_custom_initialization(self):
        # Arrange
        custom_message = "Custom error message"
        custom_name = "CUSTOM-SERVICE"
        custom_context = {"user_id": "123", "operation": "update"}
        original_error = ValueError("Original error")

        # Act
        error = AppExceptionError(
            message=custom_message,
            name=custom_name,
            context=custom_context,
            cause=original_error,
        )

        # Assert
        assert error.message == custom_message
        assert error.name == custom_name
        assert error.context == custom_context
        assert error.__cause__ == original_error

    @pytest.mark.unit
    def test_to_dict_method(self):
        # Arrange
        error = AppExceptionError(
            message="Test error",
            name="TEST-SERVICE",
            context={"key": "value"},
        )

        # Act
        result = error.to_dict()

        # Assert
        expected = {
            "error": "TEST-SERVICE",
            "message": "Test error",
            "status_code": 500,
            "context": {"key": "value"},
        }
        assert result == expected

    @pytest.mark.unit
    def test_to_response_method(self):
        # Arrange
        error = AppExceptionError(message="Test error")

        # Act
        response = error.to_response()

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert "Test error" in str(response.body)

    @pytest.mark.unit
    def test_to_plaintext_method(self):
        # Arrange
        error = AppExceptionError(message="Test error")

        # Act
        result = error.to_plaintext()

        # Assert
        assert result == "[500] Test error"

    @pytest.mark.unit
    def test_to_html_method(self):
        # Arrange
        error = AppExceptionError(
            message="Test error",
            context={"field": "username", "value": "invalid"},
        )

        # Act
        result = error.to_html()

        # Assert
        assert "alert alert-danger" in result
        assert "Test error" in result
        assert "AppExceptionError" in result
        assert "field" in result
        assert "username" in result
        assert "⚠️" in result  # Server error icon

    @pytest.mark.unit
    def test_to_html_method_without_context(self):
        # Arrange
        error = AppExceptionError(message="Simple error")

        # Act
        result = error.to_html()

        # Assert
        assert "alert alert-danger" in result
        assert "Simple error" in result
        assert "error-context" not in result

    @pytest.mark.unit
    def test_adapt_to_method(self):
        # Arrange
        error = AppExceptionError(message="Test error")

        class MockAdapter:
            def format_error(self, e):
                return f"Adapted: {e.message}"

        mock_adapter = MockAdapter()

        # Act
        result = error.adapt_to(mock_adapter)  # type: ignore

        # Assert
        assert result == "Adapted: Test error"


class TestSpecificExceptionTypes:
    """Test specific exception type behaviors."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "exception_class,expected_status,expected_message",
        [
            (ServiceError, 503, "Service is unavailable."),
            (EntityDoesNotExistError, 404, "Entity does not exist."),
            (EntityAlreadyExistsError, 409, "Entity already exists."),
            (InvalidOperationError, 400, "Invalid operation."),
            (AuthenticationFailedError, 401, "Authentication failed."),
            (InvalidTokenError, 401, "Invalid token."),
        ],
    )
    def test_specific_exception_defaults(
        self, exception_class, expected_status, expected_message
    ):
        # Arrange & Act
        error = exception_class()

        # Assert
        assert error.status_code == expected_status
        assert error.message == expected_message
        assert isinstance(error, AppExceptionError)

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "exception_class,expected_status",
        [
            (ServiceError, 503),
            (EntityDoesNotExistError, 404),
            (EntityAlreadyExistsError, 409),
            (InvalidOperationError, 400),
            (AuthenticationFailedError, 401),
            (InvalidTokenError, 401),
        ],
    )
    def test_specific_exception_custom_message(self, exception_class, expected_status):
        # Arrange
        custom_message = "Custom error message"

        # Act
        error = exception_class(message=custom_message)

        # Assert
        assert error.message == custom_message
        assert error.status_code == expected_status

    @pytest.mark.unit
    def test_client_error_html_styling(self):
        # Arrange
        error = InvalidOperationError(message="Client error")

        # Act
        result = error.to_html()

        # Assert
        assert "alert-warning" in result  # Client errors use warning style
        assert "❌" in result  # Client error icon

    @pytest.mark.unit
    def test_server_error_html_styling(self):
        # Arrange
        error = ServiceError(message="Server error")

        # Act
        result = error.to_html()

        # Assert
        assert "alert-danger" in result  # Server errors use danger style
        assert "⚠️" in result  # Server error icon

    @pytest.mark.unit
    def test_exception_with_context_in_response(self):
        # Arrange
        error = EntityDoesNotExistError(
            message="User not found",
            context={"user_id": "123", "search_field": "email"},
        )

        # Act
        response_dict = error.to_dict()
        plaintext = error.to_plaintext()

        # Assert
        assert response_dict["context"]["user_id"] == "123"
        assert response_dict["context"]["search_field"] == "email"
        assert plaintext == "[404] User not found"

    @pytest.mark.unit
    def test_exception_chaining_with_cause(self):
        # Arrange
        original_error = ValueError("Database connection failed")
        service_error = ServiceError(
            message="Unable to fetch data",
            cause=original_error,
        )

        # Act & Assert
        assert service_error.__cause__ == original_error
        assert str(service_error) == "Unable to fetch data"
