"""Factory pattern for creating appropriate processors.

Routes categories to the correct processor type:
- RECHARGE: For mobile number categories (DATA, VOICE_SMS, etc.)
- ACTIVATION: For VCR/VF categories
"""

from typing import ClassVar

from app.service.response.activation_processor import ActivationProcessor
from app.service.response.base_processor import BaseProcessor
from app.service.response.recharge_processor import RechargeProcessor


class ProcessorFactory:
    """Factory to create appropriate processor for each category."""

    # Define category mappings
    RECHARGE_CATEGORIES: ClassVar[set[str]] = {
        "DATA",
        "VOICE_SMS",
        "DIGITAL_OTHER",
        "DIGITAL_MUSIC",
        "DIGITAL_GAME",
        "ROAMING",
        "BYU",
        "HVC_DATA",
        "HVC_VOICE_SMS",
    }

    ACTIVATION_CATEGORIES: ClassVar[set[str]] = {
        "VF",
    }

    @classmethod
    def create_processor(cls, category: str) -> BaseProcessor:
        """Create processor for given category."""
        category_upper = category.upper()

        if category_upper in cls.RECHARGE_CATEGORIES:
            return RechargeProcessor(category_upper)
        elif category_upper in cls.ACTIVATION_CATEGORIES:
            return ActivationProcessor(category_upper)
        else:
            raise ValueError(
                f"Unsupported category: {category}. "
                f"Supported: {cls.RECHARGE_CATEGORIES | cls.ACTIVATION_CATEGORIES}"
            )

    @classmethod
    def get_supported_categories(cls) -> set[str]:
        """Get all supported categories."""
        return cls.RECHARGE_CATEGORIES | cls.ACTIVATION_CATEGORIES

    @classmethod
    def get_processor_type(cls, category: str) -> str:
        """Get processor type for a category."""
        category_upper = category.upper()

        if category_upper in cls.RECHARGE_CATEGORIES:
            return "RECHARGE"
        elif category_upper in cls.ACTIVATION_CATEGORIES:
            return "ACTIVATION"
        else:
            raise ValueError(f"Unsupported category: {category}")
