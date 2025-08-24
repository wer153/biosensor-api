import os
from litestar import Litestar
from litestar.plugins.sqlalchemy import (
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from dataclasses import dataclass
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import StoplightRenderPlugin
from litestar.config.cors import CORSConfig
from litestar.handlers.http_handlers.decorators import get
from typing import Literal
from litestar.plugins.sqlalchemy import base
from app.api.controllers.user import UserController
from app.api.controllers.auth import AuthController
from app.api.controllers.file import FileController
from app.auth.jwt import jwt_auth


@dataclass
class HealthCheck:
    status: Literal["ok"]


@get("/health", tags=["health"])
def health_check() -> HealthCheck:
    return HealthCheck(status="ok")


DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise ValueError("DATABASE_URL is not set")

_CONFIG = SQLAlchemyAsyncConfig(
    connection_string=DB_URL,
    create_all=True,
    metadata=base.orm_registry.metadata,
)
_PLUGIN = SQLAlchemyPlugin(config=_CONFIG)


def create_app():
    return Litestar(
        route_handlers=[health_check, UserController, AuthController, FileController],
        openapi_config=OpenAPIConfig(
            title="Biosensor API",
            description="Biosensor API",
            version="0.0.1",
            render_plugins=[StoplightRenderPlugin()],
        ),
        cors_config=CORSConfig(
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        plugins=[_PLUGIN],
        on_app_init=[jwt_auth.on_app_init],
    )
