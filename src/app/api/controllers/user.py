from litestar import Controller, Request, get, post, patch, delete
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from app.db.models.user import UserModel
from app.api.schemas.user import User, UserCreate, UserUpdate
from app.db.repositories.user import UserRepository, provide_users_repo
from app.auth.jwt import AuthUser
from typing import Any
from litestar.security.jwt import Token


class UserController(Controller):
    path = "/users"
    dependencies = {"users_repo": Provide(provide_users_repo)}
    tags = ["users"]

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

    @get("/me")
    async def get_user(
        self, users_repo: UserRepository, request: Request[AuthUser, Token, Any]
    ) -> User:
        user = await users_repo.get_one_or_none(UserModel.id == str(request.user.id))
        if not user:
            raise NotFoundException(status_code=404, detail="User not found")
        return User(name=user.name, email=user.email)

    @patch("/me")
    async def update_user(
        self,
        users_repo: UserRepository,
        request: Request[AuthUser, Token, Any],
        data: UserUpdate,
    ) -> User:
        user = await users_repo.get_one_or_none(UserModel.id == request.user.id)
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

    @delete("/me")
    async def delete_user(
        self, users_repo: UserRepository, request: Request[AuthUser, Token, Any]
    ) -> None:
        await users_repo.delete(
            request.user.id, id_attribute=UserModel.id, auto_commit=True
        )
