"""Integration tests for Digipos schemas.

Testing schema inheritance, validation, and compatibility with MemberAuthService.
"""

import pytest
from app.feature.digipos.sch_digipos import (
    DigiposCatAsProdEnum,
    DigiposRequestBuy,
    DigiposRequestCheck,
    DigiposRequestList,
    DigiposTrxRequestBase,
    DigposActionEnum,
)
from app.feature.member.rep_member import MemberRepository
from app.feature.member.srv_member_auth import MemberAuthService
from pydantic import ValidationError


@pytest.mark.integration
class TestDigiposSchemaInheritance:
    """Test inheritance pattern and compatibility with base schemas."""

    def test_base_schema_inheritance(self):
        """Test that DigiposTrxRequestBase properly inherits from ReqClientBase."""
        # Test basic creation with required fields from ReqClientBase
        request = DigiposTrxRequestBase(
            memberid="test123",
            product="DATA",
            dest="08123456789",
            refid="REF001",
            action="list",
        )

        # Verify inheritance fields
        assert request.memberid == "test123"
        assert request.product == "DATA"
        assert request.dest == "08123456789"
        assert request.refid == "REF001"

        # Verify digipos specific fields
        assert request.action == DigposActionEnum.LIST
        assert request.markup == 0  # Default value is 0

        # Verify authentication fields are available
        assert request.sign is None
        assert request.pin is None
        assert request.password is None

    def test_list_request_optional_fields(self):
        """Test DigiposRequestList with all combinations of optional fields."""
        # Test minimal required fields
        request_minimal = DigiposRequestList(
            memberid="test123",
            product="DATA",
            dest="08123456789",
            refid="REF001",
            action="list",
        )
        assert request_minimal.minday is None
        assert request_minimal.maxday is None
        assert request_minimal.markup == 0  # Default value is 0

        # Test with some optional fields
        request_partial = DigiposRequestList(
            memberid="test123",
            product="DATA",
            dest="08123456789",
            refid="REF001",
            action="list",
            minday=1,
        )
        assert request_partial.minday == 1
        assert request_partial.maxday is None

        # Test with all optional fields
        request_full = DigiposRequestList(
            memberid="test123",
            product="DATA",
            dest="08123456789",
            refid="REF001",
            action="list",
            minday=1,
            maxday=30,
            markup=1000,
        )
        assert request_full.minday == 1
        assert request_full.maxday == 30
        assert request_full.markup == 1000

    def test_check_request_schema(self):
        """Test DigiposRequestCheck specific fields and validation."""
        request = DigiposRequestCheck(
            memberid="test123",
            product="DATA",
            dest="08123456789",
            refid="REF001",
            productid="PRD001",
            markup=500,
        )

        assert request.action == DigposActionEnum.CHECK
        assert request.productid == "PRD001"
        assert request.markup == 500

    def test_buy_request_schema(self):
        """Test DigiposRequestBuy specific fields and validation."""
        request = DigiposRequestBuy(
            memberid="test123",
            product="DATA",
            dest="08123456789",
            refid="REF001",
            productid="PRD001",
            markup=500,
        )

        assert request.action == DigposActionEnum.BUY
        assert request.productid == "PRD001"
        assert request.markup == 500


