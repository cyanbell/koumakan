from fastapi import FastAPI

from .settings import settings
from .middlewares import ServerErrorMiddleware


def generate_app() -> FastAPI:
    """
    generate application instance
    """
    # initialize instance
    app = FastAPI(
        debug=settings.DEBUG,
        docs_url=None,
        redoc_url=None,
    )

    # add middlewares
    app.add_middleware(ServerErrorMiddleware, debug=settings.DEBUG)

    return app
