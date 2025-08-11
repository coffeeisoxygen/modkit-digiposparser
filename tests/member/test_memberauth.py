"""Tests for MemberAuthService using Repository pattern and conftest.py fixtures."""

import pytest
from app.exceptions import (
    MemberAuthError,
    MemberInvalidCredentialsError,
    MemberInvalidSignatureError,
    MemberNotFoundError,
)
from app.feature.member.rep_member import MemberRepository
from app.feature.member.sch_member import MemberInDB, MemberTrxRequestModel
from app.feature.member.srv_member_auth import MemberAuthService
from pydantic import ValidationError

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_member_repo(mocker):
    """Mock repository for unit tests."""
    return mocker.Mock(spec=MemberRepository)


@pytest.fixture
def member_auth_service(mock_member_repo):
    """MemberAuthService with mocked repository."""
    return MemberAuthService(mock_member_repo)


# =============================================================================
# UNIT TESTS - VALIDATION
# =============================================================================


@pytest.mark.unit
class TestMemberTrxRequestValidation:
    """Test validation of MemberTrxRequestModel schema."""

    def test_valid_request_should_pass(self, valid_trx_request):
        """Test that valid request data passes validation."""
        # Arrange & Act
        request = MemberTrxRequestModel(**valid_trx_request)

        # Assert
        assert request.memberid == valid_trx_request["memberid"]
        assert request.dest == valid_trx_request["dest"]
        assert request.product == valid_trx_request["product"]

    @pytest.mark.parametrize("missing_field", ["memberid", "dest", "product"])
    def test_missing_required_fields_should_fail(
        self, valid_trx_request, missing_field
    ):
        """Test that missing required fields raise ValidationError."""
        # Arrange
        invalid_data = valid_trx_request.copy()
        del invalid_data[missing_field]

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            MemberTrxRequestModel(**invalid_data)
        assert missing_field in str(exc_info.value)

    def test_optional_fields_can_be_none(self, valid_trx_request):
        """Test that optional fields can be None."""
        # Arrange
        data = valid_trx_request.copy()
        data.update({"pin": None, "password": None, "sign": None, "refid": None})

        # Act
        request = MemberTrxRequestModel(**data)

        # Assert
        assert request.pin is None
        assert request.password is None
        assert request.sign is None
        assert request.refid is None


# =============================================================================
# UNIT TESTS - AUTHENTICATION SERVICE
# =============================================================================


