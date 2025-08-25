from datetime import datetime, timedelta
from app.db.models.user import UserModel
from litestar import Controller, Response, post
from litestar.di import Provide
from litestar.exceptions import HTTPException, NotAuthorizedException
from app.api.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    AccessTokenResponse,
)
from app.db.repositories.user import UserRepository, provide_users_repo
from app.auth.jwt import jwt_auth, generate_refresh_token, validate_refresh_token


class AuthController(Controller):
    path = "/auth"
    dependencies = {"users_repo": Provide(provide_users_repo)}
    tags = ["auth"]

    @post("/login", exclude_from_auth=True)
    async def login(
        self, users_repo: UserRepository, data: LoginRequest
    ) -> Response[TokenResponse]:
        """Login API that generates 30 minute access token and 1 hour refresh token"""
        user = await users_repo.get_one_or_none(UserModel.email == data.email)
        if not user:
            raise NotAuthorizedException(status_code=401, detail="Invalid credentials")
        if not user.verify_password(data.password):
            raise NotAuthorizedException(status_code=401, detail="Invalid credentials")
        try:
            access_token_expires = datetime.utcnow() + timedelta(minutes=30)
            refresh_token = await generate_refresh_token(user.id)

            response = jwt_auth.login(
                identifier=str(user.id),
                response_body=TokenResponse(
                    access_token="",  # Will be set by jwt_auth.login
                    refresh_token=refresh_token,
                    expires_at=access_token_expires,
                ),
            )

            if isinstance(response.content, TokenResponse):
                response.content.access_token = response.headers.get(
                    "Authorization", ""
                ).replace("Bearer ", "")

            return response

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail="Login failed")

    @post("/refresh")
    async def refresh_token(
        self, users_repo: UserRepository, data: RefreshRequest
    ) -> Response[AccessTokenResponse]:
        """Refresh API to generate new access token using refresh token"""
        try:
            # Validate refresh token
            user_id = await validate_refresh_token(data.refresh_token)
            if not user_id:
                raise NotAuthorizedException("Invalid or expired refresh token")

            # Get user
            user = await users_repo.get(user_id)
            if not user:
                raise NotAuthorizedException("User not found")

            access_token_expires = datetime.utcnow() + timedelta(minutes=30)

            response = jwt_auth.login(
                identifier=str(user.id),
                response_body=AccessTokenResponse(
                    access_token="",  # Will be set by jwt_auth.login
                    expires_at=access_token_expires,
                ),
            )

            # Update the access_token in response body
            if isinstance(response.content, AccessTokenResponse):
                response.content.access_token = response.headers.get(
                    "Authorization", ""
                ).replace("Bearer ", "")

            return response

        except Exception as e:
            if isinstance(e, (HTTPException, NotAuthorizedException)):
                raise e
            raise HTTPException(status_code=500, detail="Token refresh failed")
