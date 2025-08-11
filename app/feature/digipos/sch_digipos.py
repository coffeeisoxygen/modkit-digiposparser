"""containing all schemas related to digipos.

Architecture:
- Base authentication: MemberTrxRequestModel dari sch_member.py
- Domain composition: DigiposTrxRequestBase extends base + digipos-specific validation
- Action-specific models: List/Check/Buy dengan field tambahan sesuai kebutuhan

Planned endpoints:
1-digipos/trx?action=list&product=DATA&up_harga=<up_harga>&minday=<minday>&maxday=<maxday>
2-digipos/trx?action=check&product=DATA&product_id=<product_id>&up_harga=<up_harga>
3-digipos/trx?action=buy&product=DATA&product_id=<product_id>&up_harga=<up_harga>
"""

from enum import StrEnum
from typing import Annotated

from app.feature.member.sch_member import MemberTrxRequestModel
from pydantic import BeforeValidator, Field, field_validator, model_validator


def validate_non_negative(v: int | None) -> int | None:
    """Validator untuk memastikan nilai adalah non-negatif (>= 0)."""
    if v is not None and v < 0:
        raise ValueError("value must be >= 0")
    return v


NonNegativeInt = Annotated[int | None, BeforeValidator(validate_non_negative)]


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


class DigiposTrxRequestBase(MemberTrxRequestModel):
    """Request model untuk endpoint transaksi Digipos.

    Inherit dari MemberTrxRequestModel untuk authentication dan base payload.
    Override product validation untuk domain digipos dan tambah field spesifik.

    Additional fields:
        action: DigposActionEnum - action to be performed
        markup: int | None - markup dapat berupa decimal atau integer

    Inherited fields dari MemberTrxRequestModel:
        memberid, product, dest, refid, sign, pin, password
    """

    action: DigposActionEnum = Field(
        description="Action to be performed", examples=["list", "check", "buy"]
    )
    markup: int | None = Field(
        default=0, description="Markup can be decimal or integer"
    )

    @field_validator("product")
    @classmethod
    def validate_product_enum(cls, v: str) -> str:
        """Validate product field against DigiposCatAsProdEnum."""
        if v not in [e.value for e in DigiposCatAsProdEnum]:
            raise ValueError(
                f"product must be one of: {[e.value for e in DigiposCatAsProdEnum]}"
            )
        return v


class DigiposRequestList(DigiposTrxRequestBase):
    """Request model untuk list paket dengan filter opsional."""

    action: DigposActionEnum = DigposActionEnum.LIST

    # future features - all optional with default None
    minday: NonNegativeInt = None
    maxday: NonNegativeInt = None
    minprice: NonNegativeInt = None
    maxprice: NonNegativeInt = None

    # Validator untuk memvalidasi hubungan antar field
    @model_validator(mode="after")
    def validate_range(self) -> "DigiposRequestList":
        # Logika ini masih perlu, karena memeriksa dua field sekaligus
        if (
            self.minday is not None
            and self.maxday is not None
            and self.minday > self.maxday
        ):
            raise ValueError("minday must be <= maxday")
        if (
            self.minprice is not None
            and self.maxprice is not None
            and self.minprice > self.maxprice
        ):
            raise ValueError("minprice must be <= maxprice")
        return self


class DigiposRequestCheck(DigiposTrxRequestBase):
    """Request model untuk check produk spesifik."""

    action: DigposActionEnum = DigposActionEnum.CHECK
    productid: str = Field(description="Product ID to check")


class DigiposRequestBuy(DigiposTrxRequestBase):
    """Request model untuk buy produk spesifik."""

    action: DigposActionEnum = DigposActionEnum.BUY
    productid: str = Field(description="Product ID to buy")
