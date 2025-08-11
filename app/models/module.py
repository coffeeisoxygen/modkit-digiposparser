from typing import TYPE_CHECKING

from app.models import Base
from sqlalchemy import JSON, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .commands import ApiCommand


class Module(Base):
    r"""ini tuh nanti nya jadi isimple / digipos dan lain lain \."""

    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    timeout: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    second_wait: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    parameters: Mapped[JSON] = mapped_column(JSON, nullable=True)
    optional_data: Mapped[JSON | None] = mapped_column(
        JSON, nullable=True
    )  # for credential that need to extend
    description: Mapped[str | None] = mapped_column(
        String(), nullable=True
    )  # just descriotions
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    apicommands: Mapped[list["ApiCommand"]] = relationship(
        "ApiCommand", back_populates="module"
    )
