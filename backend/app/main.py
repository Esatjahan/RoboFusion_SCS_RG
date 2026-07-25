from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine


app = FastAPI(
    title=settings.app_name,
    description=(
        "# 🚀 RoboFusion Smart Campus Safety & Response Grid (SCS-RG)\n\n"
        "An intelligent IoT-based Smart Campus Safety Platform developed for "
        "**RoboFusion Techathon 2026**.\n\n"
        "## ✨ Core Features\n"
        "- 🏫 Campus Zone Management\n"
        "- 📡 IoT Sensor Data Collection\n"
        "- 🤖 AI-Based Risk Assessment Engine\n"
        "- 📊 Historical Risk Analytics\n"
        "- ❤️ Backend & Database Health Monitoring\n\n"
        "---\n"
        "## 👥 Team\n"
        "**GenZ Ignite**\n\n"
        "- Mst. Esat Jahan Akhi\n"
        "- Md. Muniruzzaman Bony\n\n"
        "---\n"
        "Built using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **Pydantic v2**."
    ),
    version=settings.app_version,
    contact={
        "name": "GenZ Ignite",
        "email": "esat0001@std.uftb.ac.bd",
    },
    license_info={
        "name": "MIT License",
    },
    docs_url=None,
    redoc_url=None,
)


# =========================================================
# CORS CONFIGURATION
# =========================================================
# Allow the React/Vite frontend to access this FastAPI backend.
#
# Frontend development URLs:
# - http://localhost:5173
# - http://127.0.0.1:5173
#
# Without this middleware, the browser may receive a 200 response
# from the backend but still block JavaScript from reading it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# STATIC FILES
# =========================================================
# Used by the custom dark Swagger documentation.
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


# =========================================================
# CUSTOM SWAGGER DOCUMENTATION
# =========================================================
@app.get(
    "/docs",
    include_in_schema=False,
)
async def custom_swagger() -> HTMLResponse:
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API Documentation",
    )

    content = html.body.decode()

    css = (
        '<link rel="stylesheet" '
        'href="/static/css/swagger-dark.css">'
    )

    content = content.replace(
        "</head>",
        css + "</head>",
    )

    return HTMLResponse(content)


# =========================================================
# API ROUTES
# =========================================================
app.include_router(
    api_router,
    prefix="/api/v1",
)


# =========================================================
# SYSTEM ENDPOINTS
# =========================================================
@app.get(
    "/",
    tags=["System"],
    summary="API Root",
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
    summary="Backend Health Check",
)
def health_check() -> dict[str, str]:
    """Return backend health status."""

    return {
        "status": "healthy",
        "service": "backend",
        "version": settings.app_version,
    }


@app.get(
    "/health/database",
    tags=["System"],
    summary="Database Health Check",
)
def database_health_check() -> dict[str, str]:
    """Verify PostgreSQL database connectivity."""

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