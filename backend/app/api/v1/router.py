from fastapi import APIRouter

from app.api.v1.endpoints import sensor_readings, zones


api_router = APIRouter()


api_router.include_router(
    zones.router,
    prefix="/zones",
    tags=["Zones"],
)


api_router.include_router(
    sensor_readings.router,
    prefix="/sensor-readings",
    tags=["Sensor Readings"],
)