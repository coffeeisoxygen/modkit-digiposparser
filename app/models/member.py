from app.models import Base
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column


class Member(Base):
    __tablename__ = "members"

    memberid: Mapped[str] = mapped_column(
        String(32), primary_key=True, nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    pin: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # Store as string, not SecretStr
    password: Mapped[str] = mapped_column(
        String(128), nullable=False
    )  # Store as string, not SecretStr
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ipaddress: Mapped[str] = mapped_column(String(15), nullable=False)  # IPv4 as string
    report_url: Mapped[str] = mapped_column(String(255), nullable=False)
    allow_nosign: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
