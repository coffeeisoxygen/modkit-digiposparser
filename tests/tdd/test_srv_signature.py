import pytest
from app.feature.srv_signature import OtomaxSignatureService


@pytest.mark.unit
def test_generate_transaction_signature_should_return_expected_signature():
    # Arrange
    memberid = "abc123"
    product = "pulsa"
    dest = "08123456789"
    refid = "REF001"
    pin = "1234"
    password = "passw0rd"
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
def test_generate_transaction_signature_should_be_url_safe():
    # Arrange
    memberid = "abc123"
    product = "pulsa"
    dest = "08123456789"
    refid = "REF001"
    pin = "12+34/"
    password = "pa+ss/w0rd"
    # Act
    signature = OtomaxSignatureService.generate_transaction_signature(
        memberid, product, dest, refid, pin, password
    )
    # Assert
    assert "+" not in signature and "/" not in signature, (
        f"Signature contains unsafe chars: {signature}"
    )


@pytest.mark.unit
def test_verify_signature_should_return_true_for_valid_signature():
    # Arrange
    data = {
        "memberid": "abc123",
        "product": "pulsa",
        "dest": "08123456789",
        "refid": "REF001",
        "pin": "1234",
        "password": "passw0rd",
    }
    signature = OtomaxSignatureService.generate_transaction_signature(**data)
    # Act
    result = OtomaxSignatureService.verify_signature(data, signature)
    # Assert
    assert result is True, "Expected verification to succeed for valid signature"


@pytest.mark.unit
def test_verify_signature_should_return_false_for_invalid_signature():
    # Arrange
    data = {
        "memberid": "abc123",
        "product": "pulsa",
        "dest": "08123456789",
        "refid": "REF001",
        "pin": "1234",
        "password": "passw0rd",
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
def test_generate_transaction_signature_should_handle_empty_fields(field, value):
    # Arrange
    data = {
        "memberid": "abc123",
        "product": "pulsa",
        "dest": "08123456789",
        "refid": "REF001",
        "pin": "1234",
        "password": "passw0rd",
    }
    data[field] = value
    # Act
    signature = OtomaxSignatureService.generate_transaction_signature(**data)
    # Assert
    assert isinstance(signature, str) and len(signature) > 0, (
        f"Signature should be non-empty for empty {field}"
    )


@pytest.mark.unit
def test_otomax_signature_should_match_actual_generated_sign():
    # Arrange
    memberid = "vps"
    pin = "777999"
    password = "vps777999"
    product = "CLPDATA"
    qty = "1"
    dest = "081295221639"
    refid = "3041094LIST"
    # Act
    signature = OtomaxSignatureService.generate_transaction_signature(
        memberid, product, dest, refid, pin, password
    )
    # Assert
    expected_sign = "FzqLAOMAa2yJKA7e-w_fSQkXjrY"
    assert signature == expected_sign, f"Expected {expected_sign}, got {signature}"
