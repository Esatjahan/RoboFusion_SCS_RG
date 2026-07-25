from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.risk_engine import RiskResult, calculate_risk
from app.models.risk_assessment import RiskAssessment
from app.models.sensor_reading import SensorReading


def calculate_sensor_reading_risk(
    sensor_reading: SensorReading,
) -> RiskResult:
    """
    Calculate a fused risk result from one sensor reading.
    """

    return calculate_risk(
        temperature_c=sensor_reading.temperature_c,
        humidity_percent=sensor_reading.humidity_percent,
        smoke_ppm=sensor_reading.smoke_ppm,
        gas_ppm=sensor_reading.gas_ppm,
        water_level_percent=sensor_reading.water_level_percent,
        vibration_level=sensor_reading.vibration_level,
        flame_detected=sensor_reading.flame_detected,
        occupancy_count=sensor_reading.occupancy_count,
        battery_voltage=sensor_reading.battery_voltage,
    )


def build_risk_assessment(
    *,
    sensor_reading: SensorReading,
    result: RiskResult,
) -> RiskAssessment:
    """
    Convert a RiskResult into a RiskAssessment database model.
    """

    return RiskAssessment(
        sensor_reading_id=sensor_reading.id,
        zone_id=sensor_reading.zone_id,
        score=result.score,
        level=result.level.value,
        temperature_risk=result.breakdown.temperature,
        humidity_risk=result.breakdown.humidity,
        smoke_risk=result.breakdown.smoke,
        gas_risk=result.breakdown.gas,
        water_risk=result.breakdown.water,
        vibration_risk=result.breakdown.vibration,
        flame_risk=result.breakdown.flame,
        occupancy_risk=result.breakdown.occupancy,
        battery_risk=result.breakdown.battery,
        reasons=list(result.reasons),
    )


def create_risk_assessment_for_reading(
    *,
    db: Session,
    sensor_reading: SensorReading,
) -> RiskAssessment:
    """
    Calculate and stage a risk assessment for a sensor reading.

    This function does not commit the transaction. The caller controls
    the final database commit so sensor and risk data remain atomic.
    """

    result = calculate_sensor_reading_risk(sensor_reading)

    risk_assessment = build_risk_assessment(
        sensor_reading=sensor_reading,
        result=result,
    )

    db.add(risk_assessment)
    db.flush()

    return risk_assessment


def get_risk_assessment_by_id(
    db: Session,
    assessment_id: int,
) -> RiskAssessment | None:
    """
    Return one stored risk assessment by its primary key.
    """

    statement = select(RiskAssessment).where(
        RiskAssessment.id == assessment_id,
    )

    return db.scalar(statement)


def get_risk_assessments(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[RiskAssessment]:
    """
    Return stored risk assessments ordered from newest to oldest.
    """

    statement = (
        select(RiskAssessment)
        .order_by(
            desc(RiskAssessment.created_at),
            desc(RiskAssessment.id),
        )
        .offset(skip)
        .limit(limit)
    )

    return list(
        db.scalars(statement).all(),
    )


def get_zone_risk_assessments(
    db: Session,
    *,
    zone_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[RiskAssessment]:
    """
    Return stored risk assessments for one zone.
    """

    statement = (
        select(RiskAssessment)
        .where(
            RiskAssessment.zone_id == zone_id,
        )
        .order_by(
            desc(RiskAssessment.created_at),
            desc(RiskAssessment.id),
        )
        .offset(skip)
        .limit(limit)
    )

    return list(
        db.scalars(statement).all(),
    )


def get_latest_zone_risk_assessment(
    db: Session,
    *,
    zone_id: int,
) -> RiskAssessment | None:
    """
    Return the newest stored risk assessment for one zone.
    """

    statement = (
        select(RiskAssessment)
        .where(
            RiskAssessment.zone_id == zone_id,
        )
        .order_by(
            desc(RiskAssessment.created_at),
            desc(RiskAssessment.id),
        )
        .limit(1)
    )

    return db.scalar(statement)