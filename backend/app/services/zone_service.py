from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.zone import Zone


def get_zones(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
) -> list[Zone]:
    """Return zones from the database with optional filtering."""

    statement = select(Zone).order_by(Zone.id)

    if active_only:
        statement = statement.where(Zone.is_active.is_(True))

    statement = statement.offset(skip).limit(limit)

    return list(db.scalars(statement).all())


def get_zone_by_id(
    db: Session,
    zone_id: int,
) -> Zone | None:
    """Return one zone by its database ID."""

    statement = select(Zone).where(Zone.id == zone_id)

    return db.scalar(statement)