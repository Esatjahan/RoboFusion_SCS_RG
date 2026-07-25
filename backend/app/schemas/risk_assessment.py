from pydantic import BaseModel, ConfigDict

from app.schemas.risk import RiskAssessmentRecordResponse
from app.schemas.sensor_reading import SensorReadingResponse


class SensorReadingWithRiskResponse(BaseModel):
    """
    Response returned after storing a sensor reading.

    Includes the stored sensor reading and its automatically
    generated database risk assessment.
    """

    sensor_reading: SensorReadingResponse

    risk: RiskAssessmentRecordResponse

    model_config = ConfigDict(
        from_attributes=True,
    )