from litestar import Litestar, Router
from dataclasses import dataclass
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import StoplightRenderPlugin
from litestar.config.cors import CORSConfig
from litestar import get
from typing import Literal


@dataclass
class HealthCheck:
    status: Literal["ok"]


@get("/health")
def health_check() -> HealthCheck:
    return HealthCheck(status="ok")


def create_app():
    return Litestar(
        route_handlers=[health_check],
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
    )
