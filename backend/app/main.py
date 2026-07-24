from fastapi import FastAPI

app = FastAPI(
    title="RoboFusion SCS-RG API",
    description="Backend API for the Multi-Hazard Smart Campus Safety and Response Grid.",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Return basic information about the API."""
    return {
        "message": "RoboFusion SCS-RG API is running",
        "status": "online",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the current health status of the backend."""
    return {
        "status": "healthy",
        "service": "backend",
        "version": "0.1.0",
    }