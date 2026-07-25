from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sensor_reading import SensorReading
from app.models.zone import Zone
from app.schemas.sensor_reading import SensorReadingCreate


def get_zone_by_id(
    db: Session,
    zone_id: int,
) -> Zone | None:
    """Return a zone using its database ID."""

    return db.get(Zone, zone_id)


def create_sensor_reading(
    db: Session,
    payload: SensorReadingCreate,
) -> SensorReading:
    """Store one validated sensor reading."""

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
    zone_id: int | None = None,
    device_id: str | None = None,
) -> list[SensorReading]:
    """Return sensor readings with optional filtering."""

    statement = (
        select(SensorReading)
        .order_by(SensorReading.received_at.desc())
    )

    if zone_id is not None:
        statement = statement.where(
            SensorReading.zone_id == zone_id
        )

    if device_id is not None:
        statement = statement.where(
            SensorReading.device_id == device_id
        )

    statement = statement.offset(skip).limit(limit)

    return list(db.scalars(statement).all())


def get_sensor_reading_by_id(
    db: Session,
    reading_id: int,
) -> SensorReading | None:
    """Return one sensor reading by its primary key."""

    return db.get(SensorReading, reading_id)