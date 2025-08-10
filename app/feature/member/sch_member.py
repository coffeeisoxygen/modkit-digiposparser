# File: src/schemas/member_schema.py
import ipaddress

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
)


class MemberInDB(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "memberid": "M12345",
                "name": "John Doe",
                "pin": "1234",
                "password": "password",
                "is_active": True,
                "ipaddress": "192.168.1.1",
                "report_url": "http://example.com/report",
                "allow_nosign": False,
            }
        },
    )

    memberid: str = Field(
        ..., description="ID unik untuk member", min_length=5, pattern=r"^[a-zA-Z0-9]*$"
    )
    name: str = Field(..., description="Nama member", max_length=100)
    pin: SecretStr = Field(..., description="PIN untuk member", min_length=6)
    password: SecretStr = Field(..., description="Password untuk member", min_length=6)
    is_active: bool = Field(default=True, description="Status keaktifan member")
    ip_address: ipaddress.IPv4Address = Field(
        ..., alias="ipaddress", description="Alamat IP member"
    )
    report_url: AnyHttpUrl = Field(..., description="URL untuk laporan member")
    allow_nosign: bool = Field(
        default=False,
        description="Apakah member diizinkan untuk hit tanpa Signature.",
    )

    @field_validator("pin", "password", mode="before")
    @classmethod
    def validate_secret_fields(cls, v: str | None) -> str:
        if v is None or not v:
            raise ValueError("Field is required")
        if isinstance(v, int):
            return str(v)
        return v


class MemberTrxRequestModel(BaseModel):
    """Request transaksi mentah dari client."""

    memberid: str = Field(..., description="ID unik untuk member")
    pin: str | int | None = Field(None, description="PIN untuk member")
    password: str | int | None = Field(None, description="Password untuk member")
    sign: str | int | None = None
    product: str | int | None = None
    refid: str | int | None = None
