"""Integration tests for exception handler decorators.

Testing decorator functionality, response formatting,
and FastAPI integration scenarios.
"""

import pytest
from app.exceptions.canvas.exc_adapter import (
    JsonResponseAdapter,
    PlaintextResponseAdapter,
)
from app.exceptions.canvas.exc_base import AppExceptionError, ServiceError
from app.exceptions.canvas.exc_handler import (
    with_json_response,
    with_plaintext_response,
    with_response_adapter,
)
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError


class TestWithResponseAdapterDecorator:
    """Test response adapter decorator functionality."""

    @pytest.mark.integration
    async def test_successful_response_with_json_adapter(self):
        # Arrange
        @with_response_adapter(JsonResponseAdapter)
        async def sample_endpoint():
            return {"message": "Success", "data": [1, 2, 3]}

        # Act
        response = await sample_endpoint()

        # Assert
        assert hasattr(response, "status_code")
        assert response.status_code == 200

    @pytest.mark.integration
    async def test_successful_response_with_plaintext_adapter(self):
        # Arrange
        @with_response_adapter(PlaintextResponseAdapter)
        async def sample_endpoint():
            return "Success message"

        # Act
        response = await sample_endpoint()

        # Assert
        assert hasattr(response, "status_code")
        assert response.status_code == 200

    @pytest.mark.integration
    async def test_custom_exception_handling(self):
        # Arrange
        @with_response_adapter(JsonResponseAdapter)
        async def failing_endpoint():
            raise ServiceError(message="Service unavailable")

        # Act
        response = await failing_endpoint()

        # Assert
        assert hasattr(response, "status_code")
        assert response.status_code == 503

    @pytest.mark.integration
    async def test_request_validation_error_handling(self):
        # Arrange
        validation_error = RequestValidationError([
            {
                "loc": ["body", "username"],
                "msg": "field required",
                "type": "value_error.missing",
            },
            {
                "loc": ["body", "email"],
                "msg": "invalid email format",
                "type": "value_error.email",
            },
        ])

        @with_response_adapter(JsonResponseAdapter)
        async def endpoint_with_validation_error():
            raise validation_error

        # Act
        response = await endpoint_with_validation_error()

        # Assert
        assert hasattr(response, "status_code")
        assert response.status_code == 422

    @pytest.mark.integration
    async def test_pydantic_validation_error_handling(self):
        # Arrange
        try:

            class TestModel(BaseModel):
                name: str
                age: int

            TestModel(name="test")  # Missing required field
        except ValidationError as e:
            validation_error = e

        @with_response_adapter(PlaintextResponseAdapter)
        async def endpoint_with_pydantic_error():
            raise validation_error

        # Act
        response = await endpoint_with_pydantic_error()

        # Assert
        assert hasattr(response, "status_code")
        assert response.status_code == 422

    @pytest.mark.integration
    async def test_generic_exception_handling(self):
        # Arrange
        @with_response_adapter(JsonResponseAdapter)
        async def endpoint_with_generic_error():
            raise ValueError("Something went wrong")

        # Act
        response = await endpoint_with_generic_error()

        # Assert
        assert hasattr(response, "status_code")
        assert response.status_code == 500

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "test_data,adapter_class",
        [
            ("string response", PlaintextResponseAdapter),
            ({"json": "response"}, JsonResponseAdapter),
            (["list", "response"], JsonResponseAdapter),
            (42, PlaintextResponseAdapter),
        ],
    )
    async def test_various_success_responses(self, test_data, adapter_class):
        # Arrange
        @with_response_adapter(adapter_class)
        async def sample_endpoint():
            return test_data

        # Act
        response = await sample_endpoint()

        # Assert
        assert response.status_code == 200

    @pytest.mark.integration
    async def test_decorator_preserves_function_metadata(self):
        # Arrange
        @with_response_adapter(JsonResponseAdapter)
        async def documented_endpoint():
            """This endpoint has documentation."""
            return {"message": "success"}

        # Act & Assert
        assert documented_endpoint.__doc__ == "This endpoint has documentation."
        assert documented_endpoint.__name__ == "documented_endpoint"

    @pytest.mark.integration
    async def test_nested_exceptions(self):
        # Arrange
        original_error = ConnectionError("Database connection failed")

        @with_response_adapter(JsonResponseAdapter)
        async def endpoint_with_nested_error():
            raise AppExceptionError(
                message="Service error",
                cause=original_error,
            )

        # Act
        response = await endpoint_with_nested_error()

        # Assert
        assert response.status_code == 500


