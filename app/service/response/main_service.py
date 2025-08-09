"""Main service entry point for response processing.

Clean API for FastAPI integration.
"""

from app.mlogg.log_utils import timeit
from app.service.response.processor_factory import ProcessorFactory


@timeit
def process_category_response(category: str, response_data: str) -> str:
    """Main entry point for processing category responses.

    Args:
        category: Category type (DATA, VOICE_SMS, VF, etc.)
        response_data: Raw JSON response string

    Returns:
        Processed response string

    Raises:
        ValueError: If category is not supported
    """
    processor = ProcessorFactory.create_processor(category)
    return processor.process_response(response_data)


def get_supported_categories() -> set[str]:
    """Get all supported categories."""
    return ProcessorFactory.get_supported_categories()


def get_processor_type(category: str) -> str:
    """Get processor type for a category."""
    return ProcessorFactory.get_processor_type(category)


def is_category_supported(category: str) -> bool:
    """Check if category is supported."""
    try:
        ProcessorFactory.get_processor_type(category)
        return True
    except ValueError:
        return False


# For backward compatibility and testing
def process_recharge_response(category: str, response_data: str) -> str:
    """Process recharge category response (backward compatibility)."""
    if ProcessorFactory.get_processor_type(category) != "RECHARGE":
        raise ValueError(f"Category {category} is not a recharge category")

    return process_category_response(category, response_data)


def process_activation_response(category: str, response_data: str) -> str:
    """Process activation category response (VF)."""
    if ProcessorFactory.get_processor_type(category) != "ACTIVATION":
        raise ValueError(f"Category {category} is not an activation category")

    return process_category_response(category, response_data)
