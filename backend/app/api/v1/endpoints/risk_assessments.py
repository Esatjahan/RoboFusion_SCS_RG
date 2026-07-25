from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.risk import RiskAssessmentRecordResponse
from app.services.risk_assessment_service import (
    get_latest_zone_risk_assessment,
    get_risk_assessment_by_id,
    get_risk_assessments,
    get_zone_risk_assessments,
)
from app.services.sensor_reading_service import get_zone_by_id


router = APIRouter()

zone_router = APIRouter()


@router.get(
    "",
    response_model=list[RiskAssessmentRecordResponse],
    summary="List risk assessments",
    description=(
        "Return stored risk assessments ordered "
        "from newest to oldest."
    ),
)
def list_risk_assessments(
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
            description="Maximum number of records to return.",
        ),
    ] = 100,
) -> list[RiskAssessmentRecordResponse]:
    """
    Return a paginated list of stored risk assessments.
    """

    return get_risk_assessments(
        db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{assessment_id}",
    response_model=RiskAssessmentRecordResponse,
    summary="Get one risk assessment",
    description="Return one stored risk assessment by its ID.",
)
def read_risk_assessment(
    assessment_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> RiskAssessmentRecordResponse:
    """
    Return one risk assessment or raise a 404 response.
    """

    assessment = get_risk_assessment_by_id(
        db,
        assessment_id,
    )

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Risk assessment with ID {assessment_id} "
                "was not found."
            ),
        )

    return assessment


@zone_router.get(
    "/{zone_id}/risk-assessments",
    response_model=list[RiskAssessmentRecordResponse],
    summary="List risk assessments for one zone",
    description=(
        "Return stored risk assessments for one zone, "
        "ordered from newest to oldest."
    ),
)
def list_zone_risk_assessments(
    zone_id: int,
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
            description="Maximum number of records to return.",
        ),
    ] = 100,
) -> list[RiskAssessmentRecordResponse]:
    """
    Return risk-assessment history for one zone.
    """

    zone = get_zone_by_id(
        db,
        zone_id,
    )

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone with ID {zone_id} was not found.",
        )

    return get_zone_risk_assessments(
        db,
        zone_id=zone_id,
        skip=skip,
        limit=limit,
    )


@zone_router.get(
    "/{zone_id}/latest-risk",
    response_model=RiskAssessmentRecordResponse,
    summary="Get the latest risk assessment for one zone",
    description=(
        "Return the newest stored risk assessment "
        "for one zone."
    ),
)
def read_latest_zone_risk_assessment(
    zone_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> RiskAssessmentRecordResponse:
    """
    Return the latest zone risk or raise a 404 response.
    """

    zone = get_zone_by_id(
        db,
        zone_id,
    )

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone with ID {zone_id} was not found.",
        )

    assessment = get_latest_zone_risk_assessment(
        db,
        zone_id=zone_id,
    )

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No risk assessments were found "
                f"for zone ID {zone_id}."
            ),
        )

    return assessment