class TestConvenienceDecorators:
    """Test convenience decorator functions."""

    @pytest.mark.integration
    async def test_with_plaintext_response_decorator(self):
        # Arrange
        @with_plaintext_response
        async def plaintext_endpoint():
            return "Plain text response"

        # Act
        response = await plaintext_endpoint()

        # Assert
        assert hasattr(response, "status_code")
        assert response.status_code == 200

    @pytest.mark.integration
    async def test_with_json_response_decorator(self):
        # Arrange
        @with_json_response
        async def json_endpoint():
            return {"message": "JSON response"}

        # Act
        response = await json_endpoint()

        # Assert
        assert hasattr(response, "status_code")
        assert response.status_code == 200

    @pytest.mark.integration
    async def test_plaintext_decorator_error_handling(self):
        # Arrange
        @with_plaintext_response
        async def failing_plaintext_endpoint():
            raise AppExceptionError(message="Test error")

        # Act
        response = await failing_plaintext_endpoint()

        # Assert
        assert response.status_code == 500

    @pytest.mark.integration
    async def test_json_decorator_error_handling(self):
        # Arrange
        @with_json_response
        async def failing_json_endpoint():
            raise ServiceError(message="Service error")

        # Act
        response = await failing_json_endpoint()

        # Assert
        assert response.status_code == 503


class TestErrorScenarios:
    """Test various error scenarios and edge cases."""

    @pytest.mark.integration
    async def test_exception_without_status_code(self):
        # Arrange
        @with_response_adapter(JsonResponseAdapter)
        async def endpoint_with_basic_exception():
            raise RuntimeError("Basic runtime error")

        # Act
        response = await endpoint_with_basic_exception()

        # Assert
        assert response.status_code == 500

    @pytest.mark.integration
    async def test_exception_with_custom_status_code(self):
        # Arrange
        custom_error = ValueError("Custom error")
        custom_error.status_code = 418  # type: ignore

        @with_response_adapter(PlaintextResponseAdapter)
        async def endpoint_with_custom_status():
            raise custom_error

        # Act
        response = await endpoint_with_custom_status()

        # Assert
        assert response.status_code == 418

    @pytest.mark.integration
    async def test_empty_validation_errors(self):
        # Arrange
        validation_error = RequestValidationError([])

        @with_response_adapter(JsonResponseAdapter)
        async def endpoint_with_empty_validation_error():
            raise validation_error

        # Act
        response = await endpoint_with_empty_validation_error()

        # Assert
        assert response.status_code == 422

    @pytest.mark.integration
    async def test_complex_validation_errors(self):
        # Arrange
        validation_error = RequestValidationError([
            {
                "loc": ["body", "user", "profile", "email"],
                "msg": "invalid email format",
                "type": "value_error.email",
            },
            {
                "loc": ["query", "limit"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
            },
        ])

        @with_response_adapter(PlaintextResponseAdapter)
        async def endpoint_with_complex_validation_error():
            raise validation_error

        # Act
        response = await endpoint_with_complex_validation_error()

        # Assert
        assert response.status_code == 422

    @pytest.mark.integration
    async def test_exception_with_to_response_method(self):
        # Arrange
        @with_response_adapter(JsonResponseAdapter)
        async def endpoint_with_app_exception():
            raise AppExceptionError(
                message="Custom app error",
                context={"user_id": "123"},
            )

        # Act
        response = await endpoint_with_app_exception()

        # Assert
        assert response.status_code == 500

    @pytest.mark.integration
    async def test_function_arguments_preserved(self):
        # Arrange
        @with_response_adapter(JsonResponseAdapter)
        async def endpoint_with_args(user_id: str, limit: int = 10):
            return {"user_id": user_id, "limit": limit}

        # Act
        response = await endpoint_with_args("test_user", 20)

        # Assert
        assert response.status_code == 200
