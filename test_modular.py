"""Test file for the new modular response processing.

Test the refactored structure with existing proven logic.
"""

from pathlib import Path

from app.service.response import (
    get_processor_type,
    get_supported_categories,
    is_category_supported,
    process_category_response,
)

# Test data paths
BASE_PATH = Path(__file__).resolve().parent.parent.parent.parent
DATA_SAMPLE = BASE_PATH / "example_final_DATA.json"
DIGITAL_SAMPLE = BASE_PATH / "example_final_digital_other.json"


def test_supported_categories():
    """Test category support functionality."""
    print("=== SUPPORTED CATEGORIES ===")
    categories = get_supported_categories()
    print(f"Total supported: {len(categories)}")
    print(f"Categories: {sorted(categories)}")
    print()


def test_processor_routing():
    """Test processor type routing."""
    print("=== PROCESSOR ROUTING ===")

    test_categories = ["DATA", "VOICE_SMS", "VF", "HVC_DATA", "INVALID"]

    for category in test_categories:
        if is_category_supported(category):
            processor_type = get_processor_type(category)
            print(f"✅ {category:15} → {processor_type}")
        else:
            print(f"❌ {category:15} → UNSUPPORTED")
    print()


def test_recharge_processing():
    """Test recharge processing with proven DATA sample."""
    print("=== RECHARGE PROCESSING TEST ===")

    if not DATA_SAMPLE.exists():
        print(f"❌ Sample file not found: {DATA_SAMPLE}")
        return

    with open(DATA_SAMPLE, encoding="utf-8") as f:
        response_data = f.read()

    print(f"Original size: {len(response_data)} chars")

    try:
        result = process_category_response("DATA", response_data)
        print(f"Processed size: {len(result)} chars")
        print(f"Within limit: {len(result) <= 7000}")
        print(f"Sample output: {result[:200]}...")
        print("✅ Recharge processing SUCCESS")
    except Exception as e:
        print(f"❌ Recharge processing FAILED: {e}")
    print()


def test_small_response():
    """Test processing with small response (should skip optimization)."""
    print("=== SMALL RESPONSE TEST ===")

    if not DIGITAL_SAMPLE.exists():
        print(f"❌ Sample file not found: {DIGITAL_SAMPLE}")
        return

    with open(DIGITAL_SAMPLE, encoding="utf-8") as f:
        response_data = f.read()

    print(f"Original size: {len(response_data)} chars (should be < 7000)")

    try:
        result = process_category_response("DIGITAL_OTHER", response_data)
        print(f"Processed size: {len(result)} chars")
        print("✅ Small response processing SUCCESS")
    except Exception as e:
        print(f"❌ Small response processing FAILED: {e}")
    print()


def test_activation_processing():
    """Test activation processing (VF) - placeholder for now."""
    print("=== ACTIVATION PROCESSING TEST ===")

    # Minimal test JSON for VF
    vf_sample = '{"to":"123456","paket":[{"productId":"VF001","productName":"Test VF Product","quota":"Test quota","total_":1000}]}'

    try:
        result = process_category_response("VF", vf_sample)
        print(f"VF processed size: {len(result)} chars")
        print(f"VF sample output: {result}")
        print("✅ Activation processing SUCCESS (placeholder)")
    except Exception as e:
        print(f"❌ Activation processing FAILED: {e}")
    print()


def main():
    """Run all tests."""
    print("🚀 TESTING MODULAR RESPONSE PROCESSING\n")

    test_supported_categories()
    test_processor_routing()
    test_recharge_processing()
    test_small_response()
    test_activation_processing()

    print("✅ ALL TESTS COMPLETED")


if __name__ == "__main__":
    main()
