"""Digipos URL Builder Service.

Service untuk mapping request internal ke URL Digipos API format.
"""

from typing import Any
from urllib.parse import urlencode

from app.config.cfg_core import DigiposCoreConfig
from app.feature.digipos.sch_digipos import DigiposRequestList, DigiposTrxRequestBase
from loguru import logger


class DigiposUrlBuilder:
    """Service untuk build URL request ke Digipos API."""

    def __init__(self, digipos_config: DigiposCoreConfig):
        """Initialize dengan config digipos."""
        self.config = digipos_config
        self.base_url = digipos_config.API_BASEURL

    def build_list_url(self, request: DigiposRequestList) -> str:
        """Build URL untuk action=list (list_paket endpoint).

        Args:
            request: DigiposRequestList object

        Returns:
            str: Complete URL untuk digipos API

        Example:
            Input: action=list&product=DATA&dest=081295221639&refid=12321
            Output: http://10.0.0.3:10003/list_paket?username=WIR6289504&json=1&category=DATA&to=081295221639&trxid=12321&payment_method=LINKAJA
        """
        logger.debug(f"Building list URL for memberid: {request.memberid}")

        # Base endpoint untuk list action
        endpoint = "list_paket"

        # Build query parameters
        params = self._build_base_params(request)

        # WAJIB: payment_method=LINKAJA untuk list_paket
        params["payment_method"] = "LINKAJA"

        # Add markup mapping
        if request.markup != 0:  # Only add if not default value
            params["up_harga"] = request.markup

        # Add list-specific parameters
        if request.minday is not None:
            params["min_hari"] = request.minday  # Mapping minday ke min_hari

        if request.maxday is not None:
            params["max_hari"] = request.maxday  # Mapping maxday ke max_hari

        # Default columns untuk list response
        params["kolom"] = "productId,productSubCategory,productName,Duration,total_"

        # Build complete URL (ensure no double slashes)
        base_url_clean = self.base_url.rstrip("/")
        url = f"{base_url_clean}/{endpoint}?{urlencode(params)}"

        logger.info(f"Built list URL: {url}")
        return url

    def build_check_url(self, request: DigiposTrxRequestBase) -> str:
        """Build URL untuk action=check (placeholder for future).

        Args:
            request: DigiposTrxRequestBase object

        Returns:
            str: Complete URL untuk digipos API
        """
        logger.debug(f"Building check URL for memberid: {request.memberid}")

        # Base endpoint untuk check action
        endpoint = "paket"

        # Build query parameters
        params = self._build_base_params(request)
        params["check"] = "1"  # Check action indicator

        # Build complete URL
        url = f"{self.base_url}/{endpoint}?{urlencode(params)}"

        logger.info(f"Built check URL: {url}")
        return url

    def build_buy_url(self, request: DigiposTrxRequestBase) -> str:
        """Build URL untuk action=buy (placeholder for future).

        Args:
            request: DigiposTrxRequestBase object

        Returns:
            str: Complete URL untuk digipos API
        """
        logger.debug(f"Building buy URL for memberid: {request.memberid}")

        # Base endpoint untuk buy action
        endpoint = "paket"

        # Build query parameters
        params = self._build_base_params(request)
        # Buy tidak butuh parameter tambahan, langsung eksekusi

        # Build complete URL
        url = f"{self.base_url}/{endpoint}?{urlencode(params)}"

        logger.info(f"Built buy URL: {url}")
        return url

    def _build_base_params(self, request: DigiposTrxRequestBase) -> dict[str, Any]:
        """Build base parameters yang sama untuk semua request.

        Args:
            request: DigiposTrxRequestBase object

        Returns:
            Dict[str, Any]: Base parameters untuk digipos API
        """
        params = {
            "username": self.config.API_USERNAME,  # Fixed credential
            "json": "1",  # Always request JSON response
            "category": request.product,  # product -> category mapping
            "to": request.dest,  # dest -> to mapping
            "trxid": request.refid,  # refid -> trxid mapping
        }

        # Note: payment_method ditambahkan secara spesifik di masing-masing method
        # karena requirement berbeda per action (list=LINKAJA, check/buy=?)

        return params

    def get_endpoint_from_action(self, action: str) -> str:
        """Get digipos endpoint from action type.

        Args:
            action: Action type (list, check, buy)

        Returns:
            str: Digipos endpoint name
        """
        action_mapping = {"list": "list_paket", "check": "paket", "buy": "paket"}

        endpoint = action_mapping.get(action.lower())
        if not endpoint:
            raise ValueError(f"Unsupported action: {action}")

        logger.debug(f"Mapped action '{action}' to endpoint '{endpoint}'")
        return endpoint
