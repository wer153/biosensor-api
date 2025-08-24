from typing import List, Optional
from litestar.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models.file import FileModel


class FileRepository(SQLAlchemyAsyncRepository[FileModel]):
    model_type = FileModel

    async def get_user_files(
        self, 
        session: AsyncSession, 
        user_id: str, 
        include_deleted: bool = False
    ) -> List[FileModel]:
        stmt = select(FileModel).where(FileModel.uploaded_by == user_id)
        if not include_deleted:
            stmt = stmt.where(~FileModel.is_deleted)
        stmt = stmt.order_by(FileModel.upload_date.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_file_by_id(
        self, 
        session: AsyncSession, 
        file_id: str, 
        user_id: str
    ) -> Optional[FileModel]:
        stmt = select(FileModel).where(
            and_(
                FileModel.id == file_id,
                FileModel.uploaded_by == user_id,
                ~FileModel.is_deleted
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete_file(
        self, 
        session: AsyncSession, 
        file_id: str, 
        user_id: str
    ) -> bool:
        file_model = await self.get_user_file_by_id(session, file_id, user_id)
        if file_model:
            file_model.is_deleted = True
            await session.commit()
            return True
        return False


async def provide_files_repo(db_session: AsyncSession) -> FileRepository:
    return FileRepository(session=db_session)