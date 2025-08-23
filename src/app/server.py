import uvicorn


def run():
    uvicorn.run(
        "app.app_factory:create_app",
        host="0.0.0.0",  # TODO: change to server_settings.host
        port=8000,  # TODO: change to server_settings.port
        factory=True,
    )
