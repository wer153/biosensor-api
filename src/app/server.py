import uvicorn
from app.config import settings


def run():
    uvicorn.run(
        "app.app_factory:create_app",
        host=settings.api_host,
        port=settings.api_port,
        factory=True,
    )
