from unittest.mock import Mock

import pytest
from app.exceptions.exc_member import (
    MemberAuthError,
    MemberInvalidCredentialsError,
    MemberInvalidSignatureError,
    MemberNotFoundError,
)
from app.feature.member.sch_member import MemberInDB
from app.feature.member.srv_member_auth import MemberAuthService
from app.feature.transaction.sch_request import ReqClientBase


@pytest.fixture
def mock_member_repo():
    return Mock()


@pytest.fixture
def mock_signature_service():
    return Mock()


@pytest.fixture
def member_auth_service(mock_member_repo, mock_signature_service):
    return MemberAuthService(mock_member_repo, mock_signature_service)


@pytest.fixture
def active_member():
    return MemberInDB(
        memberid="TEST001",
        pin="1234",
        password="test123",
        is_active=True,
        allow_nosign=False,
    )


@pytest.fixture
def inactive_member():
    return MemberInDB(
        memberid="TEST002",
        pin="1234",
        password="test123",
        is_active=False,
        allow_nosign=False,
    )


@pytest.fixture
def nosign_member():
    return MemberInDB(
        memberid="TEST003",
        pin="1234",
        password="test123",
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
        pin="1234",
        password="test123",
        sign="valid_signature",
    )


@pytest.mark.smoke
class TestMemberAuthService:
    def test_authenticate_member_not_found(
        self, member_auth_service, mock_member_repo, valid_request
    ):
        """Test authentication fails when member not found"""
        mock_member_repo.get_member_by_id.return_value = None

        with pytest.raises(MemberNotFoundError) as exc_info:
            member_auth_service.authenticate_and_verify(valid_request)

        assert "Member ID 'TEST001' not found" in str(exc_info.value)
        mock_member_repo.get_member_by_id.assert_called_once_with("TEST001")

    def test_authenticate_inactive_member(
        self, member_auth_service, mock_member_repo, inactive_member, valid_request
    ):
        """Test authentication fails for inactive member"""
        mock_member_repo.get_member_by_id.return_value = inactive_member

        with pytest.raises(MemberAuthError) as exc_info:
            member_auth_service.authenticate_and_verify(valid_request)

        assert "Member tidak aktif" in str(exc_info.value)

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

    @pytest.mark.quick
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

    @pytest.mark.experimenting
    def test_verify_signature_method_called_with_no_signature(
        self, member_auth_service, active_member
    ):
        """Test _verify_signature method fails when called without signature"""
        request = ReqClientBase(memberid="TEST001", product="DATA", dest="081234567890")

        with pytest.raises(MemberInvalidSignatureError) as exc_info:
            member_auth_service._verify_signature(request, active_member)

        assert "Signature tidak ada di request" in str(exc_info.value)
