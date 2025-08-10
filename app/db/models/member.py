from app.db.setup.base import Base
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

# NOTE: validasi di lakukan di level pyndatic.


class Member(Base):
    __tablename__ = "members"

    memberid: Mapped[str] = mapped_column(String(10), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    ipaddress: Mapped[str] = mapped_column(String(), unique=True)
    report_url: Mapped[str] = mapped_column(String(), unique=True)
    pin: Mapped[str] = mapped_column(String())
    password: Mapped[str] = mapped_column(String(50))
    allow_nosign: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<Member(memberid={self.memberid}, name={self.name}, ipaddress={self.ipaddress}, report_url={self.report_url}, pin={self.pin}, password={self.password}, allow_nosign={self.allow_nosign}, is_active={self.is_active})>"
