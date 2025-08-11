# ruff: noqa
# ruff: isort=off
# ruff: F401=off
# pyright: reportUndefinedVariable=false, reportGeneralTypeIssues=false
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# import here for all models.
from app.models.commands import ApiCommand
from app.models.member import Member
from app.models.module import Module
from app.models.product import Product
from app.models.provider import Provider
from app.models.user import User
