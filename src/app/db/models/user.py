from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from litestar.plugins.sqlalchemy import base


class UserModel(base.UUIDAuditBase):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
