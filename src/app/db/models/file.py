from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Index, ForeignKey, DateTime
from litestar.plugins.sqlalchemy import base
from datetime import datetime
from typing import TYPE_CHECKING
from enum import StrEnum

if TYPE_CHECKING:
    from .user import UserModel


class UploadStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class FileModel(base.UUIDAuditBase):
    __tablename__ = "files"

    filename: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    file_size: Mapped[int] = mapped_column()
    s3_key: Mapped[str] = mapped_column(String(500))
    s3_bucket: Mapped[str] = mapped_column(String(100))
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    upload_status: Mapped[str] = mapped_column(String(20), default="pending")
    is_deleted: Mapped[bool] = mapped_column(default=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="files")

    __table_args__ = (
        Index("idx_files_uploaded_by", "uploaded_by"),
        Index("idx_files_s3_key", "s3_key"),
        Index("idx_files_is_deleted", "is_deleted"),
        Index("idx_files_upload_status", "upload_status"),
    )
