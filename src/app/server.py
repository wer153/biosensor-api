import uvicorn


def run():
    uvicorn.run(
        "src.app.app_factory:create_app",
        host="0.0.0.0",  # TODO: change to server_settings.host
        port=8000,  # TODO: change to server_settings.port
        reload=True,
        reload_dirs=["src"],
        factory=True,
    )
