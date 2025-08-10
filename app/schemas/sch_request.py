"""common standardized and work for future development."""

from pydantic import BaseModel, ConfigDict


class ReqClientConfig(BaseModel):
    """biarkan tiap subclass mengatur config masing-masing.

    sengaja di buat place holder for future development.
    """

    pass


class ReqClientBase(ReqClientConfig):
    """Base request model : Semua jenis incoming masuk akan seperti ini.

    tapi subclass akan overide ini , karena tiap domain memiliki validasi masing-masing.
    """

    memberid: str  # this is must present klo ini ngga ada ngga valid
    product: str  # overide nanti per domain sesuai validasi masing masing
    action: str  # Overide Nanti Per Domain
    dest: str
    sign: str | None = None
    pin: str | None = None
    password: str | None = None

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