@pytest.mark.integration
class TestDigiposValidation:
    """Test validation rules for Digipos schemas."""

    def test_enum_validation(self):
        """Test that enum fields validate correctly."""
        # Valid action enum
        request = DigiposRequestList(
            memberid="test123",
            product="DATA",
            dest="08123456789",
            refid="REF001",
            action="list",
        )
        assert request.action == DigposActionEnum.LIST

        # Valid product category enum
        request_data = DigiposRequestList(
            memberid="test123",
            product=DigiposCatAsProdEnum.DATA,
            dest="08123456789",
            refid="REF001",
            action="list",
        )
        assert request_data.product == "DATA"

    def test_invalid_enum_validation(self):
        """Test that invalid enum values raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DigiposRequestList(
                memberid="test123",
                product="DATA",
                dest="08123456789",
                refid="REF001",
                action="invalid_action",
            )

        assert "Input should be 'list', 'check' or 'buy'" in str(exc_info.value)

    def test_negative_values_validation(self):
        """Test that negative values are properly handled."""
        # Test negative minday should be converted to None or raise error
        with pytest.raises(ValidationError):
            DigiposRequestList(
                memberid="test123",
                product="DATA",
                dest="08123456789",
                refid="REF001",
                action="list",
                minday=-1,
            )

        # Test negative markup should be converted to None or raise error
        with pytest.raises(ValidationError):
            DigiposRequestList(
                memberid="test123",
                product="DATA",
                dest="08123456789",
                refid="REF001",
                action="list",
                markup=-100,
            )

    def test_dest_pattern_validation(self):
        """Test that dest field validates as numeric string."""
        # Valid numeric string
        request_valid = DigiposRequestList(
            memberid="test123",
            product="DATA",
            dest="08123456789",
            refid="REF001",
            action="list",
        )
        assert request_valid.dest == "08123456789"

        # Invalid non-numeric string should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            DigiposRequestList(
                memberid="test123",
                product="DATA",
                dest="invalid_dest",
                refid="REF001",
                action="list",
            )

        assert "String should match pattern" in str(exc_info.value)


@pytest.mark.integration
class TestDigiposAuthCompatibility:
    """Test compatibility between Digipos schemas and MemberAuthService."""

    @pytest.fixture
    def member_repo(self):
        """Real member repository for testing."""
        return MemberRepository("data/members.yaml")

    @pytest.fixture
    def auth_service(self, member_repo):
        """MemberAuthService instance for testing."""
        return MemberAuthService(member_repo)

    def test_digipos_request_with_auth_service(self, auth_service):
        """Test that DigiposRequestList can be used with MemberAuthService."""
        # Create digipos request with authentication
        request = DigiposRequestList(
            memberid="otomax3",  # From test data - allows nosign
            product="DATA",
            dest="08123456789",
            refid="REF001",
            action="list",
            pin="111222",  # Valid PIN from test data
        )

        # Should be able to authenticate
        result = auth_service.authenticate_and_verify(request)

        assert result.memberid == "otomax3"
        assert result.is_active is True
        assert result.allow_nosign is True

    def test_digipos_request_with_signature_auth(self, auth_service, mocker):
        """Test DigiposRequestCheck with signature authentication."""
        # Mock signature service for this test
        mocker.patch.object(
            auth_service.otomax_sign_service,
            "generate_transaction_signature",
            return_value="valid_signature",
        )

        request = DigiposRequestCheck(
            memberid="otomax1",  # Requires signature
            product="DATA",
            dest="08123456789",
            refid="REF001",
            action="check",
            productid="PRD001",
            sign="valid_signature",
        )

        result = auth_service.authenticate_and_verify(request)

        assert result.memberid == "otomax1"
        assert result.is_active is True
        assert result.allow_nosign is False

    def test_digipos_request_field_access(self):
        """Test that all inherited fields are accessible."""
        request = DigiposRequestBuy(
            memberid="test123",
            product="DATA",
            dest="08123456789",
            refid="REF001",
            action="buy",
            productid="PRD001",
            markup=500,
            pin="123456",
            password="secret123",
            sign="test_signature",
        )

        # Test ReqClientBase fields
        assert hasattr(request, "memberid")
        assert hasattr(request, "product")
        assert hasattr(request, "dest")
        assert hasattr(request, "refid")
        assert hasattr(request, "sign")
        assert hasattr(request, "pin")
        assert hasattr(request, "password")

        # Test DigiposTrxRequestBase fields
        assert hasattr(request, "action")
        assert hasattr(request, "markup")

        # Test DigiposRequestBuy specific fields
        assert hasattr(request, "productid")

        # Verify values
        assert request.memberid == "test123"
        assert request.action == DigposActionEnum.BUY
        assert request.productid == "PRD001"
        assert request.markup == 500
        assert request.pin == "123456"
        assert request.password == "secret123"
        assert request.sign == "test_signature"


@pytest.mark.integration
class TestDigiposRealWorldScenarios:
    """Test real-world usage scenarios for Digipos schemas."""

    def test_list_request_minimal_payload(self):
        """Test typical list request with minimal payload."""
        # Typical user request without optional fields
        request = DigiposRequestList(
            memberid="otomax3",
            product="DATA",
            dest="08123456789",
            refid="TRX001",
            action="list",
        )

        assert request.action == "list"
        assert request.product == "DATA"
        assert request.minday is None
        assert request.maxday is None
        assert request.markup == 0

    def test_list_request_with_filters(self):
        """Test list request with day range filters."""
        # User request with day filters
        request = DigiposRequestList(
            memberid="otomax3",
            product="DATA",
            dest="08123456789",
            refid="TRX002",
            action="list",
            minday=7,
            maxday=30,
        )

        assert request.minday == 7
        assert request.maxday == 30

    def test_buy_request_complete_payload(self):
        """Test buy request with complete authentication."""
        request = DigiposRequestBuy(
            memberid="otomax3",
            product="DATA",
            dest="08123456789",
            refid="TRX003",
            action="buy",
            productid="DATA_5GB_30D",
            markup=1000,
            pin="111222",
        )

        assert request.action == "buy"
        assert request.productid == "DATA_5GB_30D"
        assert request.markup == 1000
        assert request.pin == "111222"

    def test_schema_serialization(self):
        """Test that schemas can be serialized and deserialized."""
        original = DigiposRequestList(
            memberid="test123",
            product="DATA",
            dest="08123456789",
            refid="REF001",
            action="list",
            minday=1,
            maxday=30,
        )

        # Serialize to dict
        data = original.model_dump()

        # Deserialize back
        reconstructed = DigiposRequestList(**data)

        assert reconstructed.memberid == original.memberid
        assert reconstructed.action == original.action
        assert reconstructed.minday == original.minday
        assert reconstructed.maxday == original.maxday
