from fastapi import APIRouter

from app.api.v1.endpoints import (
    risk,
    risk_assessments,
    sensor_readings,
    zones,
)


api_router = APIRouter()


api_router.include_router(
    zones.router,
    prefix="/zones",
    tags=["Zones"],
)


api_router.include_router(
    risk_assessments.zone_router,
    prefix="/zones",
    tags=["Risk Assessments"],
)


api_router.include_router(
    sensor_readings.router,
    prefix="/sensor-readings",
    tags=["Sensor Readings"],
)


api_router.include_router(
    risk.router,
    prefix="/risk",
    tags=["Risk"],
)


api_router.include_router(
    risk_assessments.router,
    prefix="/risk-assessments",
    tags=["Risk Assessments"],
)