"""Version 3: Factory pattern approach for multiple category processing.

Core principles:
1. Always check character limit <= 7000
2. Apply filtering based on processor type (RECHARGE vs ACTIVATION)
3. Two main processor types:
   - RECHARGE: For mobile numbers (DATA/VOICE_SMS/DIGITAL_*/ROAMING/BYU/HVC_*)
   - ACTIVATION: For VCR/VF (VF category)
4. Standardized output format: #id|name(quota)|total#
"""

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from app.mlogg.log_utils import logger, timeit

# Sample data path
SAMPLEDATA = (
    Path(__file__).resolve().parent / "example_final_VF.json"
)

# Character limit constant
MAX_CHAR_LIMIT = 7000


class CategoryProcessor(ABC):
    """Abstract base class for category-specific processing."""

    def __init__(self, category: str):
        self.category = category
        self.logger = logger.bind(category=category)

    @abstractmethod
    def get_exclude_subcategories(self) -> list[str]:
        """Return list of subcategories to exclude for this category."""
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
        """Category-specific quota optimization."""
        pass

    @timeit
    def process_response(self, response_data: str) -> str:
        """Main processing pipeline."""
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

    def _filter_by_subcategory(self, data: dict) -> dict:
        """Filter products by excluded subcategories."""
        exclude_list = self.get_exclude_subcategories()
        if not exclude_list:
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

    def _filter_by_productname(self, data: dict) -> dict:
        """Filter products by excluded product name patterns."""
        exclude_patterns = self.get_exclude_productnames()
        if not exclude_patterns:
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

    def _filter_by_quota_metadata(self, data: dict) -> dict:
        """Filter products by excluded quota metadata patterns."""
        exclude_patterns = self.get_exclude_quota_metadata()
        if not exclude_patterns:
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

    def _optimize_quotas(self, data: dict) -> dict:
        """Apply quota optimization to all products."""
        for product in data.get("paket", []):
            original_quota = product.get("quota", "")
            optimized_quota = self.optimize_quota(original_quota)
            product["quota"] = optimized_quota

        self.logger.info(f"Optimized quotas for {len(data.get('paket', []))} products")
        return data

    def _format_output(self, data: dict) -> str:
        """Format final output in standard format."""
        output_parts = []

        for product in data.get("paket", []):
            product_id = product.get("productId", "")
            product_name = product.get("productName", "")
            quota = product.get("quota", "")
            total = product.get("total_", "")

            # Format: #id|name(quota)|total
            formatted = f"#{product_id}|{product_name}({quota})|{total}"
            output_parts.append(formatted)

        return "".join(output_parts)


class DataCategoryProcessor(CategoryProcessor):
    """Processor for DATA category."""

    def get_exclude_subcategories(self) -> list[str]:
        """Subcategories to exclude for DATA category."""
        return [""]

    def get_exclude_productnames(self) -> list[str]:
        """Product name patterns to exclude for DATA category."""
        return [""]

    def get_exclude_quota_metadata(self) -> list[str]:
        """Quota metadata patterns to exclude for DATA category."""
        return ["Music RBT/NSP"]  # Exclude artis RBT packages

    def optimize_quota(self, quota: str) -> str:
        """DATA-specific quota optimization using V1's proven metadata cleanup."""
        if not quota:
            return quota

        # Step 1: Clean metadata using V1's elegant "/" delimiter parsing
        optimized = self.clean_quota_metadata(quota)

        # Step 2: Apply additional optimizations

        # DAYS OPTIMIZATION
        optimized = re.sub(r"\b(\d+)\s+Days\b", r"\1D", optimized, flags=re.IGNORECASE)

        # GB/MB OPTIMIZATION
        optimized = re.sub(
            r"\b(\d+(?:\.\d+)?)\s+GB\b", r"\1GB", optimized, flags=re.IGNORECASE
        )
        optimized = re.sub(r"\b(\d+)\s+MB\b", r"\1MB", optimized, flags=re.IGNORECASE)

        # COMMON WORD REPLACEMENTS
        optimized = re.sub(r"\bInternet\b", "Net", optimized, flags=re.IGNORECASE)
        optimized = re.sub(r"\bNasional\b", "Nas", optimized, flags=re.IGNORECASE)

        # CLEANUP EXTRA SPACES AND COMMAS
        optimized = re.sub(r"\s+", " ", optimized)  # Multiple spaces → single space
        optimized = re.sub(r",\s*,", ",", optimized)  # Double commas → single comma
        optimized = re.sub(r"^\s*,\s*", "", optimized)  # Leading comma
        optimized = re.sub(r"\s*,\s*$", "", optimized)  # Trailing comma

        return optimized.strip()

    def clean_quota_metadata(self, quota: str) -> str:
        """Clean metadata from quota field using V1's proven "/" delimiter parsing.

        Example:
        Input: "DATA National/Internet 30 Days 12 GB Nasional, Local Data/Kuota Lokal Internet 30 Days 43 GB"
        Output: "Internet 30 Days 12 GB Nasional,Kuota Lokal Internet 30 Days 43 GB"
        """
        # Split by comma to get each quota item
        items = quota.split(",")
        cleaned_items = []

        for item in items:
            item = item.strip()
            if "/" in item:
                # Take the part after '/' as the description
                description = item.split("/", 1)[1].strip()
                cleaned_items.append(description)
            elif item:  # If no '/', keep original item (if not empty)
                cleaned_items.append(item)

        return ",".join(cleaned_items)


class ProcessorFactory:
    """Factory to create appropriate processor for each category."""

    _processors: ClassVar = {
        "DATA": DataCategoryProcessor,
        # Add more processors as needed
        # "VOICE_SMS": VoiceSmsProcessor,
        # "DIGITAL_OTHER": DigitalProcessor,
    }

    @classmethod
    def create_processor(cls, category: str) -> CategoryProcessor:
        """Create processor for given category."""
        processor_class = cls._processors.get(category)
        if not processor_class:
            raise ValueError(f"No processor found for category: {category}")

        return processor_class(category)


@timeit
def process_category_response(category: str, response_data: str) -> str:
    """Main entry point for processing category responses."""
    processor = ProcessorFactory.create_processor(category)
    return processor.process_response(response_data)


def main():
    """Test the processor with sample data."""
    with open(SAMPLEDATA, encoding="utf-8") as f:
        response_data = f.read()

    print("Processing DATA category...")
    print(f"Original response size: {len(response_data)} chars")

    result = process_category_response("DATA", response_data)

    print(f"Final output size: {len(result)} chars")
    print(f"Within limit: {len(result) <= MAX_CHAR_LIMIT}")
    print("\nSample output (first 500 chars):")
    print(result[:5000] + "..." if len(result) > 500 else result)


if __name__ == "__main__":
    main()
