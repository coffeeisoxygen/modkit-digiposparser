"""Activation processor for VCR/VF category.

Handles: VF (VCR activation)
VF structure: {"req":{...},"res":[...]} vs recharge: {"to":"...","paket":[...]}
"""

import re
from typing import Any

from app.service.response.base_processor import BaseProcessor


class ActivationProcessor(BaseProcessor):
    """Processor for activation-type categories (VCR/VF)."""

    def __init__(self, category: str):
        super().__init__(category, "ACTIVATION")

    def get_exclude_subcategories(self) -> list[str]:
        """Subcategories to exclude for VF category."""
        # No exclusions for VF by default
        return [""]

    def get_exclude_productnames(self) -> list[str]:
        """Product name patterns to exclude for VF category."""
        # No exclusions for VF by default
        return [""]

    def get_exclude_quota_metadata(self) -> list[str]:
        """Quota metadata patterns to exclude for VF category."""
        # No exclusions for VF by default
        return [""]

    def optimize_quota(self, quota: str) -> str:
        """VF-specific quota optimization - same as recharge but adapted for VF."""
        if not quota:
            return quota

        # Step 1: Clean metadata using same "/" delimiter parsing as recharge
        optimized = self.clean_quota_metadata(quota)

        # Step 2: Apply same text optimizations as recharge
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
        """Clean metadata from quota field using same logic as recharge."""
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

    def format_product_output(self, product: dict[str, Any]) -> str:
        """Format product output for VF category.

        VF uses 'price' instead of 'total_' field.
        Format: #id|name(quota)|price#
        """
        product_id = product.get("productId", "")
        product_name = product.get("productName", "")
        quota = product.get("quota", "")
        price = product.get("price", "")  # VF uses 'price' not 'total_'

        # Format: #id|name(quota)|price#
        return f"#{product_id}|{product_name}({quota})|{price}"

    # Override base processor methods to handle VF structure
    def _filter_by_subcategory(self, data: dict[str, Any]) -> dict[str, Any]:
        """Filter products by excluded subcategories - VF version."""
        exclude_list = self.get_exclude_subcategories()
        if not exclude_list or not any(exclude_list):
            return data

        original_count = len(data.get("res", []))  # VF uses 'res' not 'paket'
        filtered_res = []

        for product in data.get("res", []):
            subcategory = product.get("productSubCategory", "")
            if subcategory not in exclude_list:
                filtered_res.append(product)

        data["res"] = filtered_res
        self.logger.info(
            f"Subcategory filter: {original_count} → {len(filtered_res)} products"
        )
        return data

    def _filter_by_productname(self, data: dict[str, Any]) -> dict[str, Any]:
        """Filter products by excluded product name patterns - VF version."""
        exclude_patterns = self.get_exclude_productnames()
        if not exclude_patterns or not any(exclude_patterns):
            return data

        original_count = len(data.get("res", []))  # VF uses 'res' not 'paket'
        filtered_res = []

        for product in data.get("res", []):
            product_name = product.get("productName", "")
            should_exclude = any(
                re.match(rf"^{re.escape(pattern)}", product_name, re.IGNORECASE)
                for pattern in exclude_patterns
                if pattern.strip()
            )

            if not should_exclude:
                filtered_res.append(product)

        data["res"] = filtered_res
        self.logger.info(
            f"Product name filter: {original_count} → {len(filtered_res)} products"
        )
        return data

    def _filter_by_quota_metadata(self, data: dict[str, Any]) -> dict[str, Any]:
        """Filter products by excluded quota metadata patterns - VF version."""
        exclude_patterns = self.get_exclude_quota_metadata()
        if not exclude_patterns or not any(exclude_patterns):
            return data

        original_count = len(data.get("res", []))  # VF uses 'res' not 'paket'
        filtered_res = []

        for product in data.get("res", []):
            quota = product.get("quota", "")
            should_exclude = any(
                pattern in quota for pattern in exclude_patterns if pattern.strip()
            )

            if not should_exclude:
                filtered_res.append(product)

        data["res"] = filtered_res
        self.logger.info(
            f"Quota metadata filter: {original_count} → {len(filtered_res)} products"
        )
        return data

    def _optimize_quotas(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply quota optimization to all products - VF version."""
        for product in data.get("res", []):  # VF uses 'res' not 'paket'
            original_quota = product.get("quota", "")
            optimized_quota = self.optimize_quota(original_quota)
            product["quota"] = optimized_quota

        self.logger.info(f"Optimized quotas for {len(data.get('res', []))} products")
        return data

    def _format_output(self, data: dict[str, Any]) -> str:
        """Format final output using VF-specific formatting."""
        output_parts = []

        for product in data.get("res", []):  # VF uses 'res' not 'paket'
            formatted = self.format_product_output(product)
            output_parts.append(formatted)

        return "".join(output_parts)
