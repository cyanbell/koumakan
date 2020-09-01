import traceback

from starlette.middleware.errors import ServerErrorMiddleware as StarletteServerErrorMiddleware


class ServerErrorMiddleware(StarletteServerErrorMiddleware):
    # copy from `https://github.com/encode/starlette/pull/1031`
    def generate_plain_text(self, exc: Exception) -> str:
        return "".join(traceback.format_exception(type(exc)), exc, exc.__traceback__)
