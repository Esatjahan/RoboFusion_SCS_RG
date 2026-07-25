from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class SensorReading(Base):
    """Store one sensor-data packet received from a zone node."""

    __tablename__ = "sensor_readings"

    __table_args__ = (
        Index(
            "ix_sensor_readings_zone_received",
            "zone_id",
            "received_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    zone_id: Mapped[int] = mapped_column(
        ForeignKey(
            "zones.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    device_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    temperature_c: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    humidity_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    smoke_ppm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    gas_ppm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    water_level_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    vibration_level: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    flame_detected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    motion_detected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    occupancy_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    battery_voltage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    captured_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )