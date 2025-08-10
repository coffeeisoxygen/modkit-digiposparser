"""containing all schmeas related to digipos.

Later akan di improve.
plant endpoint (below are example Only):
1-digipos/trx?action=list&product=DATA&up_harga=<up_harga>&minday=<minday>&maxday=<maxday>
2-digipos/trx?action=check&product=DATA&product_id=<product_id>&up_harga=<up_harga>
3-digipos/trx?action=buy&product=DATA&product_id=<product_id>&up_harga=<up_harga>
"""

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


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
        description="Action to be performed, exol",
        examples=["list", "check", "buy"]
    )
    product: str = Field(
        description="Product category",
        examples=["DATA", "VOICE_SMS", "DIGITAL_OTHER"]
    )
    markup: float | None = Field(
        default=0, description="Markup can be decimal or integer"
    )

    @field_validator("action")
    @classmethod
    def validate_action_enum(cls, v: str) -> str:
        """Validate action field against DigposActionEnum."""
        if v not in [e.value for e in DigposActionEnum]:
            raise ValueError(
                f"action must be one of: {[e.value for e in DigposActionEnum]}"
            )
        return v

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
    pass


class DigiposRequestCheck(DigiposTrxRequestBase):
    pass


class DigiposRequestBuy(DigiposTrxRequestBase):
    pass


# class DigiposListRequest(ReqClientBase):
#     """Request model untuk endpoint list paket Digipos."""

#     product: str
#     action: str

#     # future field and feature
#     up_harga: float | None = None
#     minday: int | None = None
#     maxday: int | None = None

#     @field_validator("product")
#     @classmethod
#     def validate_product_enum(cls, v: str) -> str:
#         """Validate product field against DigiposCatAsProdEnum."""
#         if v not in [e.value for e in DigiposCatAsProdEnum]:
#             raise ValueError(
#                 f"product must be one of: {[e.value for e in DigiposCatAsProdEnum]}"
#             )
#         return v


#     @field_validator("up_harga")
#     @classmethod
#     def validate_up_harga(cls, v: float | None) -> float | None:
#         """Validate up_harga if provided."""
#         if v is not None and v < 0:
#             raise ValueError("up_harga must be >= 0")
#         return v

#     @field_validator("minday")
#     @classmethod
#     def validate_minday(cls, v: int | None) -> int | None:
#         """Validate minday if provided."""
#         if v is not None and v < 0:
#             raise ValueError("minday must be >= 0")
#         return v

#     @field_validator("maxday")
#     @classmethod
#     def validate_maxday(cls, v: int | None) -> int | None:
#         """Validate maxday if provided."""
#         if v is not None and v < 0:
#             raise ValueError("maxday must be >= 0")
#         return v
