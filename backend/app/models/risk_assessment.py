from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


if TYPE_CHECKING:
    from app.models.sensor_reading import SensorReading
    from app.models.zone import Zone


class RiskAssessment(Base):
    """Stored risk result generated from one sensor reading."""

    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    sensor_reading_id: Mapped[int] = mapped_column(
        ForeignKey(
            "sensor_readings.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    zone_id: Mapped[int] = mapped_column(
        ForeignKey(
            "zones.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    temperature_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    humidity_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    smoke_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    gas_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    water_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    vibration_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    flame_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    occupancy_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    battery_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    reasons: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    sensor_reading: Mapped["SensorReading"] = relationship(
        back_populates="risk_assessment",
    )

    zone: Mapped["Zone"] = relationship(
        back_populates="risk_assessments",
    )