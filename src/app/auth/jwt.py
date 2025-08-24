from datetime import timedelta
from uuid import UUID
from litestar.security.jwt import JWTAuth, Token
from litestar.connection import ASGIConnection
from app.services import token_service
from app.config import settings
from dataclasses import dataclass


@dataclass
class AuthUser:
    id: UUID


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection
) -> AuthUser | None:
    return AuthUser(id=UUID(token.sub))


# JWT configuration
jwt_auth = JWTAuth[AuthUser](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=settings.jwt.secret,
    default_token_expiration=timedelta(
        minutes=settings.jwt.access_token_expire_minutes
    ),
    exclude=["/health", "/schema", "/auth", "POST:/users"],
    auth_header="Authorization",
)


async def generate_refresh_token(
    user_id: UUID, expires_in_hours: int | None = None
) -> str:
    """Generate a refresh token for the user using Redis"""
    if expires_in_hours is None:
        expires_in_hours = settings.jwt.refresh_token_expire_hours
    return await token_service.create_refresh_token(user_id, expires_in_hours)


async def validate_refresh_token(refresh_token: str) -> UUID | None:
    """Validate refresh token and return user ID if valid"""
    return await token_service.validate_refresh_token(refresh_token)


async def revoke_refresh_token(refresh_token: str) -> bool:
    """Revoke a specific refresh token"""
    return await token_service.revoke_token(refresh_token)


async def revoke_all_user_tokens(user_id: UUID) -> int:
    """Revoke all tokens for a specific user"""
    return await token_service.revoke_all_user_tokens(user_id)
