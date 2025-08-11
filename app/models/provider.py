from typing import TYPE_CHECKING

from app.models import Base
from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .product import Product


class Provider(Base):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    products: Mapped[list["Product"]] = relationship(
        "Product",  # <-- harus "Product" bukan "Products"
        back_populates="provider",
        cascade="all, delete-orphan",
    )
