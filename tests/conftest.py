from pathlib import Path

import pytest


@pytest.fixture
def sample_members_yaml_path():
    """Fixture to provide path to sample test members yaml."""
    return Path(__file__).parent / ".sample" / "test_members.yaml"


@pytest.fixture(
    params=[
        # Valid member (active, allow_nosign False)
        {
            "memberid": "WIR6289504",
            "pin": "123456",
            "password": "password",
            "is_active": True,
            "allow_nosign": False,
        },
        # Valid member (active, allow_nosign True)
        {
            "memberid": "TEST003",
            "pin": "654321",
            "password": "test123",
            "is_active": True,
            "allow_nosign": True,
        },
        # Invalid PIN
        {
            "memberid": "WIR6289504",
            "pin": "wrongpin",
            "password": "password",
            "is_active": True,
            "allow_nosign": False,
        },
        # Invalid password
        {
            "memberid": "WIR6289504",
            "pin": "123456",
            "password": "wrongpass",
            "is_active": True,
            "allow_nosign": False,
        },
        # Missing password
        {
            "memberid": "WIR6289504",
            "pin": "123456",
            "is_active": True,
            "allow_nosign": False,
        },
        # Missing pin
        {
            "memberid": "WIR6289504",
            "password": "password",
            "is_active": True,
            "allow_nosign": False,
        },
        # Inactive member
        {
            "memberid": "INACTIVE01",
            "pin": "111111",
            "password": "inactivepass",
            "is_active": False,
            "allow_nosign": True,
        },
        # Missing memberid
        {
            "pin": "123456",
            "password": "password",
            "is_active": True,
            "allow_nosign": False,
        },
    ]
)
def sample_member_data(request):
    """Parametrized fixture for various member data scenarios."""
    return request.param


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
