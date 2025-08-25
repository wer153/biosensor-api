from pydantic import BaseModel
from datetime import datetime


class FileInfo(BaseModel):
    id: str
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    upload_date: datetime
    uploaded_by: str


class FileUploadResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    message: str


class FileListResponse(BaseModel):
    files: list[FileInfo]
    total_count: int


class FileDownloadResponse(BaseModel):
    download_url: str
    expires_at: datetime
    filename: str


class FileDeleteResponse(BaseModel):
    message: str
    deleted_file_id: str


class PresignedUploadRequest(BaseModel):
    filename: str
    content_type: str


class PresignedUploadResponse(BaseModel):
    upload_url: str
    s3_key: str
    expires_at: datetime
    file_id: str
    fields: dict[str, str] | None = None


class UploadConfirmRequest(BaseModel):
    s3_key: str
    filename: str
    content_type: str
    file_size: int


class S3ObjectInfo(BaseModel):
    key: str
    size: int

class S3Info(BaseModel):
    object: S3ObjectInfo

class S3WebhookEvent(BaseModel):
    """S3 Event Notification webhook payload"""
    
    eventSource: str
    eventName: str
    s3: S3Info
