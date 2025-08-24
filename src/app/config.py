from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_", case_sensitive=False, extra="ignore"
    )

    url: PostgresDsn = Field(
        description="PostgreSQL database URL",
        examples=["postgresql+asyncpg://user:pass@localhost:5432/biosensor"],
    )

    @field_validator("url")
    @classmethod
    def validate_database_url(cls, v: PostgresDsn) -> PostgresDsn:
        """Ensure the database URL uses asyncpg driver."""
        if not str(v).startswith(("postgresql+asyncpg://", "postgres+asyncpg://")):
            # Convert postgres:// to postgresql+asyncpg://
            url_str = str(v)
            if url_str.startswith("postgres://"):
                url_str = url_str.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url_str.startswith("postgresql://"):
                url_str = url_str.replace("postgresql://", "postgresql+asyncpg://", 1)
            return PostgresDsn(url_str)
        return v


class RedisConfig(BaseSettings):
    """Redis configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_", case_sensitive=False, extra="ignore"
    )

    url: RedisDsn = Field(
        default="redis://localhost:6379", description="Redis connection URL"
    )


class AWSConfig(BaseSettings):
    """AWS configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="AWS_", case_sensitive=False, extra="ignore"
    )

    access_key_id: str = Field(description="AWS Access Key ID")
    secret_access_key: str = Field(description="AWS Secret Access Key")
    region: str = Field(default="ap-northeast-2", description="AWS region")


class S3Config(BaseSettings):
    """S3 configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="AWS_S3_", case_sensitive=False, extra="ignore"
    )

    bucket_name: str = Field(description="S3 bucket name for file storage")
    presigned_url_expiry: int = Field(
        default=3600, description="Presigned URL expiry time in seconds"
    )


class JWTConfig(BaseSettings):
    """JWT authentication configuration."""

    model_config = SettingsConfigDict(
        env_prefix="JWT_", case_sensitive=False, extra="ignore"
    )

    secret: str = Field(description="JWT secret key for signing tokens")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )
    refresh_token_expire_hours: int = Field(
        default=24, description="Refresh token expiration time in hours"
    )


class AppConfig(BaseSettings):
    """Main application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # App settings
    app_name: str = Field(default="Biosensor API")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # API settings
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    # CORS settings
    cors_allow_origins: str = Field(
        default="*", 
        description="Comma-separated list of allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: str = Field(
        default="*", 
        description="Comma-separated list of allowed CORS methods"
    )
    cors_allow_headers: str = Field(
        default="*", 
        description="Comma-separated list of allowed CORS headers"
    )

    @property
    def cors_allow_origins_list(self) -> list[str]:
        """Convert comma-separated origins string to list."""
        if self.cors_allow_origins == "*":
            return ["*"]
        return [item.strip() for item in self.cors_allow_origins.split(",") if item.strip()]

    @property
    def cors_allow_methods_list(self) -> list[str]:
        """Convert comma-separated methods string to list."""
        if self.cors_allow_methods == "*":
            return ["*"]
        return [item.strip() for item in self.cors_allow_methods.split(",") if item.strip()]

    @property
    def cors_allow_headers_list(self) -> list[str]:
        """Convert comma-separated headers string to list."""
        if self.cors_allow_headers == "*":
            return ["*"]
        return [item.strip() for item in self.cors_allow_headers.split(",") if item.strip()]

    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)
    s3: S3Config = Field(default_factory=S3Config)
    jwt: JWTConfig = Field(default_factory=JWTConfig)

    def __init__(self, **kwargs):
        """Initialize with component configs loaded from environment."""
        super().__init__(**kwargs)
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.aws = AWSConfig()
        self.s3 = S3Config()
        self.jwt = JWTConfig()


@lru_cache()
def get_settings() -> AppConfig:
    return AppConfig()


settings = get_settings()
