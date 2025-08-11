from app.models import Base
from sqlalchemy import Boolean, Column, String


class Member(Base):
    __tablename__ = "members"

    memberid = Column(String(32), primary_key=True, nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    pin = Column(String(64), nullable=False)  # Store as string, not SecretStr
    password = Column(String(128), nullable=False)  # Store as string, not SecretStr
    is_active = Column(Boolean, default=True, nullable=False)
    ipaddress = Column(String(15), nullable=False)  # IPv4 as string
    report_url = Column(String(255), nullable=False)
    allow_nosign = Column(Boolean, default=False, nullable=False)
