from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.zone import ZoneResponse
from app.services.zone_service import get_zone_by_id, get_zones


router = APIRouter()


@router.get(
    "",
    response_model=list[ZoneResponse],
    summary="List campus zones",
    description="Return monitored campus zones stored in PostgreSQL.",
)
def list_zones(
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
            le=100,
            description="Maximum number of records to return.",
        ),
    ] = 100,
    active_only: Annotated[
        bool,
        Query(
            description="Return only active zones when true.",
        ),
    ] = False,
) -> list[ZoneResponse]:
    """Return a paginated list of campus zones."""

    zones = get_zones(
        db,
        skip=skip,
        limit=limit,
        active_only=active_only,
    )

    return zones


@router.get(
    "/{zone_id}",
    response_model=ZoneResponse,
    summary="Get one campus zone",
    description="Return a campus zone using its database ID.",
)
def read_zone(
    zone_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ZoneResponse:
    """Return one zone or a 404 response when it does not exist."""

    zone = get_zone_by_id(db, zone_id)

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone with ID {zone_id} was not found.",
        )

    return zone