"""model untuk modul, seperti digipos, isimple sidompul dan lain lain."""


from app.db.base import Base
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column


class Modules(Base):
    __tablename__ = "modules"

    moduleid: Mapped[str] = mapped_column(String(10), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<Modules(moduleid={self.moduleid}, name={self.name}, description={self.description}, is_active={self.is_active})>"
