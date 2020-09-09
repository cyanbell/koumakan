from fastapi.routing import APIRouter
from starlette.status import HTTP_200_OK
from starlette.requests import Request

from ..utils import templates

router = APIRouter()


@router.get("/about_us")
async def get_information_about_us(request: Request):
    return templates.TemplateResponse(
        "about_us.html",
        context={"request": request},
        status_code=HTTP_200_OK
    )