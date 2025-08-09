"""Activation processor for VCR/VF category.

Handles: VF (VCR activation)
"""

from typing import Any

from app.service.response.base_processor import BaseProcessor


class ActivationProcessor(BaseProcessor):
    """Processor for activation-type categories (VCR/VF)."""

    def __init__(self, category: str):
        super().__init__(category, "ACTIVATION")

    def get_exclude_subcategories(self) -> list[str]:
        """Subcategories to exclude for VF category."""
        # TODO: Implement VF-specific exclusions after analyzing VF data
        return [""]

    def get_exclude_productnames(self) -> list[str]:
        """Product name patterns to exclude for VF category."""
        # TODO: Implement VF-specific exclusions after analyzing VF data
        return [""]

    def get_exclude_quota_metadata(self) -> list[str]:
        """Quota metadata patterns to exclude for VF category."""
        # TODO: Implement VF-specific exclusions after analyzing VF data
        return [""]

    def optimize_quota(self, quota: str) -> str:
        """VF-specific quota optimization."""
        if not quota:
            return quota

        # TODO: Implement VF-specific optimizations after analyzing VF data structure
        # For now, return as-is (no optimization needed for short responses)
        return quota

    def format_product_output(self, product: dict[str, Any]) -> str:
        """Format product output for VF category.

        TODO: Determine VF-specific format after analyzing VF data structure.
        May differ from recharge format.
        """
        product_id = product.get("productId", "")
        product_name = product.get("productName", "")
        quota = product.get("quota", "")
        total = product.get("total_", "")

        # Placeholder format - same as recharge for now
        # TODO: Adjust format after analyzing VF response structure
        return f"#{product_id}|{product_name}({quota})|{total}"
