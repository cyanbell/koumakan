from fastapi.routing import APIRouter

from . import about

service_routers = APIRouter()

service_routers.include_router(about.router)
