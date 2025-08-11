from app.models import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ApiCommand(Base):
    __tablename__ = "apicommands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    product_code: Mapped[str] = mapped_column(
        String(100), ForeignKey("products.code"), nullable=False
    )
    module_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("modules.id"), nullable=False
    )

    command_template: Mapped[str] = mapped_column(String(1000), nullable=False)
    # contoh: "list_paket?username=[username]&to=[to]&trxid=[trxid]&category=[category]"

    description: Mapped[str] = mapped_column(String(255), nullable=True)
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

    # relasi opsional untuk kemudahan query
    product = relationship("Product", back_populates="api_commands")
    module = relationship("Module")


# Jangan lupa di Product tambahin:
# api_commands: Mapped[list["ApiCommand"]] = relationship("ApiCommand", back_populates="product")
