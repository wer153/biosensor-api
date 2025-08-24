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
    expires_in: int
    filename: str


class FileDeleteResponse(BaseModel):
    message: str
    deleted_file_id: str
