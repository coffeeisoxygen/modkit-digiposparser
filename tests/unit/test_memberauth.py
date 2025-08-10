from ipaddress import IPv4Address

import pytest
import yaml
from app.exceptions.exc_member import (
    MemberAuthError,
    MemberInvalidCredentialsError,
    MemberInvalidSignatureError,
    MemberNotFoundError,
)
from app.feature.member.rep_member import MemberRepository
from app.feature.member.sch_member import MemberInDB
from app.feature.member.srv_member_auth import MemberAuthService
from app.feature.transaction.sch_request import ReqClientBase
from pydantic import AnyHttpUrl, SecretStr


@pytest.fixture
def mock_member_repo(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_signature_service(mocker):
    return mocker.Mock()


@pytest.fixture
def member_auth_service(mock_member_repo, mock_signature_service):
    return MemberAuthService(mock_member_repo, mock_signature_service)


@pytest.fixture
def real_member_repo():
    """Create real MemberRepository with test data from actual YAML file."""
    # Use the actual data/members.yaml file for testing
    return MemberRepository("data/members.yaml")


@pytest.fixture
def real_member_auth_service(real_member_repo, mock_signature_service):
    """Auth service with real member data but mocked signature service."""
    return MemberAuthService(real_member_repo, mock_signature_service)


# Test data based on test_members.yaml
@pytest.fixture
def otomax1_member():
    """Active member requiring signature (from test_members.yaml)."""
    return MemberInDB(
        memberid="otomax1",
        name="otomax utama untuk testing dengan sign",
        pin=SecretStr("1234"),
        password=SecretStr("secret123"),
        ipaddress=IPv4Address("192.168.1.1"),
        report_url=AnyHttpUrl("http://192.168.1.1:8080/report"),
        is_active=True,
        allow_nosign=False,
    )


@pytest.fixture
def otomax2_member():
    """Inactive member allowing no-sign (from test_members.yaml)."""
    return MemberInDB(
        memberid="otomax2",
        name="otomax kedua untuk testing tanpa sign",
        pin=SecretStr("5678"),
        password=SecretStr("secret456"),
        ipaddress=IPv4Address("192.168.1.2"),
        report_url=AnyHttpUrl("http://192.168.1.2:8080/report"),
        is_active=False,
        allow_nosign=True,
    )


# Legacy fixtures for backward compatibility
@pytest.fixture
def active_member():
    return MemberInDB(
        memberid="TEST001",
        name="Test Member 1",
        pin=SecretStr("1234"),
        password=SecretStr("test123"),
        ipaddress=IPv4Address("127.0.0.1"),
        report_url=AnyHttpUrl("http://localhost:8080/report"),
        is_active=True,
        allow_nosign=False,
    )


@pytest.fixture
def inactive_member():
    return MemberInDB(
        memberid="TEST002",
        name="Test Member 2",
        pin=SecretStr("1234"),
        password=SecretStr("test123"),
        ipaddress=IPv4Address("127.0.0.1"),
        report_url=AnyHttpUrl("http://localhost:8080/report"),
        is_active=False,
        allow_nosign=False,
    )


@pytest.fixture
def nosign_member():
    return MemberInDB(
        memberid="TEST003",
        name="Test Member 3",
        pin=SecretStr("1234"),
        password=SecretStr("test123"),
        ipaddress=IPv4Address("127.0.0.1"),
        report_url=AnyHttpUrl("http://localhost:8080/report"),
        is_active=True,
        allow_nosign=True,
    )


@pytest.fixture
def valid_request():
    return ReqClientBase(
        memberid="TEST001",
        product="DATA",
        dest="081234567890",
        refid="REF001",
        pin="123467",
        password="test123",
        sign="valid_signature",
    )


@pytest.mark.unit
class TestMemberAuthService:
    @pytest.mark.unit
    def test_authenticate_member_not_found(
        self, member_auth_service, mock_member_repo, valid_request
    ):
        """Test authentication fails when member not found"""
        mock_member_repo.get_member_by_id.return_value = None

        with pytest.raises(MemberNotFoundError) as exc_info:
            member_auth_service.authenticate_and_verify(valid_request)

        assert "Member ID 'TEST001' not found" in str(exc_info.value)
        mock_member_repo.get_member_by_id.assert_called_once_with("TEST001")

    @pytest.mark.unit
    def test_authenticate_inactive_member(
        self, member_auth_service, mock_member_repo, inactive_member, valid_request
    ):
        """Test authentication fails for inactive member"""
        mock_member_repo.get_member_by_id.return_value = inactive_member

        with pytest.raises(MemberAuthError) as exc_info:
            member_auth_service.authenticate_and_verify(valid_request)

        assert "Member tidak aktif" in str(exc_info.value)

    @pytest.mark.unit
    def test_authenticate_with_valid_signature(
        self,
        member_auth_service,
        mock_member_repo,
        mock_signature_service,
        active_member,
        valid_request,
    ):
        """Test successful authentication with valid signature"""
        mock_member_repo.get_member_by_id.return_value = active_member
        mock_signature_service.generate_transaction_signature.return_value = (
            "valid_signature"
        )

        result = member_auth_service.authenticate_and_verify(valid_request)

        assert result == active_member
        mock_signature_service.generate_transaction_signature.assert_called_once()

    @pytest.mark.unit
    def test_authenticate_with_invalid_signature(
        self,
        member_auth_service,
        mock_member_repo,
        mock_signature_service,
        active_member,
        valid_request,
    ):
        """Test authentication fails with invalid signature"""
        mock_member_repo.get_member_by_id.return_value = active_member
        mock_signature_service.generate_transaction_signature.return_value = (
            "different_signature"
        )

        with pytest.raises(MemberInvalidSignatureError) as exc_info:
            member_auth_service.authenticate_and_verify(valid_request)

        assert "Signature tidak valid" in str(exc_info.value)

    @pytest.mark.unit
    def test_authenticate_nosign_with_valid_pin(
        self, member_auth_service, mock_member_repo, nosign_member
    ):
        """Test successful authentication without signature using PIN"""
        mock_member_repo.get_member_by_id.return_value = nosign_member
        request = ReqClientBase(
            memberid="TEST003",
            product="DATA",
            dest="081234567890",
            refid="REF001",
            pin="1234",
        )

        result = member_auth_service.authenticate_and_verify(request)

        assert result == nosign_member

    @pytest.mark.unit
    def test_authenticate_nosign_with_valid_password(
        self, member_auth_service, mock_member_repo, nosign_member
    ):
        """Test successful authentication without signature using password"""
        mock_member_repo.get_member_by_id.return_value = nosign_member
        request = ReqClientBase(
            memberid="TEST003",
            product="DATA",
            dest="081234567890",
            refid="REF001",
            password="test123",
        )

        result = member_auth_service.authenticate_and_verify(request)

        assert result == nosign_member

    @pytest.mark.unit
    def test_authenticate_nosign_with_invalid_credentials(
        self, member_auth_service, mock_member_repo, nosign_member
    ):
        """Test authentication fails with invalid PIN/password for nosign member"""
        mock_member_repo.get_member_by_id.return_value = nosign_member
        request = ReqClientBase(
            memberid="TEST003",
            product="DATA",
            dest="081234567890",
            refid="REF001",
            pin="wrong_pin",
        )

        with pytest.raises(MemberInvalidCredentialsError) as exc_info:
            member_auth_service.authenticate_and_verify(request)

        assert "PIN atau Password tidak valid" in str(exc_info.value)

    @pytest.mark.unit
    def test_authenticate_requires_signature_but_none_provided(
        self, member_auth_service, mock_member_repo, active_member
    ):
        """Test authentication fails when signature required but not provided"""
        mock_member_repo.get_member_by_id.return_value = active_member
        request = ReqClientBase(
            memberid="TEST001",
            product="DATA",
            dest="081234567890",
            refid="REF001",
            pin="1234",
        )

        with pytest.raises(MemberInvalidSignatureError) as exc_info:
            member_auth_service.authenticate_and_verify(request)

        assert "Signature wajib untuk member ini" in str(exc_info.value)

    @pytest.mark.unit
    def test_verify_signature_with_empty_optional_fields(
        self,
        member_auth_service,
        mock_member_repo,
        mock_signature_service,
        active_member,
    ):
        """Test signature verification handles empty optional fields correctly"""
        mock_member_repo.get_member_by_id.return_value = active_member
        mock_signature_service.generate_transaction_signature.return_value = (
            "valid_signature"
        )

        request = ReqClientBase(
            memberid="TEST001",
            product="DATA",
            dest="081234567890",
            sign="valid_signature",
            refid="REF001",
        )

        result = member_auth_service.authenticate_and_verify(request)

        assert result == active_member
        mock_signature_service.generate_transaction_signature.assert_called_once_with(
            memberid="TEST001",
            product="DATA",
            dest="081234567890",
            refid="",
            pin="",
            password="",
        )

    @pytest.mark.unit
    def test_verify_signature_method_called_with_no_signature(
        self, member_auth_service, active_member
    ):
        """Test _verify_signature method fails when called without signature"""
        request = ReqClientBase(
            memberid="TEST001", product="DATA", dest="081234567890", refid="REF001"
        )

        with pytest.raises(MemberInvalidSignatureError) as exc_info:
            member_auth_service._verify_signature(request, active_member)

        assert "Signature tidak ada di request" in str(exc_info.value)


@pytest.mark.unit
class TestMemberAuthServiceWithRealData:
    """Integration tests using real test data from YAML."""

    @pytest.mark.unit
    def test_authenticate_otomax1_with_signature(
        self, real_member_auth_service, mock_signature_service, otomax1_member
    ):
        """Test authentication of otomax1 with valid signature."""
        mock_signature_service.generate_transaction_signature.return_value = (
            "valid_signature"
        )

        request = ReqClientBase(
            memberid="otomax1",
            product="DATA",
            dest="081234567890",
            refid="REF001",
            sign="valid_signature",
        )

        result = real_member_auth_service.authenticate_and_verify(request)

        assert result.memberid == "otomax1"
        assert result.is_active is True
        assert result.allow_nosign is False

    @pytest.mark.unit
    def test_authenticate_otomax2_inactive_member(
        self, real_member_auth_service, otomax2_member
    ):
        """Test authentication fails for inactive otomax2."""
        request = ReqClientBase(
            memberid="otomax2",
            product="DATA",
            dest="081234567890",
            refid="REF001",
            pin="5678",
        )

        with pytest.raises(MemberAuthError) as exc_info:
            real_member_auth_service.authenticate_and_verify(request)

        assert "Member tidak aktif" in str(exc_info.value)

    @pytest.mark.unit
    def test_authenticate_otomax1_requires_signature(self, real_member_auth_service):
        """Test otomax1 requires signature (allow_nosign=False)."""
        request = ReqClientBase(
            memberid="otomax1",
            product="DATA",
            dest="081234567890",
            refid="REF001",
            pin="1234",
        )

        with pytest.raises(MemberInvalidSignatureError) as exc_info:
            real_member_auth_service.authenticate_and_verify(request)

        assert "Signature wajib untuk member ini" in str(exc_info.value)

    @pytest.mark.unit
    def test_member_not_found_in_real_data(self, real_member_auth_service):
        """Test member not found with real data source."""
        request = ReqClientBase(
            memberid="nonexistent", product="DATA", dest="081234567890", refid="REF001"
        )

        with pytest.raises(MemberNotFoundError) as exc_info:
            real_member_auth_service.authenticate_and_verify(request)

        assert "Member ID 'nonexistent' not found" in str(exc_info.value)