@pytest.mark.unit
class TestMemberAuthService:
    """Unit tests for MemberAuthService using mocks."""

    def test_member_not_found_should_raise_error(
        self, member_auth_service, mock_member_repo, valid_trx_request
    ):
        """Test authentication fails when member not found."""
        # Arrange
        mock_member_repo.get_member_by_id.return_value = None
        request = MemberTrxRequestModel(**valid_trx_request)

        # Act & Assert
        with pytest.raises(MemberNotFoundError) as exc_info:
            member_auth_service.authenticate_and_verify(request)
        assert "Member ID" in str(exc_info.value)
        mock_member_repo.get_member_by_id.assert_called_once_with(request.memberid)

    def test_inactive_member_should_raise_error(
        self, member_auth_service, mock_member_repo, valid_member_db, valid_trx_request
    ):
        """Test authentication fails for inactive member."""
        # Arrange
        inactive_member_data = valid_member_db.copy()
        inactive_member_data["is_active"] = False
        mock_member_repo.get_member_by_id.return_value = MemberInDB(
            **inactive_member_data
        )
        request = MemberTrxRequestModel(**valid_trx_request)

        # Act & Assert
        with pytest.raises(MemberAuthError) as exc_info:
            member_auth_service.authenticate_and_verify(request)
        assert "Member tidak aktif" in str(exc_info.value)

    def test_signature_required_but_not_provided_should_fail(
        self, member_auth_service, mock_member_repo, valid_member_db, valid_trx_request
    ):
        """Test authentication fails when signature required but not provided."""
        # Arrange
        member_data = valid_member_db.copy()
        member_data["allow_nosign"] = False
        mock_member_repo.get_member_by_id.return_value = MemberInDB(**member_data)

        request_data = valid_trx_request.copy()
        request_data["sign"] = None
        request = MemberTrxRequestModel(**request_data)

        # Act & Assert
        with pytest.raises(MemberInvalidSignatureError) as exc_info:
            member_auth_service.authenticate_and_verify(request)
        assert "Signature wajib untuk member ini" in str(exc_info.value)

    def test_valid_signature_should_authenticate(
        self,
        member_auth_service,
        mock_member_repo,
        valid_member_db,
        valid_trx_request_with_sign,
        mocker,
    ):
        """Test successful authentication with valid signature."""
        # Arrange
        member = MemberInDB(**valid_member_db)
        mock_member_repo.get_member_by_id.return_value = member
        request = MemberTrxRequestModel(**valid_trx_request_with_sign)

        # Mock signature verification to return True
        mock_verify = mocker.patch.object(
            member_auth_service.otomax_sign_service,
            "verify_signature",
            return_value=True,
        )

        # Act
        result = member_auth_service.authenticate_and_verify(request)

        # Assert
        assert result == member
        mock_verify.assert_called_once()

    def test_invalid_signature_should_fail(
        self,
        member_auth_service,
        mock_member_repo,
        valid_member_db,
        valid_trx_request_with_sign,
        mocker,
    ):
        """Test authentication fails with invalid signature."""
        # Arrange
        member = MemberInDB(**valid_member_db)
        mock_member_repo.get_member_by_id.return_value = member
        request = MemberTrxRequestModel(**valid_trx_request_with_sign)

        # Mock signature verification to return False
        mock_verify = mocker.patch.object(
            member_auth_service.otomax_sign_service,
            "verify_signature",
            return_value=False,
        )

        # Act & Assert
        with pytest.raises(MemberInvalidSignatureError) as exc_info:
            member_auth_service.authenticate_and_verify(request)
        assert "Signature tidak valid" in str(exc_info.value)
        mock_verify.assert_called_once()

    def test_nosign_member_with_valid_pin_should_authenticate(
        self, member_auth_service, mock_member_repo, valid_member_db, valid_trx_request
    ):
        """Test successful authentication without signature using valid PIN."""
        # Arrange
        member_data = valid_member_db.copy()
        member_data["allow_nosign"] = True
        member = MemberInDB(**member_data)
        mock_member_repo.get_member_by_id.return_value = member

        request_data = valid_trx_request.copy()
        request_data["sign"] = None
        request_data["pin"] = member_data["pin"]  # Use same PIN as member
        request = MemberTrxRequestModel(**request_data)

        # Act
        result = member_auth_service.authenticate_and_verify(request)

        # Assert
        assert result == member

    def test_nosign_member_with_valid_password_should_authenticate(
        self, member_auth_service, mock_member_repo, valid_member_db, valid_trx_request
    ):
        """Test successful authentication without signature using valid password."""
        # Arrange
        member_data = valid_member_db.copy()
        member_data["allow_nosign"] = True
        member = MemberInDB(**member_data)
        mock_member_repo.get_member_by_id.return_value = member

        request_data = valid_trx_request.copy()
        request_data["sign"] = None
        request_data["password"] = member_data[
            "password"
        ]  # Use same password as member
        request = MemberTrxRequestModel(**request_data)

        # Act
        result = member_auth_service.authenticate_and_verify(request)

        # Assert
        assert result == member

    def test_nosign_member_with_invalid_credentials_should_fail(
        self, member_auth_service, mock_member_repo, valid_member_db, valid_trx_request
    ):
        """Test authentication fails with invalid PIN/password for nosign member."""
        # Arrange
        member_data = valid_member_db.copy()
        member_data["allow_nosign"] = True
        member = MemberInDB(**member_data)
        mock_member_repo.get_member_by_id.return_value = member

        request_data = valid_trx_request.copy()
        request_data["sign"] = None
        request_data["pin"] = "wrong_pin"
        request_data["password"] = "wrong_password"
        request = MemberTrxRequestModel(**request_data)

        # Act & Assert
        with pytest.raises(MemberInvalidCredentialsError) as exc_info:
            member_auth_service.authenticate_and_verify(request)
        assert "PIN atau Password tidak valid" in str(exc_info.value)

    def test_nosign_member_with_missing_credentials_should_fail(
        self, member_auth_service, mock_member_repo, valid_member_db, valid_trx_request
    ):
        """Test authentication fails when no credentials provided for nosign member."""
        # Arrange
        member_data = valid_member_db.copy()
        member_data["allow_nosign"] = True
        member = MemberInDB(**member_data)
        mock_member_repo.get_member_by_id.return_value = member

        request_data = valid_trx_request.copy()
        request_data["sign"] = None
        request_data["pin"] = None
        request_data["password"] = None
        request = MemberTrxRequestModel(**request_data)

        # Act & Assert
        with pytest.raises(MemberInvalidCredentialsError) as exc_info:
            member_auth_service.authenticate_and_verify(request)
        assert "PIN atau Password tidak valid" in str(exc_info.value)


