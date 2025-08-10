"""Updated tests for MemberAuthService using Repository pattern."""

from ipaddress import IPv4Address

import pytest
from app.exceptions.exc_member import (
    MemberAuthError,
    MemberInvalidCredentialsError,
    MemberInvalidSignatureError,
    MemberNotFoundError,
)
from app.feature.member.rep_member import MemberRepository
from app.feature.member.sch_member import MemberInDB, MemberTrxRequestModel
from app.feature.member.srv_member_auth import MemberAuthService
from pydantic import AnyHttpUrl, SecretStr


@pytest.fixture
def mock_member_repo(mocker):
    """Mock repository for unit tests."""
    return mocker.Mock(spec=MemberRepository)


@pytest.fixture
def member_auth_service(mock_member_repo):
    """MemberAuthService with mocked repository (signature service auto-instantiated)."""
    return MemberAuthService(mock_member_repo)


@pytest.fixture
def real_member_repo():
    """Real MemberRepository using actual data/members.yaml file."""
    return MemberRepository("data/members.yaml")


@pytest.fixture
def real_member_auth_service(real_member_repo):
    """Auth service with real member data (signature service auto-instantiated)."""
    return MemberAuthService(real_member_repo)


# Test fixtures for members from actual YAML
@pytest.fixture
def active_member():
    """Generic active member for testing."""
    return MemberInDB(
        memberid="TEST001",
        name="Test Member 1",
        pin=SecretStr("123456"),  # Fix: minimal 6 karakter
        password=SecretStr("test123"),
        ipaddress=IPv4Address("127.0.0.1"),
        report_url=AnyHttpUrl("http://localhost:8080/report"),
        is_active=True,
        allow_nosign=False,
    )


@pytest.fixture
def inactive_member():
    """Generic inactive member for testing."""
    return MemberInDB(
        memberid="TEST002",
        name="Test Member 2",
        pin=SecretStr("789012"),  # Fix: minimal 6 karakter
        password=SecretStr("test123"),
        ipaddress=IPv4Address("127.0.0.1"),
        report_url=AnyHttpUrl("http://localhost:8080/report"),
        is_active=False,
        allow_nosign=False,
    )


@pytest.fixture
def nosign_member():
    """Generic member allowing no-sign authentication."""
    return MemberInDB(
        memberid="TEST003",
        name="Test Member 3",
        pin=SecretStr("345678"),  # Fix: minimal 6 karakter
        password=SecretStr("test123"),
        ipaddress=IPv4Address("127.0.0.1"),
        report_url=AnyHttpUrl("http://localhost:8080/report"),
        is_active=True,
        allow_nosign=True,
    )


@pytest.fixture
def valid_request():
    """Valid request for testing."""
    return MemberTrxRequestModel(
        memberid="TEST001",
        product="DATA",
        refid="REF001",
        pin="123456",
        password="test123",
        sign="valid_signature",
    )


@pytest.mark.unit
class TestMemberAuthService:
    """Unit tests for MemberAuthService using mocks."""

    def test_authenticate_member_not_found(
        self, member_auth_service, mock_member_repo, valid_request
    ):
        """Test authentication fails when member not found."""
        mock_member_repo.get_member_by_id.return_value = None

        with pytest.raises(MemberNotFoundError) as exc_info:
            member_auth_service.authenticate_and_verify(valid_request)

        assert "Member ID 'TEST001' not found" in str(exc_info.value)
        mock_member_repo.get_member_by_id.assert_called_once_with("TEST001")

    def test_authenticate_inactive_member(
        self, member_auth_service, mock_member_repo, inactive_member, valid_request
    ):
        """Test authentication fails for inactive member."""
        mock_member_repo.get_member_by_id.return_value = inactive_member

        with pytest.raises(MemberAuthError) as exc_info:
            member_auth_service.authenticate_and_verify(valid_request)

        assert "Member tidak aktif" in str(exc_info.value)

    def test_authenticate_with_valid_signature(
        self,
        member_auth_service,
        mock_member_repo,
        active_member,
        valid_request,
        mocker,
    ):
        """Test successful authentication with valid signature."""
        mock_member_repo.get_member_by_id.return_value = active_member
        # Mock the signature service method directly on the instance
        mocker.patch.object(
            member_auth_service.otomax_sign_service,
            "generate_transaction_signature",
            return_value="valid_signature",
        )

        result = member_auth_service.authenticate_and_verify(valid_request)

        assert result == active_member

    def test_authenticate_with_invalid_signature(
        self,
        member_auth_service,
        mock_member_repo,
        active_member,
        valid_request,
        mocker,
    ):
        """Test authentication fails with invalid signature."""
        mock_member_repo.get_member_by_id.return_value = active_member
        # Mock signature service to return different signature
        mocker.patch.object(
            member_auth_service.otomax_sign_service,
            "generate_transaction_signature",
            return_value="different_signature",
        )

        with pytest.raises(MemberInvalidSignatureError) as exc_info:
            member_auth_service.authenticate_and_verify(valid_request)

        assert "Signature tidak valid" in str(exc_info.value)

    def test_authenticate_nosign_with_valid_pin(
        self, member_auth_service, mock_member_repo, nosign_member
    ):
        """Test successful authentication without signature using PIN."""
        mock_member_repo.get_member_by_id.return_value = nosign_member
        request = MemberTrxRequestModel(
            memberid="TEST003",
            product="DATA",
            dest="08123456567890",
            refid="REF001",
            pin="345678",  # Fix: sesuai dengan nosign_member fixture
        )  # type: ignore

        result = member_auth_service.authenticate_and_verify(request)

        assert result == nosign_member

    def test_authenticate_nosign_with_valid_password(
        self, member_auth_service, mock_member_repo, nosign_member
    ):
        """Test successful authentication without signature using password."""
        mock_member_repo.get_member_by_id.return_value = nosign_member
        request = MemberTrxRequestModel(
            memberid="TEST003",
            product="DATA",
            dest="08123456567890",
            refid="REF001",
            password="test123",
        )

        result = member_auth_service.authenticate_and_verify(request)

        assert result == nosign_member

    def test_authenticate_nosign_with_invalid_credentials(
        self, member_auth_service, mock_member_repo, nosign_member
    ):
        """Test authentication fails with invalid PIN/password for nosign member."""
        mock_member_repo.get_member_by_id.return_value = nosign_member
        request = MemberTrxRequestModel(
            memberid="TEST003",
            product="DATA",
            dest="08123456567890",
            refid="REF001",
            pin="wrong_pin",
        )

        with pytest.raises(MemberInvalidCredentialsError) as exc_info:
            member_auth_service.authenticate_and_verify(request)

        assert "PIN atau Password tidak valid" in str(exc_info.value)

    def test_authenticate_requires_signature_but_none_provided(
        self, member_auth_service, mock_member_repo, active_member
    ):
        """Test authentication fails when signature required but not provided."""
        mock_member_repo.get_member_by_id.return_value = active_member
        request = MemberTrxRequestModel(
            memberid="TEST001",
            product="DATA",
            dest="08123456567890",
            refid="REF001",
            pin="123456",
        )

        with pytest.raises(MemberInvalidSignatureError) as exc_info:
            member_auth_service.authenticate_and_verify(request)

        assert "Signature wajib untuk member ini" in str(exc_info.value)


