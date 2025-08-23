from litestar import Controller
from litestar.di import Provide
from litestar.handlers.http_handlers.decorators import get, post, patch, delete
from app.db.models.user import UserModel
from app.api.schemas.user import User, UserCreate, UserUpdate
from app.db.repositories.user import UserRepository, provide_users_repo


class UserController(Controller):
    path = "/users"
    dependencies = {"users_repo": Provide(provide_users_repo)}

    @get("/")
    async def list_users(self, users_repo: UserRepository) -> list[User]:
        users = await users_repo.list()
        return [User(name=user.name, email=user.email) for user in users]

    @post("/")
    async def create_user(
        self,
        users_repo: UserRepository,
        data: UserCreate,
    ) -> User:
        user_model = UserModel(**data.model_dump())
        await users_repo.add(user_model, auto_commit=True)
        return User(name=data.name, email=data.email)

    @get("/{email:str}")
    async def get_user(self, users_repo: UserRepository, email: str) -> User:
        user = await users_repo.get(email)
        return User(name=user.name, email=user.email)

    @patch("/{email:str}")
    async def update_user(
        self, users_repo: UserRepository, email: str, data: UserUpdate
    ) -> User:
        user = UserModel(
            email=email,
            name=data.name,
        )
        await users_repo.update(
            user,
            id_attribute=UserModel.email,
            auto_commit=True,
        )
        return User(name=data.name, email=data.email)

    @delete("/{email:str}")
    async def delete_user(self, users_repo: UserRepository, email: str) -> None:
        await users_repo.delete(email, id_attribute=UserModel.email, auto_commit=True)
