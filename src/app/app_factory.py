from litestar import Litestar
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import StoplightRenderPlugin
from litestar.config.cors import CORSConfig


def create_app():
    return Litestar(
        route_handlers=[],
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
