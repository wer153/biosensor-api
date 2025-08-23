from litestar.plugins.sqlalchemy import repository
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import UserModel


class UserRepository(repository.SQLAlchemyAsyncRepository[UserModel]):
    model_type = UserModel


async def provide_users_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(session=db_session)
