from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sensor_reading import SensorReading
from app.models.zone import Zone
from app.schemas.sensor_reading import SensorReadingCreate


def get_zone_by_id(
    db: Session,
    zone_id: int,
) -> Zone | None:
    """Return one zone."""

    return db.get(
        Zone,
        zone_id,
    )


def create_sensor_reading(
    db: Session,
    payload: SensorReadingCreate,
) -> SensorReading:
    """Insert one sensor reading."""

    reading = SensorReading(
        **payload.model_dump(),
    )

    db.add(reading)

    db.commit()

    db.refresh(reading)

    return reading


def get_sensor_readings(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[SensorReading]:
    """Return all readings."""

    statement = (
        select(SensorReading)
        .order_by(
            SensorReading.received_at.desc()
        )
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
    """Return one reading."""

    return db.get(
        SensorReading,
        reading_id,
    )