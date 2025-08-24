from litestar import Controller, Request, post, get, delete
from litestar.di import Provide
from litestar.exceptions import NotFoundException, InternalServerException
from litestar.datastructures import UploadFile
from litestar.security.jwt import Token
from app.db.models.file import FileModel
from app.api.schemas.file import (
    FileInfo,
    FileUploadResponse,
    FileListResponse,
    FileDownloadResponse,
    FileDeleteResponse,
)
from app.db.repositories.file import FileRepository, provide_files_repo
from app.services.s3_service import s3_service
from app.auth.jwt import AuthUser
from typing import Annotated, Any
from datetime import datetime
from litestar.enums import RequestEncodingType
from litestar.params import Body
from io import BytesIO


class FileController(Controller):
    path = "/files"
    dependencies = {"files_repo": Provide(provide_files_repo)}
    tags = ["files"]

    @post("/upload")
    async def upload_files(
        self,
        request: Request[AuthUser, Token, Any],
        files_repo: FileRepository,
        data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
    ) -> FileUploadResponse:
        if not data:
            raise InternalServerException("No file provided")

        user_id = request.user.id
        
        file_content = await data.read()
        file_size = len(file_content)
        file_obj = BytesIO(file_content)

        s3_key, s3_bucket = await s3_service.upload_file(
            file_content=file_obj,
            user_id=user_id,
            original_filename=data.filename,
            content_type=data.content_type or "application/octet-stream",
        )

        file_model = FileModel(
            filename=data.filename,
            original_filename=data.filename,
            content_type=data.content_type or "application/octet-stream",
            file_size=file_size,
            s3_key=s3_key,
            s3_bucket=s3_bucket,
            uploaded_by=user_id,
            upload_date=datetime.utcnow(),
        )

        await files_repo.add(file_model, auto_commit=True)

        return FileUploadResponse(
            id=str(file_model.id),
            filename=file_model.filename,
            original_filename=file_model.original_filename,
            content_type=file_model.content_type,
            file_size=file_model.file_size,
            message="File uploaded successfully",
        )

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

        download_url = s3_service.generate_presigned_url(file.s3_key, expires_in=60)

        return FileDownloadResponse(
            download_url=download_url, expires_in=60, filename=file.original_filename
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
