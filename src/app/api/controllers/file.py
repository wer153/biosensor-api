import uuid
from litestar import Controller, Request, post, get, delete
from litestar.di import Provide
from litestar.exceptions import NotFoundException, InternalServerException, PermissionDeniedException
from litestar.security.jwt import Token
from app.db.models.file import FileModel, UploadStatus
from app.api.schemas.file import (
    FileInfo,
    FileListResponse,
    FileDownloadResponse,
    FileDeleteResponse,
    PresignedUploadRequest,
    PresignedUploadResponse,
    S3WebhookEvent,
)
from app.db.repositories.file import FileRepository, provide_files_repo
from app.services.s3_service import s3_service
from app.auth.jwt import AuthUser
from typing import Any
from datetime import datetime, timedelta

_PRESIGNED_URL_EXPIRY_SECONDS = 60


class FileController(Controller):
    path = "/files"
    dependencies = {"files_repo": Provide(provide_files_repo)}
    tags = ["files"]


    @get("/")
    async def get_files(
        self,
        request: Request[AuthUser, Token, Any],
        files_repo: FileRepository,
    ) -> FileListResponse:
        user_id = request.user.id
        files = await files_repo.get_user_files(files_repo.session, user_id)

        file_infos = [
            FileInfo(
                id=str(file.id),
                filename=file.filename,
                original_filename=file.original_filename,
                content_type=file.content_type,
                file_size=file.file_size,
                upload_date=file.upload_date,
                uploaded_by=str(file.uploaded_by),
            )
            for file in files
        ]

        return FileListResponse(files=file_infos, total_count=len(file_infos))

    @get("/{file_id:str}/download")
    async def download_file(
        self,
        request: Request[AuthUser, Token, Any],
        files_repo: FileRepository,
        file_id: str,
    ) -> FileDownloadResponse:
        user_id = request.user.id
        file = await files_repo.get_user_file_by_id(
            files_repo.session, file_id, user_id
        )

        if not file:
            raise NotFoundException("File not found")

        try:
            download_url = s3_service.generate_presigned_url(
                file.s3_key, expires_in=_PRESIGNED_URL_EXPIRY_SECONDS
            )
        except InternalServerException as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "404" in error_msg:
                raise NotFoundException(f"File not available for download: {file.original_filename}")
            elif "access denied" in error_msg.lower() or "403" in error_msg:
                raise PermissionDeniedException(f"Access denied to file: {file.original_filename}")
            else:
                raise InternalServerException(f"Download currently unavailable: {file.original_filename}")

        expires_at = datetime.utcnow() + timedelta(
            seconds=_PRESIGNED_URL_EXPIRY_SECONDS
        )

        return FileDownloadResponse(
            download_url=download_url,
            expires_at=expires_at,
            filename=file.original_filename,
        )

    @delete("/{file_id:str}", status_code=200)
    async def delete_file(
        self,
        request: Request[AuthUser, Token, Any],
        files_repo: FileRepository,
        file_id: str,
    ) -> FileDeleteResponse:
        user_id = request.user.id
        success = await files_repo.soft_delete_file(
            files_repo.session, file_id, user_id
        )

        if not success:
            raise NotFoundException("File not found")

        return FileDeleteResponse(
            message="File removed from list successfully", deleted_file_id=file_id
        )

    @post("/upload/presigned")
    async def get_presigned_upload_url(
        self,
        request: Request[AuthUser, Token, Any],
        files_repo: FileRepository,
        data: PresignedUploadRequest,
    ) -> PresignedUploadResponse:
        """Get presigned URL for direct S3 upload (better for large files)"""
        user_id = request.user.id

        # Pre-create file record with PENDING status (file_size will be updated after upload)
        file_model = FileModel(
            id=uuid.uuid4(),
            filename=data.filename,
            original_filename=data.filename,
            content_type=data.content_type,
            file_size=0,  # Will be updated after upload
            s3_key="",  # Will be updated after S3 key generation
            s3_bucket=s3_service.bucket_name,
            uploaded_by=user_id,
            upload_date=datetime.utcnow(),
            upload_status=UploadStatus.PENDING,
        )
        
        # Save to get the file ID first
        
        # Generate S3 key and presigned URL using the file ID
        upload_url, s3_key = s3_service.generate_presigned_upload_url(
            file_id=str(file_model.id),
            user_id=user_id,
            original_filename=data.filename,
            content_type=data.content_type,
            expires_in=_PRESIGNED_URL_EXPIRY_SECONDS,
        )

        # Update the file record with the S3 key
        file_model.s3_key = s3_key
        await files_repo.add(file_model, auto_commit=True)

        expires_at = datetime.utcnow() + timedelta(
            seconds=_PRESIGNED_URL_EXPIRY_SECONDS
        )

        return PresignedUploadResponse(
            upload_url=upload_url,
            s3_key=s3_key,
            expires_at=expires_at,
            file_id=str(file_model.id),  # Return file ID for webhook
        )

    @post("/webhook/s3-upload", exclude_from_auth=True)
    async def s3_upload_webhook(
        self,
        files_repo: FileRepository,
        events: list[S3WebhookEvent],
    ) -> dict[str, str]:
        """Webhook endpoint for S3 upload completion notifications"""
        for event in events:
            if event.eventName.startswith("ObjectCreated"):
                s3_key = event.s3["object"]["key"]
                file_size = event.s3["object"]["size"]
                # Find and update the file record
                file_record = await files_repo.get_by_s3_key(s3_key)
                if file_record:
                    file_record.upload_status = UploadStatus.COMPLETED
                    file_record.file_size = file_size
                    await files_repo.session.commit()
        return {"status": "processed"}
