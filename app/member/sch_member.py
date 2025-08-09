from pydantic import AnyHttpUrl, BaseModel, Field, SecretStr, field_validator


class MemberInDB(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "json_schema_extra": {
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
    }
    memberid: str = Field(..., description="ID unik untuk member")
    name: str = Field(..., description="Nama member")
    pin: SecretStr = Field(..., description="PIN untuk member")
    password: SecretStr = Field(..., description="Password untuk member")
    is_active: bool = Field(default=True, description="Status keaktifan member")
    ip_address: str = Field(..., alias="ipaddress", description="Alamat IP member")
    report_url: AnyHttpUrl = Field(..., description="URL untuk laporan member")
    allow_nosign: bool = Field(
        default=False,
        description="Apakah member diizinkan untuk hit tanpa Signature(ini Biasanya Otomax Signature)",
    )

    # Pydantic V2 config
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }

    @field_validator("pin", mode="before")
    @classmethod
    def validate_pin(cls, value: str) -> str:
        """Validasi pin."""
        # Accept int or str, convert to str for validation
        value_str = str(value)
        if not value_str.isdigit() or len(value_str) != 4:
            raise ValueError("PIN must be a 4-digit number")
        return value_str

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Validasi password."""
        # Accept int or str, convert to str for validation
        value_str = str(value)
        if len(value_str) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value_str

    @field_validator("memberid", mode="before")
    @classmethod
    def validate_memberid(cls, value: str) -> str:
        """Validasi memberid."""
        value_str = str(value)
        if not value_str.isalnum() or len(value_str) < 5:
            raise ValueError("Member ID must be alphanumeric and at least 5 characters")
        return value_str

    @field_validator("ip_address", mode="before")
    @classmethod
    def validate_ip_address(cls, value: str) -> str:
        """Validasi alamat IP."""
        value_str = str(value)
        parts = value_str.split(".")
        if len(parts) != 4:
            raise ValueError("IP address must be in the format 'X.X.X.X'")
        for part in parts:
            if not part.isdigit() or not (0 <= int(part) <= 255):
                raise ValueError(
                    "Each part of the IP address must be a number between 0 and 255"
                )
        return value_str

    @field_validator("report_url", mode="before")
    @classmethod
    def validate_report_url(cls, value: str) -> str:
        """Validasi URL laporan."""
        value_str = str(value)
        if not value_str.startswith("http://") and not value_str.startswith("https://"):
            raise ValueError("Report URL must start with 'http://' or 'https://'")
        return value_str
