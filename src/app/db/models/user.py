from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Index
from litestar.plugins.sqlalchemy import base


class UserModel(base.UUIDAuditBase):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))

    __table_args__ = (
        Index('idx_users_email', 'email'),
    )

    def set_password(self, password: str) -> None:
        # TODO: hash password
        self.password = password

    def verify_password(self, password: str) -> bool:
        return password == self.password
