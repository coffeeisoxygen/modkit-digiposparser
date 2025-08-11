from pathlib import Path

import pytest


@pytest.fixture
def sample_members_yaml_path():
    """Fixture to provide path to sample test members yaml."""
    return Path(__file__).parent / ".sample" / "test_members.yaml"


# =============================================================================
# MEMBER DATABASE FIXTURES (MemberInDB)
# =============================================================================


@pytest.fixture(
    params=[
        # Valid member (active, allow_nosign False)
        {
            "memberid": "WIR6289504",
            "name": "OTOMAX Utama",
            "pin": "123456",
            "password": "password",
            "is_active": True,
            "ipaddress": "192.168.1.1",
            "report_url": "http://192.168.1.1:8080/report",
            "allow_nosign": False,
        },
        # Valid member (active, allow_nosign True)
        {
            "memberid": "TEST003",
            "name": "Test Member No Sign",
            "pin": "654321",
            "password": "test123",
            "is_active": True,
            "ipaddress": "192.168.1.2",
            "report_url": "http://192.168.1.2:8080/report",
            "allow_nosign": True,
        },
        # Inactive member
        {
            "memberid": "INACTIVE01",
            "name": "Inactive Member",
            "pin": "111111",
            "password": "inactivepass",
            "is_active": False,
            "ipaddress": "192.168.1.3",
            "report_url": "http://192.168.1.3:8080/report",
            "allow_nosign": True,
        },
    ]
)
def sample_member_db_data(request):
    """Parametrized fixture for MemberInDB scenarios."""
    return request.param


# =============================================================================
# TRANSACTION REQUEST FIXTURES (MemberTrxRequestModel)
# =============================================================================


@pytest.fixture(
    params=[
        # Valid request with signature
        {
            "memberid": "WIR6289504",
            "dest": "081295221639",
            "product": "PULSA5000",
            "pin": "123456",
            "password": "password",
            "sign": "valid_signature_here",
            "refid": "TRX001",
        },
        # Valid request without signature (allow_nosign=True)
        {
            "memberid": "TEST003",
            "dest": "081234567890",
            "product": "DATA1GB",
            "pin": "654321",
            "password": "test123",
            "refid": "TRX002",
        },
        # Missing PIN
        {
            "memberid": "WIR6289504",
            "dest": "081295221639",
            "product": "PULSA5000",
            "password": "password",
            "refid": "TRX003",
        },
        # Missing password
        {
            "memberid": "WIR6289504",
            "dest": "081295221639",
            "product": "PULSA5000",
            "pin": "123456",
            "refid": "TRX004",
        },
        # Invalid PIN
        {
            "memberid": "WIR6289504",
            "dest": "081295221639",
            "product": "PULSA5000",
            "pin": "wrongpin",
            "password": "password",
            "refid": "TRX005",
        },
        # Invalid password
        {
            "memberid": "WIR6289504",
            "dest": "081295221639",
            "product": "PULSA5000",
            "pin": "123456",
            "password": "wrongpass",
            "refid": "TRX006",
        },
        # Missing memberid (should fail validation)
        {
            "dest": "081295221639",
            "product": "PULSA5000",
            "pin": "123456",
            "password": "password",
            "refid": "TRX007",
        },
        # Missing dest (should fail validation)
        {
            "memberid": "WIR6289504",
            "product": "PULSA5000",
            "pin": "123456",
            "password": "password",
            "refid": "TRX008",
        },
        # Missing product (should fail validation)
        {
            "memberid": "WIR6289504",
            "dest": "081295221639",
            "pin": "123456",
            "password": "password",
            "refid": "TRX009",
        },
    ]
)
def sample_trx_request_data(request):
    """Parametrized fixture for MemberTrxRequestModel scenarios."""
    return request.param


# =============================================================================
# SPECIFIC TEST DATA FIXTURES
# =============================================================================


@pytest.fixture
def valid_member_db():
    """Single valid member for database operations."""
    return {
        "memberid": "WIR6289504",
        "name": "OTOMAX Utama",
        "pin": "123456",
        "password": "password",
        "is_active": True,
        "ipaddress": "192.168.1.1",
        "report_url": "http://192.168.1.1:8080/report",
        "allow_nosign": False,
    }


@pytest.fixture
def valid_trx_request():
    """Single valid transaction request."""
    return {
        "memberid": "WIR6289504",
        "dest": "081295221639",
        "product": "PULSA5000",
        "pin": "123456",
        "password": "password",
        "refid": "TRX001",
    }


@pytest.fixture
def valid_trx_request_with_sign():
    """Valid transaction request with signature."""
    return {
        "memberid": "WIR6289504",
        "dest": "081295221639",
        "product": "PULSA5000",
        "pin": "123456",
        "password": "password",
        "sign": "valid_signature",
        "refid": "TRX001",
    }


# =============================================================================
# SIGNATURE TEST DATA
# =============================================================================


@pytest.fixture
def otomax_signature_sample_data():
    """
    Fixture for actual member data and expected signature used in
    test_otomax_signature_should_match_actual_generated_sign.
    """
    return {
        "memberid": "vps",
        "pin": "777999",
        "password": "vps777999",
        "product": "CLPDATA",
        "qty": "1",  # not used in signature
        "dest": "081295221639",
        "refid": "3041094LIST",
        "expected_sign": "FzqLAOMAa2yJKA7e-w_fSQkXjrY",
    }


# =============================================================================
# DIGIPOS API PRODUCT TEST DATA
# =============================================================================


@pytest.fixture
def sample_digipos_products():
    """Sample product data for Digipos API testing."""
    return [
        {"productId": "PULSA5K", "productName": "Pulsa 5000", "category": "PULSA"},
        {"productId": "DATA1GB", "productName": "Data 1GB", "category": "DATA"},
        {
            "productId": "CLPDATA",
            "productName": "Paket Chat Lite Plus",
            "category": "DATA",
        },
    ]


@pytest.fixture
def sample_list_paket_params():
    """Sample parameters for list_paket endpoint."""
    return {
        "memberid": "WIR6289504",
        "dest": "081295221639",
        "category": "DATA",
        "up_harga": 100,
        "kolom": "productId,productName,quota,total_",
        "trxid": "1LIST",
        "payment_method": "LINKAJA",
    }


# =============================================================================
# ERROR CASES FOR VALIDATION TESTING
# =============================================================================


@pytest.fixture
def invalid_dest_formats():
    """Invalid destination number formats for validation testing."""
    return [
        "",  # Empty string
        "123",  # Too short
        "08129522163912345678901234567890",  # Too long
        "abc123",  # Contains letters
        "+628129522163",  # Contains plus sign
        "08129522163 ",  # Contains space
    ]


@pytest.fixture
def invalid_product_codes():
    """Invalid product codes for validation testing."""
    return [
        "",  # Empty string
        "INVALID_PRODUCT_CODE_THAT_IS_TOO_LONG_FOR_NORMAL_USE",  # Too long
        "PROD WITH SPACES",  # Contains spaces
        "PROD@#$%",  # Contains special characters
    ]


@pytest.fixture
def edge_case_memberids():
    """Edge case member IDs for testing."""
    return [
        "A",  # Too short (min 5 required)
        "AB",  # Still too short
        "VALID5",  # Minimum valid length
        "VERYLONGMEMBERIDTHATMIGHTCAUSEISSUES",  # Long but valid
        "MEM123",  # Mixed alphanumeric
    ]
