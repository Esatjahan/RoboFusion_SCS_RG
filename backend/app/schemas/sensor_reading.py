from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SensorReadingCreate(BaseModel):
    """Validate a sensor packet received from a zone node."""

    zone_id: int = Field(
        gt=0,
        description="Database ID of the monitored zone.",
    )

    device_id: str = Field(
        min_length=1,
        max_length=100,
        examples=["ESP32-IOT-LAB-01"],
    )

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
    motion_detected: bool = False

    occupancy_count: int = Field(
        default=0,
        ge=0,
        le=10000,
    )

    battery_voltage: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    captured_at: datetime | None = None

    @model_validator(mode="after")
    def require_sensor_measurement(self) -> "SensorReadingCreate":
        """Require at least one meaningful sensor measurement."""

        numeric_measurements = (
            self.temperature_c,
            self.humidity_percent,
            self.smoke_ppm,
            self.gas_ppm,
            self.water_level_percent,
            self.vibration_level,
            self.battery_voltage,
        )

        has_numeric_measurement = any(
            value is not None
            for value in numeric_measurements
        )

        has_event_measurement = (
            self.flame_detected
            or self.motion_detected
            or self.occupancy_count > 0
        )

        if not has_numeric_measurement and not has_event_measurement:
            raise ValueError(
                "At least one sensor measurement must be provided."
            )

        return self


class SensorReadingResponse(BaseModel):
    """Response returned after storing or reading sensor data."""

    id: int
    zone_id: int
    device_id: str

    temperature_c: float | None
    humidity_percent: float | None
    smoke_ppm: float | None
    gas_ppm: float | None
    water_level_percent: float | None
    vibration_level: float | None

    flame_detected: bool
    motion_detected: bool
    occupancy_count: int

    battery_voltage: float | None
    captured_at: datetime | None
    received_at: datetime

    model_config = ConfigDict(from_attributes=True)