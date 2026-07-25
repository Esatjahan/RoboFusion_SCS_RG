from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sensor_reading import SensorReading
from app.models.zone import Zone
from app.schemas.sensor_reading import SensorReadingCreate
from app.services.risk_assessment_service import (
    create_risk_assessment_for_reading,
)


def get_zone_by_id(
    db: Session,
    zone_id: int,
) -> Zone | None:
    """
    Return one active or inactive zone by its database ID.
    """

    statement = select(Zone).where(
        Zone.id == zone_id,
    )

    return db.scalar(statement)


def create_sensor_reading(
    db: Session,
    payload: SensorReadingCreate,
) -> SensorReading:
    """
    Create one sensor reading and its automatic risk assessment.

    Both records are saved in one database transaction.
    """

    zone = get_zone_by_id(
        db=db,
        zone_id=payload.zone_id,
    )

    if zone is None:
        raise ValueError(
            f"Zone with ID {payload.zone_id} was not found."
        )

    sensor_reading = SensorReading(
        **payload.model_dump(),
    )

    try:
        db.add(sensor_reading)

        # Generate the sensor reading ID before risk creation.
        db.flush()

        create_risk_assessment_for_reading(
            db=db,
            sensor_reading=sensor_reading,
        )

        # Commit sensor reading and risk assessment together.
        db.commit()

        db.refresh(sensor_reading)

        return sensor_reading

    except Exception:
        db.rollback()
        raise


def get_sensor_readings(
    db: Session,
    *,
    zone_id: int | None = None,
    device_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[SensorReading]:
    """
    Return sensor readings with optional zone and device filters.
    """

    statement = select(SensorReading)

    if zone_id is not None:
        statement = statement.where(
            SensorReading.zone_id == zone_id,
        )

    if device_id is not None:
        statement = statement.where(
            SensorReading.device_id == device_id,
        )

    statement = (
        statement
        .order_by(SensorReading.received_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(
        db.scalars(statement).all()
    )


def get_sensor_reading_by_id(
    db: Session,
    reading_id: int,
) -> SensorReading | None:
    """
    Return one sensor reading by its database ID.
    """

    statement = select(SensorReading).where(
        SensorReading.id == reading_id,
    )

    return db.scalar(statement)