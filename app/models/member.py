from sqlalchemy import Integer, String,Mapped
from app.db.base import Base


class Member(Base):
    __tablename__ = "members"

    id = Mapped(Integer, primary_key=True, index=True)
    name = Mapped(String, index=True)
    email = Mapped(String, unique=True, index=True)
    phone_number = Mapped(String, unique=True, index=True)

    def __repr__(self):
        return f"<Member(id={self.id}, name={self.name}, email={self.email})>"