# =============================================================================
# INTEGRATION TESTS WITH REAL SIGNATURE
# =============================================================================


@pytest.mark.integration
class TestMemberAuthServiceWithRealSignature:
    """Integration tests using real signature verification."""

    def test_authenticate_with_real_signature_data(
        self, member_auth_service, mock_member_repo, otomax_signature_sample_data
    ):
        """Test authentication with real signature data from conftest.py."""
        # Arrange
        member_data = {
            "memberid": "AKSES01",  # Updated to match actual otomax data
            "name": "AKSES Test Member",
            "pin": otomax_signature_sample_data["pin"],
            "password": otomax_signature_sample_data["password"],
            "is_active": True,
            "ipaddress": "192.168.1.10",
            "report_url": "http://192.168.1.10:8080/report",
            "allow_nosign": False,
        }
        member = MemberInDB(**member_data)
        mock_member_repo.get_member_by_id.return_value = member

        request_data = {
            "memberid": "AKSES01",  # Match the member data
            "dest": otomax_signature_sample_data["dest"],
            "product": otomax_signature_sample_data["product"],
            "pin": otomax_signature_sample_data["pin"],
            "password": otomax_signature_sample_data["password"],
            "sign": otomax_signature_sample_data["expected_sign"],
            "refid": otomax_signature_sample_data["refid"],
        }
        request = MemberTrxRequestModel(**request_data)

        # Act
        result = member_auth_service.authenticate_and_verify(request)

        # Assert
        assert result == member


# =============================================================================
# SMOKE TESTS
# =============================================================================


@pytest.mark.smoke
class TestMemberAuthServiceSmoke:
    """Smoke tests for basic functionality."""

    def test_service_instantiation(self, mock_member_repo):
        """Test that service can be instantiated."""
        # Act
        service = MemberAuthService(mock_member_repo)

        # Assert
        assert service is not None
        assert service.member_manager == mock_member_repo  # Fixed attribute name
        assert service.otomax_sign_service is not None

    def test_basic_authentication_flow(
        self,
        member_auth_service,
        mock_member_repo,
        valid_member_db,
        valid_trx_request_with_sign,
        mocker,
    ):
        """Test basic authentication flow works end-to-end."""
        # Arrange
        member = MemberInDB(**valid_member_db)
        mock_member_repo.get_member_by_id.return_value = member
        request = MemberTrxRequestModel(**valid_trx_request_with_sign)

        mocker.patch.object(
            member_auth_service.otomax_sign_service,
            "verify_signature",
            return_value=True,
        )

        # Act
        result = member_auth_service.authenticate_and_verify(request)

        # Assert
        assert result is not None
        assert isinstance(result, MemberInDB)
        assert result.memberid == request.memberid
