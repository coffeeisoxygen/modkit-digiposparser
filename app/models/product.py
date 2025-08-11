from typing import TYPE_CHECKING

from app.models import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .commands import ApiCommand
    from .provider import Provider


class Product(Base):
    """product and related disini juga."""

    __tablename__ = "products"

    code: Mapped[str] = mapped_column(
        String(100), primary_key=True, nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    provider_code: Mapped[str] = mapped_column(
        ForeignKey("providers.code"), nullable=False
    )
    provider: Mapped["Provider"] = relationship("Provider", back_populates="products")

    api_commands: Mapped[list["ApiCommand"]] = relationship(
        "ApiCommand", back_populates="product"
    )
