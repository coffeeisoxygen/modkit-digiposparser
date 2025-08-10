"""Integration tests for DigiposUrlBuilder."""

import pytest
from app.dependencies.dep_settings import get_digipos_config
from app.feature.digipos.sch_digipos import DigiposRequestList, DigposActionEnum
from app.feature.digipos.srv_digipos_url_builder import DigiposUrlBuilder


@pytest.mark.integration
class TestDigiposUrlBuilder:
    """Test URL building for Digipos API forwarding."""

    @pytest.fixture
    def url_builder(self):
        """DigiposUrlBuilder instance with config."""
        config = get_digipos_config()
        return DigiposUrlBuilder(config)

    def test_basic_list_url_generation(self, url_builder):
        """Test basic list URL generation."""
        request = DigiposRequestList(
            memberid="test123",
            product="DATA",
            dest="081295221639",
            refid="1LIST",
            action=DigposActionEnum.LIST,
        )

        url = url_builder.build_list_url(request)

        # Basic URL structure check
        assert "list_paket?" in url
        assert "category=DATA" in url
        assert "to=081295221639" in url
        assert "trxid=1LIST" in url
        assert "payment_method=LINKAJA" in url
        assert "json=1" in url

    def test_list_url_with_markup(self, url_builder):
        """Test list URL generation with markup (should map to up_harga)."""
        request = DigiposRequestList(
            memberid="test123",
            product="DATA",
            dest="081295221639",
            refid="1LIST",
            action=DigposActionEnum.LIST,
            markup=100,
        )

        url = url_builder.build_list_url(request)

        assert "up_harga=100" in url

    def test_list_url_with_day_filters(self, url_builder):
        """Test list URL generation with day filters."""
        request = DigiposRequestList(
            memberid="test123",
            product="DATA",
            dest="081295221639",
            refid="1LIST",
            action=DigposActionEnum.LIST,
            minday=7,
            maxday=30,
        )

        url = url_builder.build_list_url(request)

        assert "min_hari=7" in url
        assert "max_hari=30" in url

    def test_list_url_complete_params(self, url_builder):
        """Test complete list URL with all optional parameters."""
        request = DigiposRequestList(
            memberid="test123",
            product="DATA",
            dest="081295221639",
            refid="1LIST",
            action=DigposActionEnum.LIST,
            markup=100,
            minday=7,
            maxday=30,
        )

        url = url_builder.build_list_url(request)

        # Check all expected parameters
        expected_params = [
            "list_paket?",
            "category=DATA",
            "to=081295221639",
            "trxid=1LIST",
            "payment_method=LINKAJA",
            "up_harga=100",
            "min_hari=7",
            "max_hari=30",
            "json=1",
            "kolom=productId%2CproductSubCategory%2CproductName%2CDuration%2Ctotal_",
        ]

        for param in expected_params:
            assert param in url, f"Parameter '{param}' not found in URL: {url}"

    def test_no_double_slashes_in_url(self, url_builder):
        """Test that generated URLs don't have double slashes."""
        request = DigiposRequestList(
            memberid="test123",
            product="DATA",
            dest="081295221639",
            refid="1LIST",
            action=DigposActionEnum.LIST,
        )

        url = url_builder.build_list_url(request)

        # Should not have double slashes between base URL and endpoint
        assert "//" not in url.split("://")[1], f"Double slash found in URL: {url}"
