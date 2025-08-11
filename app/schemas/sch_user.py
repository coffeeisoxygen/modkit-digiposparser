from app.schemas.sch_user_validation import (
    NameUserIsAlpha,
    PasswordIsStrong,
    UserNameIsAlNum,
)
from pydantic import BaseModel, Field, field_validator

# TODO : nanti klo udah beres , beres beres description, example sama json schema


class UserConfig(BaseModel):
    model_config = {
        "extra": "forbid",
        "from_attributes": True,
    }


class UserBase(BaseModel):
    """Base model untuk User, ini tidak ada validasi khusus."""

    username: UserNameIsAlNum = Field(..., max_length=64)
    name: NameUserIsAlpha = Field(..., max_length=100)


class UserAdminSeed(UserConfig, UserBase):
    """ini buat seeding Admin

    saat pertama kali tidak di temukan is_superuser / username admin.
    di lakukan di service layer.
    Atau Ini Kklo Admin Mau Seed User.
    """

    password: PasswordIsStrong = Field(
        description="Password must be strong", min_length=1
    )
    is_superuser: bool = Field(default=True)
    is_active: bool = Field(default=True)


class UserLogin(UserConfig):
    """ini buat login user

    hanya membutuhkan username dan password, tidak ada validasi khusus.
    karens ini hanya check ke database,
    klo di validasi isAlnum ketebak nanti inputnya , jadi pattern ketebak
    biar ngga ketebak , kita buat validasi khusus , input tidak bileh ada spesial chars.
    """

    username: UserNameIsAlNum = Field(..., max_length=64)
    password: PasswordIsStrong = Field(..., min_length=1)


class PasswordChange(UserConfig):
    password: PasswordIsStrong = Field(description="Old password", min_length=1)
    new_password: PasswordIsStrong = Field(
        description="New password must be strong", min_length=1
    )

    @field_validator("new_password")
    @classmethod
    def check_new_password(cls, v, info):  # noqa: ANN001, ANN206
        if v == info.data.get("password"):
            raise ValueError("New password must be different from old password")
        return v


class UserRead(BaseModel):
    """buat user Non Admin retrive data."""

    username: str
    name: str
    is_active: bool
    created_at: str
    updated_at: str


class UserAdminRead(BaseModel):
    """buat admin retrive data."""

    id: int
    username: str
    name: str
    is_superuser: bool
    is_active: bool
    created_at: str
    updated_at: str
