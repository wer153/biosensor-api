from math import e
from litestar import Litestar
from litestar.plugins.sqlalchemy import (
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from dataclasses import dataclass
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import StoplightRenderPlugin, SwaggerRenderPlugin
from litestar.config.cors import CORSConfig
from litestar.logging import LoggingConfig
from litestar.handlers.http_handlers.decorators import get
from typing import Literal
from litestar.plugins.sqlalchemy import base
from app.api.controllers.user import UserController
from app.api.controllers.auth import AuthController
from app.api.controllers.file import FileController
from app.auth.jwt import jwt_auth
from app.config import settings


@dataclass
class HealthCheck:
    status: Literal["ok"]


@get("/health", tags=["health"], exclude_from_auth=True)
def health_check() -> HealthCheck:
    return HealthCheck(status="ok")


_CONFIG = SQLAlchemyAsyncConfig(
    connection_string=str(settings.database.url),
    create_all=True,
    metadata=base.orm_registry.metadata,
)
_PLUGIN = SQLAlchemyPlugin(config=_CONFIG)


def create_app():
    logging_config = LoggingConfig(
        root={"level": "INFO", "handlers": ["queue_listener"]},
        log_exceptions="always",
    )

    return Litestar(
        route_handlers=[health_check, UserController, AuthController, FileController],
        openapi_config=OpenAPIConfig(
            title=settings.app_name,
            description=settings.app_name,
            version=settings.app_version,
            render_plugins=[StoplightRenderPlugin(), SwaggerRenderPlugin()],
        ),
        cors_config=CORSConfig(
            allow_origins=settings.cors_allow_origins_list,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=settings.cors_allow_methods_list,
            allow_headers=settings.cors_allow_headers_list,
        ),
        plugins=[_PLUGIN],
        on_app_init=[jwt_auth.on_app_init],
        logging_config=logging_config,
    )
