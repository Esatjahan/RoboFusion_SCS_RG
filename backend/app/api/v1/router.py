from fastapi import APIRouter

from app.api.v1.endpoints import zones


api_router = APIRouter()

api_router.include_router(
    zones.router,
    prefix="/zones",
    tags=["Zones"],
)