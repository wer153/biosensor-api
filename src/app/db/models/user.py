from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Index
from litestar.plugins.sqlalchemy import base
from typing import TYPE_CHECKING, List

from app.services.password_service import password_service

if TYPE_CHECKING:
    from .file import FileModel


class UserModel(base.UUIDAuditBase):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))

    files: Mapped[List["FileModel"]] = relationship("FileModel", back_populates="user")

    __table_args__ = (Index("idx_users_email", "email"),)

    def set_password(self, password: str) -> None:
        self.password = password_service.hash_password(password)

    def verify_password(self, password: str) -> bool:
        return password_service.verify_password(password, self.password)
