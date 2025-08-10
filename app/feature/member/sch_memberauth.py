# Reminder: Bagian ini yang akan Jadi Diamond
from pydantic import BaseModel, Field


class MemberTrxRequestModel(BaseModel):
    """Model data Yang Di Butuhkan Untuk Transaksi."""

    memberid: str = Field(..., description="ID unik untuk member")
    pin: str | int | None = Field(None, description="PIN untuk member")
    password: str | int | None = Field(None, description="Password untuk member")
    sign: str | int | None = None
    product: str | int | None = None
    refid: str | int | None = None


class MemberTrxAuthModel(MemberTrxRequestModel):
    """Model data Yang Di Butuhkan Untuk Auth."""

    is_active: bool | None = Field(description="Status keaktifan member")
    allow_nosign: bool | None = Field(
        description="Apakah member diizinkan untuk hit tanpa Signature."
    )
