"""Integration tests for FastHX decorators.

Testing HTMX-specific error handling decorators and
HTML response functionality.
"""

import pytest
from app.exceptions import AppExceptionError, ServiceError
from app.exceptions.exc_fasthx import (
    with_config_error_handling,
    with_htmx_error_handling,
)


class MockTemplate:
    """Mock template for testing."""

    def __init__(self, content: str = "Mock template content"):
        self.content = content

    def render(self, context: dict) -> str:
        """Mock render method."""
        return self.content.format(**context) if context else self.content


class MockTemplates:
    """Mock Jinja2Templates for testing."""

    def __init__(self, template_content: str = "Mock template"):
        self.template_content = template_content

    def get_template(self, _name: str) -> MockTemplate:
        """Mock get_template method."""
        return MockTemplate(self.template_content)


class TestWithHtmxErrorHandling:
    """Test HTMX error handling decorator."""

    def setup_method(self):
        """Setup test templates."""
        self.mock_templates = MockTemplates()

    @pytest.mark.integration
    async def test_successful_execution(self):
        # Arrange
        @with_htmx_error_handling(self.mock_templates)  # type: ignore
        async def successful_endpoint():
            return {"success": True, "message": "Operation completed"}

        # Act
        result = await successful_endpoint()

        # Assert
        assert result["success"] is True
        assert result["message"] == "Operation completed"

    @pytest.mark.integration
    async def test_app_exception_handling(self):
        # Arrange
        @with_htmx_error_handling(self.mock_templates)  # type: ignore
        async def failing_endpoint():
            raise ServiceError(message="Service unavailable")

        # Act
        response = await failing_endpoint()

        # Assert
        # Should return HTML response from adapter
        assert hasattr(response, "status_code")
        assert response.status_code == 503

    @pytest.mark.integration
    async def test_generic_exception_handling(self):
        # Arrange
        @with_htmx_error_handling(self.mock_templates)  # type: ignore
        async def endpoint_with_generic_error():
            raise ValueError("Unexpected error")

        # Act
        response = await endpoint_with_generic_error()

        # Assert
        assert hasattr(response, "status_code")
        assert response.status_code == 500

    @pytest.mark.integration
    async def test_function_metadata_preserved(self):
        # Arrange
        @with_htmx_error_handling(self.mock_templates)  # type: ignore
        async def documented_endpoint():
            """This endpoint has documentation."""
            return {"data": "test"}

        # Act & Assert
        assert documented_endpoint.__doc__ == "This endpoint has documentation."
        assert documented_endpoint.__name__ == "documented_endpoint"

    @pytest.mark.integration
    async def test_error_context_preservation(self):
        # Arrange
        @with_htmx_error_handling(self.mock_templates)  # type: ignore
        async def endpoint_with_context_error():
            raise AppExceptionError(
                message="Context error",
                context={"field": "username", "value": "invalid"},
            )

        # Act
        response = await endpoint_with_context_error()

        # Assert
        assert response.status_code == 500


