from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine


app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API for the RoboFusion Smart Campus "
        "Safety and Response Grid."
    ),
    version=settings.app_version,
)


app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get(
    "/",
    tags=["System"],
    summary="API root",
)
def read_root() -> dict[str, str]:
    """Return basic information about the API."""

    return {
        "message": "RoboFusion SCS-RG API is running",
        "status": "online",
        "environment": settings.app_env,
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Backend health check",
)
def health_check() -> dict[str, str]:
    """Return the current health status of the backend."""

    return {
        "status": "healthy",
        "service": "backend",
        "version": settings.app_version,
    }


@app.get(
    "/health/database",
    tags=["System"],
    summary="Database health check",
)
def database_health_check() -> dict[str, str]:
    """Verify that the backend can connect to PostgreSQL."""

    try:
        with engine.connect() as connection:
            database_name = connection.execute(
                text("SELECT current_database();")
            ).scalar_one()

            database_user = connection.execute(
                text("SELECT current_user;")
            ).scalar_one()

        return {
            "status": "healthy",
            "service": "postgresql",
            "database": database_name,
            "user": database_user,
        }

    except SQLAlchemyError:
        return {
            "status": "unhealthy",
            "service": "postgresql",
            "message": "Database connection failed",
        }