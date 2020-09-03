from fastapi.routing import APIRouter
from starlette.responses import HTMLResponse
from starlette.status import HTTP_200_OK

router = APIRouter()


@router.get("/about_us")
async def get_information_about_us():
    return HTMLResponse(
        content="<h1>Nothing to say anymore.</h1>",
        status_code=HTTP_200_OK
    )
