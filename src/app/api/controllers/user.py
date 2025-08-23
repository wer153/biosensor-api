from litestar import Controller, get, post, patch, delete
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from app.db.models.user import UserModel
from app.api.schemas.user import User, UserCreate, UserUpdate
from app.db.repositories.user import UserRepository, provide_users_repo


class UserController(Controller):
    path = "/users"
    dependencies = {"users_repo": Provide(provide_users_repo)}
    tags = ["users"]

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
        user_model = UserModel(name=data.name, email=str(data.email))
        user_model.set_password(data.password)
        await users_repo.add(user_model, auto_commit=True)
        return User(name=data.name, email=data.email)

    @get("/{email:str}")
    async def get_user(self, users_repo: UserRepository, email: str) -> User:
        user = await users_repo.get_one_or_none(UserModel.email == email)
        if not user:
            raise NotFoundException(status_code=404, detail="User not found")
        return User(name=user.name, email=user.email)

    @patch("/{email:str}")
    async def update_user(
        self, users_repo: UserRepository, email: str, data: UserUpdate
    ) -> User:
        user = await users_repo.get_one_or_none(UserModel.email == email)
        if not user:
            raise NotFoundException(status_code=404, detail="User not found")         
        if data.name:
            user.name = data.name
        if data.password:
            user.set_password(data.password)            
        await users_repo.update(
            user,
            id_attribute=UserModel.email,
            auto_commit=True,
        )
        return User(name=user.name, email=user.email)

    @delete("/{email:str}")
    async def delete_user(self, users_repo: UserRepository, email: str) -> None:
        await users_repo.delete(email, id_attribute=UserModel.email, auto_commit=True)