class TestWithConfigErrorHandling:
    """Test configuration-specific error handling decorator."""

    def setup_method(self):
        """Setup test templates."""
        self.mock_templates = MockTemplates()

    @pytest.mark.integration
    async def test_successful_config_processing(self):
        # Arrange
        @with_config_error_handling(self.mock_templates)  # type: ignore
        async def config_upload_endpoint():
            return {"success": True, "message": "Config uploaded successfully"}

        # Act
        result = await config_upload_endpoint()

        # Assert
        assert result["success"] is True
        assert result["message"] == "Config uploaded successfully"

    @pytest.mark.integration
    async def test_validation_error_handling(self):
        # Arrange
        @with_config_error_handling(self.mock_templates)  # type: ignore
        async def config_validation_endpoint():
            validation_errors = [
                {"loc": ["username"], "msg": "Username is required"},
                {"loc": ["email"], "msg": "Invalid email format"},
            ]
            raise AppExceptionError(
                message="Configuration validation failed",
                context={"validation_errors": validation_errors},
            )

        # Act
        response = await config_validation_endpoint()

        # Assert
        assert response.status_code == 500

    @pytest.mark.integration
    async def test_generic_config_error(self):
        # Arrange
        @with_config_error_handling(self.mock_templates)  # type: ignore
        async def config_error_endpoint():
            raise RuntimeError("Config processing failed")

        # Act
        response = await config_error_endpoint()

        # Assert
        assert response.status_code == 500

    @pytest.mark.integration
    async def test_app_exception_with_config_adapter(self):
        # Arrange
        @with_config_error_handling(self.mock_templates)  # type: ignore
        async def config_app_error_endpoint():
            raise AppExceptionError(
                message="Config error",
                context={"config_file": "modules.yaml"},
            )

        # Act
        response = await config_app_error_endpoint()

        # Assert
        assert response.status_code == 500

    @pytest.mark.integration
    async def test_enhanced_error_context(self):
        # Arrange
        @with_config_error_handling(self.mock_templates)  # type: ignore
        async def complex_config_error():
            raise KeyError("Missing configuration key")

        # Act
        response = await complex_config_error()

        # Assert
        assert response.status_code == 500


class TestDecoratorIntegration:
    """Test decorator integration scenarios."""

    def setup_method(self):
        """Setup test templates."""
        self.mock_templates = MockTemplates()

    @pytest.mark.integration
    async def test_decorator_with_function_arguments(self):
        # Arrange
        @with_htmx_error_handling(self.mock_templates)  # type: ignore
        async def endpoint_with_args(user_id: str, config_data: dict):
            return {"user_id": user_id, "config": config_data}

        # Act
        result = await endpoint_with_args("test_user", {"key": "value"})

        # Assert
        assert result["user_id"] == "test_user"
        assert result["config"]["key"] == "value"

    @pytest.mark.integration
    async def test_decorator_error_with_function_arguments(self):
        # Arrange
        @with_config_error_handling(self.mock_templates)  # type: ignore
        async def endpoint_with_args_and_error(config_name: str):
            raise AppExceptionError(f"Failed to process config: {config_name}")

        # Act
        response = await endpoint_with_args_and_error("test_config")

        # Assert
        assert response.status_code == 500

    @pytest.mark.integration
    async def test_multiple_decorator_scenarios(self):
        # Arrange
        test_cases = [
            (with_htmx_error_handling, "HTMX decorator"),
            (with_config_error_handling, "Config decorator"),
        ]

        for decorator_func, description in test_cases:

            @decorator_func(self.mock_templates)  # type: ignore
            async def test_endpoint():
                return {"decorator": description}

            # Act
            result = await test_endpoint()

            # Assert
            assert result["decorator"] == description

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "exception_class,expected_status",
        [
            (AppExceptionError, 500),
            (ServiceError, 503),
            (ValueError, 500),
            (RuntimeError, 500),
        ],
    )
    async def test_decorator_error_status_codes(self, exception_class, expected_status):
        # Arrange
        @with_htmx_error_handling(self.mock_templates)  # type: ignore
        async def error_endpoint():
            if exception_class == AppExceptionError:
                raise exception_class(message="Test error")
            elif exception_class == ServiceError:
                raise exception_class(message="Service error")
            else:
                raise exception_class("Generic error")

        # Act
        response = await error_endpoint()

        # Assert
        assert response.status_code == expected_status

    @pytest.mark.integration
    async def test_decorator_preserves_async_behavior(self):
        # Arrange
        import asyncio

        @with_htmx_error_handling(self.mock_templates)  # type: ignore
        async def async_endpoint():
            await asyncio.sleep(0.001)  # Minimal async operation
            return {"async": True}

        # Act
        result = await async_endpoint()

        # Assert
        assert result["async"] is True
