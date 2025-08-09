"""Recharge processor for mobile number categories.

Handles: DATA, VOICE_SMS, DIGITAL_OTHER, DIGITAL_MUSIC, DIGITAL_GAME,
         ROAMING, BYU, HVC_DATA, HVC_VOICE_SMS
"""

import re
from typing import Any

from app.service.response.base_processor import BaseProcessor


class RechargeProcessor(BaseProcessor):
    """Processor for recharge-type categories (mobile numbers)."""

    def __init__(self, category: str):
        super().__init__(category, "RECHARGE")

    def get_exclude_subcategories(self) -> list[str]:
        """Subcategories to exclude for recharge categories."""
        return [""]  # No exclusions by default

    def get_exclude_productnames(self) -> list[str]:
        """Product name patterns to exclude for recharge categories."""
        return [""]  # No exclusions by default

    def get_exclude_quota_metadata(self) -> list[str]:
        """Quota metadata patterns to exclude for recharge categories."""
        # Universal filter for artis/music content across all recharge categories
        return ["Music RBT/NSP"]

    def optimize_quota(self, quota: str) -> str:
        """Recharge-specific quota optimization using V1's proven metadata cleanup."""
        if not quota:
            return quota

        # Step 1: Clean metadata using V1's elegant "/" delimiter parsing
        optimized = self.clean_quota_metadata(quota)

        # Step 2: Apply universal text optimizations

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

    def format_product_output(self, product: dict[str, Any]) -> str:
        """Format product output for recharge categories.

        Standard format: #id|name(quota)|total#
        """
        product_id = product.get("productId", "")
        product_name = product.get("productName", "")
        quota = product.get("quota", "")
        total = product.get("total_", "")

        # Format: #id|name(quota)|total#
        return f"#{product_id}|{product_name}({quota})|{total}"
