from fastapi import APIRouter

from app.core.risk_engine import calculate_risk
from app.schemas.risk import (
    RiskAssessmentRequest,
    RiskAssessmentResponse,
)


router = APIRouter()


@router.post(
    "/preview",
    response_model=RiskAssessmentResponse,
    summary="Preview fused risk",
    description=(
        "Calculate a risk score from sensor values without "
        "storing anything in the database."
    ),
)
def preview_risk(
    payload: RiskAssessmentRequest,
) -> RiskAssessmentResponse:
    """
    Calculate and return the fused risk assessment.
    """

    result = calculate_risk(
        temperature_c=payload.temperature_c,
        humidity_percent=payload.humidity_percent,
        smoke_ppm=payload.smoke_ppm,
        gas_ppm=payload.gas_ppm,
        water_level_percent=payload.water_level_percent,
        vibration_level=payload.vibration_level,
        flame_detected=payload.flame_detected,
        occupancy_count=payload.occupancy_count,
        battery_voltage=payload.battery_voltage,
    )

    return RiskAssessmentResponse.model_validate(
        result.to_dict()
    )