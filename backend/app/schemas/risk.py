from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.core.risk_engine import RiskLevel


class RiskAssessmentRequest(BaseModel):
    """Input schema for an on-demand risk calculation."""

    temperature_c: float | None = Field(
        default=None,
        ge=-50,
        le=150,
    )

    humidity_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    smoke_ppm: float | None = Field(
        default=None,
        ge=0,
    )

    gas_ppm: float | None = Field(
        default=None,
        ge=0,
    )

    water_level_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    vibration_level: float | None = Field(
        default=None,
        ge=0,
    )

    flame_detected: bool = False

    occupancy_count: int = Field(
        default=0,
        ge=0,
    )

    battery_voltage: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    @model_validator(mode="after")
    def validate_measurement(self) -> "RiskAssessmentRequest":
        """Require at least one meaningful risk input."""

        numeric_values = [
            self.temperature_c,
            self.humidity_percent,
            self.smoke_ppm,
            self.gas_ppm,
            self.water_level_percent,
            self.vibration_level,
            self.battery_voltage,
        ]

        has_numeric = any(
            value is not None
            for value in numeric_values
        )

        has_event = (
            self.flame_detected
            or self.occupancy_count > 0
        )

        if not has_numeric and not has_event:
            raise ValueError(
                "At least one risk input is required."
            )

        return self


class RiskBreakdownResponse(BaseModel):
    """Normalized individual risk components."""

    temperature: float = Field(
        ge=0,
        le=100,
    )

    humidity: float = Field(
        ge=0,
        le=100,
    )

    smoke: float = Field(
        ge=0,
        le=100,
    )

    gas: float = Field(
        ge=0,
        le=100,
    )

    water: float = Field(
        ge=0,
        le=100,
    )

    vibration: float = Field(
        ge=0,
        le=100,
    )

    flame: float = Field(
        ge=0,
        le=100,
    )

    occupancy: float = Field(
        ge=0,
        le=100,
    )

    battery: float = Field(
        ge=0,
        le=100,
    )

    model_config = ConfigDict(
        from_attributes=True,
    )


class RiskAssessmentResponse(BaseModel):
    """
    Risk result returned by the risk preview endpoint.

    This schema represents an in-memory calculation result.
    It is not the schema for a stored RiskAssessment database row.
    """

    score: float = Field(
        ge=0,
        le=100,
    )

    level: RiskLevel

    breakdown: RiskBreakdownResponse

    reasons: list[str]

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )


class RiskAssessmentRecordResponse(BaseModel):
    """
    Response schema for a stored RiskAssessment database record.

    Field names correspond directly to columns in the
    risk_assessments database table.
    """

    id: int

    sensor_reading_id: int

    zone_id: int

    score: float = Field(
        ge=0,
        le=100,
    )

    level: RiskLevel

    temperature_risk: float = Field(
        ge=0,
        le=100,
    )

    humidity_risk: float = Field(
        ge=0,
        le=100,
    )

    smoke_risk: float = Field(
        ge=0,
        le=100,
    )

    gas_risk: float = Field(
        ge=0,
        le=100,
    )

    water_risk: float = Field(
        ge=0,
        le=100,
    )

    vibration_risk: float = Field(
        ge=0,
        le=100,
    )

    flame_risk: float = Field(
        ge=0,
        le=100,
    )

    occupancy_risk: float = Field(
        ge=0,
        le=100,
    )

    battery_risk: float = Field(
        ge=0,
        le=100,
    )

    reasons: list[str]

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
    )