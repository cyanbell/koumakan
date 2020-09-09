import os

from starlette.templating import Jinja2Templates

from .settings import settings

templates = Jinja2Templates(
    directory=os.path.join(settings.BASE_DIR, "templates")
)
