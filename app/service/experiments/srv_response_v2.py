"""this will be second approach.

pendekatan experiment kali ini adalah dengan menyusun functional , lalu di akhir akan di evaluasi untuk menjadi class.
"""

import json
from pathlib import Path
from typing import Any

from app.mlogg.log_utils import logger, timeit

SAMPLEDATA = (
    Path(__file__).resolve().parent.parent.parent.parent / "example_response.json"
)


@timeit
def count_responsechar(response: Any, threshold: int) -> tuple[int, bool]:
    """Hitung jumlah karakter pada response JSON.

    Logging dengan context 'count_responsechar'.
    Return: (jumlah karakter, apakah perlu parsing)
    """
    total_char = len(str(response))
    need_more_processing = total_char > threshold
    logger.bind(func="count_responsechar").info(
        f"total_char={total_char}, need_more_processing={need_more_processing}"
    )
    return total_char, need_more_processing


def extract_quota_metadata(quota_string: str) -> list[str]:
    """Extract metadata dari quota string.

    Pattern: metadata/deskripsi, metadata/deskripsi
    Return: list metadata saja (tanpa deskripsi)
    """
    metadata_list = []

    # Split by comma, trim whitespace
    quota_parts = [part.strip() for part in quota_string.split(",") if part.strip()]

    for part in quota_parts:
        # Split by slash and ambil bagian pertama (metadata)
        if "/" in part:
            metadata = part.split("/")[0].strip()
            if metadata:
                metadata_list.append(metadata)

    # logger.bind(func="extract_quota_metadata").debug(
    #     f"Extracted {len(metadata_list)} metadata from quota"
    # )
    return metadata_list


@timeit
def analyze_product_quota_patterns(response_data: str) -> None:
    """Analisa pattern metadata quota untuk setiap produk."""
    data = json.loads(response_data)
    paket_list = data.get("paket", [])

    print("\n=== QUOTA METADATA ANALYSIS ===")
    print(f"Total products: {len(paket_list)}")
    print("-" * 50)

    for i, product in enumerate(paket_list, 1):
        product_id = product.get("productId", "Unknown")
        product_name = product.get("productName", "Unknown")
        quota = product.get("quota", "")

        # Extract metadata
        metadata_list = extract_quota_metadata(quota)

        print(f"{i:2d}. {product_id}-{product_name}")
        print(
            f"    Metadata: {', '.join(metadata_list) if metadata_list else 'No metadata found'}"
        )
        print()

    logger.bind(func="analyze_product_quota_patterns").info(
        f"Analyzed {len(paket_list)} products"
    )


def main():
    """Main function to run the character counting and quota metadata analysis."""
    with open(SAMPLEDATA, encoding="utf-8") as f:
        response_data = f.read()
    _, need_more_processing = count_responsechar(response_data, 7000)

    if need_more_processing:
        # Lakukan parsing dan analisa metadata quota
        analyze_product_quota_patterns(response_data)
    else:
        logger.bind(func="main").info("Parser succeeded")


if __name__ == "__main__":
    main()
