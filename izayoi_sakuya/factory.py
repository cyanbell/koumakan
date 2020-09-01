from fastapi import FastAPI

from .settings import settings

def generate_app() -> FastAPI:
    """
    generate application instance
    """
    app = FastAPI(
        debug=settings.DEBUG,
        docs_url=None,
        redoc_url=None,
    )

    return app
