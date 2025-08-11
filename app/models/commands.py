from app.models import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Apicommand(Base):
    r"""ini adalah junction table antara product dan module

    jadi 1 product bisa memilki beberapa module yang akan handle dia,
    jika di otomax anggap aja ini adalah table parsing.
    """

    __tablename__ = "apicommands"

    product_id: Mapped[str] = mapped_column(
        String(32), primary_key=True, nullable=False
    )
    module_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False
    )