@pytest.mark.integration
class TestMemberAuthServiceWithRealRepo:
    """Integration tests using real MemberRepository with actual YAML data."""

    def test_authenticate_otomax1_with_signature(
        self, real_member_auth_service, mocker
    ):
        """Test authentication of otomax1 (active, requires signature)."""
        # Mock signature service on the real auth service instance
        mocker.patch.object(
            real_member_auth_service.otomax_sign_service,
            "generate_transaction_signature",
            return_value="valid_signature",
        )

        request = MemberTrxRequestModel(
            memberid="otomax1",
            product="DATA",
            dest="08123456567890",
            refid="REF001",
            sign="valid_signature",
        )

        result = real_member_auth_service.authenticate_and_verify(request)

        assert result.memberid == "otomax1"
        assert result.is_active is True
        assert result.allow_nosign is False

    def test_authenticate_otomax2_inactive_member(self, real_member_auth_service):
        """Test authentication fails for inactive otomax2."""
        request = MemberTrxRequestModel(
            memberid="otomax2",
            product="DATA",
            dest="08123456567890",
            refid="REF001",
            pin="898989",
        )

        with pytest.raises(MemberAuthError) as exc_info:
            real_member_auth_service.authenticate_and_verify(request)

        assert "Member tidak aktif" in str(exc_info.value)

    def test_authenticate_otomax3_nosign_with_pin(self, real_member_auth_service):
        """Test otomax3 authentication with PIN (active, allow_nosign=True)."""
        request = MemberTrxRequestModel(
            memberid="otomax3",
            product="DATA",
            dest="08123456567890",
            refid="REF001",
            pin="111222",
        )

        result = real_member_auth_service.authenticate_and_verify(request)

        assert result.memberid == "otomax3"
        assert result.is_active is True
        assert result.allow_nosign is True

    def test_authenticate_otomax3_nosign_with_password(self, real_member_auth_service):
        """Test otomax3 authentication with password."""
        request = MemberTrxRequestModel(
            memberid="otomax3",
            product="DATA",
            dest="08123456567890",
            refid="REF001",
            password="secret789",
        )

        result = real_member_auth_service.authenticate_and_verify(request)

        assert result.memberid == "otomax3"

    def test_authenticate_otomax1_requires_signature(self, real_member_auth_service):
        """Test otomax1 requires signature (allow_nosign=False)."""
        request = MemberTrxRequestModel(
            memberid="otomax1",
            product="DATA",
            dest="08123456567890",
            refid="REF001",
            pin="777999",
        )

        with pytest.raises(MemberInvalidSignatureError) as exc_info:
            real_member_auth_service.authenticate_and_verify(request)

        assert "Signature wajib untuk member ini" in str(exc_info.value)

    def test_member_not_found_in_real_data(self, real_member_auth_service):
        """Test member not found with real data source."""
        request = MemberTrxRequestModel(
            memberid="nonexistent",
            product="DATA",
            dest="08123456567890",
            refid="REF001",
        )

        with pytest.raises(MemberNotFoundError) as exc_info:
            real_member_auth_service.authenticate_and_verify(request)

        assert "Member ID 'nonexistent' not found" in str(exc_info.value)

    def test_repository_integration(self, real_member_repo):
        """Test that repository integration works correctly."""
        # Test repository basic functionality
        assert (
            real_member_repo.get_member_count() >= 3
        )  # Should have at least our test members

        # Test specific member lookup
        otomax1 = real_member_repo.get_member_by_id("otomax1")
        assert otomax1 is not None
        assert otomax1.memberid == "otomax1"
        assert otomax1.is_active is True
        assert otomax1.allow_nosign is False

        otomax3 = real_member_repo.get_member_by_id("otomax3")
        assert otomax3 is not None
        assert otomax3.memberid == "otomax3"
        assert otomax3.is_active is True
        assert otomax3.allow_nosign is True

        # Test non-existent member
        nonexistent = real_member_repo.get_member_by_id("nonexistent")
        assert nonexistent is None
