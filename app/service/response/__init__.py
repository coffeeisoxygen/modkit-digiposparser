"""Response processing module.

Provides clean API for processing different category responses.
"""

from app.service.response.main_service import (
    get_processor_type,
    get_supported_categories,
    is_category_supported,
    process_activation_response,
    process_category_response,
    process_recharge_response,
)

__all__ = [
    "get_processor_type",
    "get_supported_categories",
    "is_category_supported",
    "process_activation_response",
    "process_category_response",
    "process_recharge_response",
]

# # Usage in FastAPI endpoints:
# from app.service.response import process_category_response

# # Single entry point for all categories
# result = process_category_response("DATA", response_data)
# result = process_category_response("VF", response_data)
