"""common standardized and work for future development."""

from pydantic import BaseModel, ConfigDict, Field


class ReqClientConfig(BaseModel):
    """biarkan tiap subclass mengatur config masing-masing.

    sengaja di buat place holder for future development.
    """

    pass


class ReqClientBase(ReqClientConfig):
    """Setiap Request masuk dari client untuk Transaksi."""

    memberid: str = Field(
        description="memberid yang terdaftar di service",
        examples=["member123", "member456"],
    )
    product: str = Field(
        description="Kategori produk yang valid, setiap service memilki daftar produk masing-masing",
    )
    dest: str = Field(
        description="ini adalah phone number / voucher number di assign as str , tapi validasi dasar adalah angka",
        examples=["dest123", "dest456"],
        pattern=r"^\d+$",
    )
    sign: str | None = Field(
        default=None,
        description="Signature dari otomax untuk verifikasi request, optional.",
    )
    pin: str | None = Field(
        default=None,
        description="PIN untuk otentikasi tambahan, optional.",
    )
    password: str | None = Field(
        default=None,
        description="Password untuk otentikasi tambahan, optional.",
    )

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)


# SABAR Lakukan Satu Per Satu , Make Sure Dulu Semua Udah Clean, baru Jalan Lagi.


# class ClientResConfig(BaseModel):
#     pass


# class ClientRespBase(ClientResConfig):
#     pass


# # class ClientResponse(GenericModel, Generic[T]):
# #     """Schema respons standar untuk semua output dari API ini."""

# #     success: bool = Field(..., description="Menandakan apakah request berhasil diproses.")
# #     data: T | None = Field(None, description="Berisi data payload jika request sukses.")
# #     error: str | None = Field(None, description="Berisi pesan error jika request gagal.")
