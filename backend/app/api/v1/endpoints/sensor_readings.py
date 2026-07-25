from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.risk_assessment import (
    SensorReadingWithRiskResponse,
)
from app.schemas.sensor_reading import (
    SensorReadingCreate,
    SensorReadingResponse,
)
from app.services.sensor_reading_service import (
    create_sensor_reading,
    get_sensor_reading_by_id,
    get_sensor_readings,
    get_zone_by_id,
)


router = APIRouter()


@router.post(
    "",
    response_model=SensorReadingWithRiskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Store a sensor reading and calculate risk",
    description=(
        "Receive and store one validated sensor packet "
        "from a Wokwi or ESP32 zone node, then automatically "
        "calculate and return its fused risk assessment."
    ),
)
def create_reading(
    payload: SensorReadingCreate,
    db: Annotated[Session, Depends(get_db)],
) -> SensorReadingWithRiskResponse:
    """
    Store one sensor reading and return its risk assessment.
    """

    zone = get_zone_by_id(
        db,
        payload.zone_id,
    )

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone with ID {payload.zone_id} was not found.",
        )

    if not zone.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Zone with ID {payload.zone_id} is inactive.",
        )

    try:
        sensor_reading = create_sensor_reading(
            db,
            payload,
        )

        risk_assessment = sensor_reading.risk_assessment

        if risk_assessment is None:
            raise RuntimeError(
                "Risk assessment was not generated for the sensor reading."
            )

        return SensorReadingWithRiskResponse(
            sensor_reading=sensor_reading,
            risk=risk_assessment,
        )

    except SQLAlchemyError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to store the sensor reading "
                "and risk assessment."
            ),
        ) from exc

    except RuntimeError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[SensorReadingResponse],
    summary="List sensor readings",
    description="Return stored sensor readings.",
)
def list_readings(
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[
        int,
        Query(
            ge=0,
            description="Number of records to skip.",
        ),
    ] = 0,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=500,
            description="Maximum records to return.",
        ),
    ] = 100,
) -> list[SensorReadingResponse]:
    """Return a paginated list of readings."""

    return get_sensor_readings(
        db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{reading_id}",
    response_model=SensorReadingResponse,
    summary="Get one sensor reading",
)
def read_sensor_reading(
    reading_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> SensorReadingResponse:
    """Return one reading or raise a 404 response."""

    reading = get_sensor_reading_by_id(
        db,
        reading_id,
    )

    if reading is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Sensor reading with ID {reading_id} "
                "was not found."
            ),
        )

    return reading