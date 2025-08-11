from typing import TYPE_CHECKING

from app.models import Base
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .product import Product


class Provider(Base):
    """grouping product dan related dsini."""

    __tablename__ = "providers"

    code: Mapped[str] = mapped_column(
        String(100), primary_key=True, nullable=False, unique=True
    )
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
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
    products: Mapped[list["Product"]] = relationship(
        "Product",  # <-- harus "Product" bukan "Products"
        back_populates="provider",
        cascade="all, delete-orphan",
    )
