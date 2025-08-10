"""containing all schmeas related to digipos.

Later akan di improve.
plant endpoint (below are example Only):
1-digipos/trx?action=list&product=DATA&up_harga=<up_harga>&minday=<minday>&maxday=<maxday>
2-digipos/trx?action=check&product=DATA&product_id=<product_id>&up_harga=<up_harga>
3-digipos/trx?action=buy&product=DATA&product_id=<product_id>&up_harga=<up_harga>
"""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, field_validator, model_validator


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


class DigiposTrxRequestBase(BaseModel):
    """Request model untuk endpoint transaksi Digipos.

    validasi :
            action harus salah satu dari enums
            product harus salah satu dari enums
    optional:
        up_harga: float | None`
    """

    action: DigposActionEnum = Field(
        description="Action to be performed", examples=["list", "check", "buy"]
    )
    product: str = Field(
        description="Product category", examples=["DATA", "VOICE_SMS", "DIGITAL_OTHER"]
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
    action: DigposActionEnum = DigposActionEnum.LIST

    # future features
    minday: NonNegativeInt
    maxday: NonNegativeInt
    minprice: NonNegativeInt
    maxprice: NonNegativeInt

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
    action: DigposActionEnum = DigposActionEnum.CHECK


class DigiposRequestBuy(DigiposTrxRequestBase):
    action: DigposActionEnum = DigposActionEnum.BUY
    action: DigposActionEnum = DigposActionEnum.BUY
