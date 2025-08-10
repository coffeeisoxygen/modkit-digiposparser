"""Base Request dan Params Untuk Endpoint Digipos."""

from enum import StrEnum

from app.schemas.sch_request import ReqClientBase
from pydantic import field_validator


class DigposActionEnum(StrEnum):
    """Enum untuk action yang valid pada endpoint Digipos."""

    LIST = "list"
    CHECK = "check"
    BUY = "buy"


class DigiposCatAsProdEnum(StrEnum):
    """Kategori yang valid untuk endpoint list paket Digipos."""

    DATA = "DATA"
    VOICE_SMS = "VOICE_SMS"
    DIGITAL_OTHER = "DIGITAL_OTHER"
    DIGITAL_MUSIC = "DIGITAL_MUSIC"
    DIGITAL_GAME = "DIGITAL_GAME"
    ROAMING = "ROAMING"
    VF = "VF"
    BYU = "BYU"
    HVC_DATA = "HVC_DATA"
    HVC_VOICE_SMS = "HVC_VOICE_SMS"


class DigiposListRequest(ReqClientBase):
    """Request model untuk endpoint list paket Digipos."""

    product: str
    action: str

    # future field and feature
    up_harga: float | None = None
    minday: int | None = None
    maxday: int | None = None

    @field_validator("product")
    @classmethod
    def validate_product_enum(cls, v: str) -> str:
        """Validate product field against DigiposCatAsProdEnum."""
        if v not in [e.value for e in DigiposCatAsProdEnum]:
            raise ValueError(
                f"product must be one of: {[e.value for e in DigiposCatAsProdEnum]}"
            )
        return v

    @field_validator("action")
    @classmethod
    def validate_action_enum(cls, v: str) -> str:
        """Validate action field against DigposActionEnum."""
        if v not in [e.value for e in DigposActionEnum]:
            raise ValueError(
                f"action must be one of: {[e.value for e in DigposActionEnum]}"
            )
        return v

    @field_validator("up_harga")
    @classmethod
    def validate_up_harga(cls, v: float | None) -> float | None:
        """Validate up_harga if provided."""
        if v is not None and v < 0:
            raise ValueError("up_harga must be >= 0")
        return v

    @field_validator("minday")
    @classmethod
    def validate_minday(cls, v: int | None) -> int | None:
        """Validate minday if provided."""
        if v is not None and v < 0:
            raise ValueError("minday must be >= 0")
        return v

    @field_validator("maxday")
    @classmethod
    def validate_maxday(cls, v: int | None) -> int | None:
        """Validate maxday if provided."""
        if v is not None and v < 0:
            raise ValueError("maxday must be >= 0")
        return v
