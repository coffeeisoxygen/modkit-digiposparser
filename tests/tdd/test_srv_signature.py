import pytest
from app.feature.member.srv_signature import OtomaxSignatureService


@pytest.mark.unit
def test_generate_transaction_signature_should_return_expected_signature(
    valid_trx_request,
):
    # Arrange
    memberid = valid_trx_request["memberid"]
    product = valid_trx_request["product"]
    dest = valid_trx_request["dest"]
    refid = valid_trx_request["refid"]
    pin = valid_trx_request["pin"]
    password = valid_trx_request["password"]

    # Act
    signature = OtomaxSignatureService.generate_transaction_signature(
        memberid, product, dest, refid, pin, password
    )

    # Assert
    # Signature should be deterministic for same input
    expected = OtomaxSignatureService.generate_transaction_signature(
        memberid, product, dest, refid, pin, password
    )
    assert signature == expected, f"Expected {expected}, got {signature}"


@pytest.mark.unit
def test_generate_transaction_signature_should_be_url_safe(valid_trx_request):
    # Arrange - modify data to include problematic characters
    memberid = valid_trx_request["memberid"]
    product = valid_trx_request["product"]
    dest = valid_trx_request["dest"]
    refid = valid_trx_request["refid"]
    pin = "12+34/"  # Characters that should be encoded
    password = "pa+ss/w0rd"  # Characters that should be encoded

    # Act
    signature = OtomaxSignatureService.generate_transaction_signature(
        memberid, product, dest, refid, pin, password
    )

    # Assert
    assert "+" not in signature and "/" not in signature, (
        f"Signature contains unsafe chars: {signature}"
    )


@pytest.mark.unit
def test_verify_signature_should_return_true_for_valid_signature(valid_trx_request):
    # Arrange
    data = {
        "memberid": valid_trx_request["memberid"],
        "product": valid_trx_request["product"],
        "dest": valid_trx_request["dest"],
        "refid": valid_trx_request["refid"],
        "pin": valid_trx_request["pin"],
        "password": valid_trx_request["password"],
    }
    signature = OtomaxSignatureService.generate_transaction_signature(**data)

    # Act
    result = OtomaxSignatureService.verify_signature(data, signature)

    # Assert
    assert result is True, "Expected verification to succeed for valid signature"


@pytest.mark.unit
def test_verify_signature_should_return_false_for_invalid_signature(valid_trx_request):
    # Arrange
    data = {
        "memberid": valid_trx_request["memberid"],
        "product": valid_trx_request["product"],
        "dest": valid_trx_request["dest"],
        "refid": valid_trx_request["refid"],
        "pin": valid_trx_request["pin"],
        "password": valid_trx_request["password"],
    }
    invalid_signature = "invalidsignature"

    # Act
    result = OtomaxSignatureService.verify_signature(data, invalid_signature)

    # Assert
    assert result is False, "Expected verification to fail for invalid signature"


@pytest.mark.unit
@pytest.mark.parametrize(
    "field,value",
    [
        ("memberid", ""),
        ("product", ""),
        ("dest", ""),
        ("refid", ""),
        ("pin", ""),
        ("password", ""),
    ],
)
def test_generate_transaction_signature_should_handle_empty_fields(
    field, value, valid_trx_request
):
    # Arrange
    data = {
        "memberid": valid_trx_request["memberid"],
        "product": valid_trx_request["product"],
        "dest": valid_trx_request["dest"],
        "refid": valid_trx_request["refid"],
        "pin": valid_trx_request["pin"],
        "password": valid_trx_request["password"],
    }
    data[field] = value

    # Act
    signature = OtomaxSignatureService.generate_transaction_signature(**data)

    # Assert
    assert isinstance(signature, str) and len(signature) > 0, (
        f"Signature should be non-empty for empty {field}"
    )


@pytest.mark.unit
def test_otomax_signature_should_match_actual_generated_sign(
    otomax_signature_sample_data,
):
    # Arrange
    memberid = otomax_signature_sample_data["memberid"]
    pin = otomax_signature_sample_data["pin"]
    password = otomax_signature_sample_data["password"]
    product = otomax_signature_sample_data["product"]
    dest = otomax_signature_sample_data["dest"]
    refid = otomax_signature_sample_data["refid"]
    expected_sign = otomax_signature_sample_data["expected_sign"]

    # Act
    signature = OtomaxSignatureService.generate_transaction_signature(
        memberid, product, dest, refid, pin, password
    )

    # Assert
    assert signature == expected_sign, f"Expected {expected_sign}, got {signature}"
