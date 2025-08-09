"""Base processor for all response processing.

Contains the core processing pipeline and abstract methods
that must be implemented by specific processor types.
"""

import json
import re
from abc import ABC, abstractmethod
from typing import Any

from app.mlogg.log_utils import logger, timeit

# Character limit constant
MAX_CHAR_LIMIT = 7000


class BaseProcessor(ABC):
    """Abstract base class for all response processors."""

    def __init__(self, category: str, processor_type: str):
        self.category = category
        self.processor_type = processor_type
        self.logger = logger.bind(category=category, processor_type=processor_type)

    @abstractmethod
    def get_exclude_subcategories(self) -> list[str]:
        """Return list of subcategories to exclude for this processor."""
        pass

    @abstractmethod
    def get_exclude_productnames(self) -> list[str]:
        """Return list of product name patterns to exclude."""
        pass

    @abstractmethod
    def get_exclude_quota_metadata(self) -> list[str]:
        """Return list of quota metadata patterns to exclude."""
        pass

    @abstractmethod
    def optimize_quota(self, quota: str) -> str:
        """Apply processor-specific quota optimization."""
        pass

    @abstractmethod
    def format_product_output(self, product: dict[str, Any]) -> str:
        """Format individual product for output."""
        pass

    @timeit
    def process_response(self, response_data: str) -> str:
        """Main processing pipeline - same for all processor types."""
        # 1. Check character limit first
        char_count = len(response_data)
        self.logger.info(f"Response character count: {char_count}")

        data = json.loads(response_data)

        # 2. Always apply filtering (to clean irrelevant data)
        self.logger.info("Applying filters to clean data...")

        # Filter by subcategory
        filtered_data = self._filter_by_subcategory(data)

        # Filter by product name patterns
        filtered_data = self._filter_by_productname(filtered_data)

        # Filter by quota metadata patterns
        filtered_data = self._filter_by_quota_metadata(filtered_data)

        # 3. Apply text optimization only if needed
        if char_count <= MAX_CHAR_LIMIT:
            self.logger.info("Response within limit, skipping text optimization")
            final_data = filtered_data
        else:
            self.logger.info("Response exceeds limit, applying text optimization")
            final_data = self._optimize_quotas(filtered_data)

        # Final character check
        final_output = self._format_output(final_data)
        final_char_count = len(final_output)
        self.logger.info(f"Final output character count: {final_char_count}")

        return final_output

    def _filter_by_subcategory(self, data: dict[str, Any]) -> dict[str, Any]:
        """Filter products by excluded subcategories."""
        exclude_list = self.get_exclude_subcategories()
        if not exclude_list or not any(
            exclude_list
        ):  # Skip if empty or all empty strings
            return data

        original_count = len(data.get("paket", []))
        filtered_paket = []

        for product in data.get("paket", []):
            subcategory = product.get("productSubCategory", "")
            if subcategory not in exclude_list:
                filtered_paket.append(product)

        data["paket"] = filtered_paket
        self.logger.info(
            f"Subcategory filter: {original_count} → {len(filtered_paket)} products"
        )
        return data

    def _filter_by_productname(self, data: dict[str, Any]) -> dict[str, Any]:
        """Filter products by excluded product name patterns."""
        exclude_patterns = self.get_exclude_productnames()
        if not exclude_patterns or not any(
            exclude_patterns
        ):  # Skip if empty or all empty strings
            return data

        original_count = len(data.get("paket", []))
        filtered_paket = []

        for product in data.get("paket", []):
            product_name = product.get("productName", "")
            should_exclude = any(
                re.match(rf"^{re.escape(pattern)}", product_name, re.IGNORECASE)
                for pattern in exclude_patterns
                if pattern.strip()
            )

            if not should_exclude:
                filtered_paket.append(product)

        data["paket"] = filtered_paket
        self.logger.info(
            f"Product name filter: {original_count} → {len(filtered_paket)} products"
        )
        return data

    def _filter_by_quota_metadata(self, data: dict[str, Any]) -> dict[str, Any]:
        """Filter products by excluded quota metadata patterns."""
        exclude_patterns = self.get_exclude_quota_metadata()
        if not exclude_patterns or not any(
            exclude_patterns
        ):  # Skip if empty or all empty strings
            return data

        original_count = len(data.get("paket", []))
        filtered_paket = []

        for product in data.get("paket", []):
            quota = product.get("quota", "")
            should_exclude = any(
                pattern in quota for pattern in exclude_patterns if pattern.strip()
            )

            if not should_exclude:
                filtered_paket.append(product)

        data["paket"] = filtered_paket
        self.logger.info(
            f"Quota metadata filter: {original_count} → {len(filtered_paket)} products"
        )
        return data

    def _optimize_quotas(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply quota optimization to all products."""
        for product in data.get("paket", []):
            original_quota = product.get("quota", "")
            optimized_quota = self.optimize_quota(original_quota)
            product["quota"] = optimized_quota

        self.logger.info(f"Optimized quotas for {len(data.get('paket', []))} products")
        return data

    def _format_output(self, data: dict[str, Any]) -> str:
        """Format final output using processor-specific formatting."""
        output_parts = []

        for product in data.get("paket", []):
            formatted = self.format_product_output(product)
            output_parts.append(formatted)

        return "".join(output_parts)
