from dataclasses import asdict, dataclass
from enum import Enum


class RiskLevel(str, Enum):
    """Human-readable risk severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RiskBreakdown:
    """Normalized risk score for every sensor category."""

    temperature: float
    humidity: float
    smoke: float
    gas: float
    water: float
    vibration: float
    flame: float
    occupancy: float
    battery: float

    def to_dict(self) -> dict[str, float]:
        """Return the breakdown as a normal dictionary."""

        return asdict(self)


@dataclass(frozen=True)
class RiskResult:
    """Final output returned by the risk fusion engine."""

    score: float
    level: RiskLevel
    breakdown: RiskBreakdown
    reasons: tuple[str, ...]

    def to_dict(self) -> dict:
        """Return a JSON-compatible representation."""

        return {
            "score": self.score,
            "level": self.level.value,
            "breakdown": self.breakdown.to_dict(),
            "reasons": list(self.reasons),
        }


RISK_WEIGHTS: dict[str, float] = {
    "temperature": 0.15,
    "humidity": 0.05,
    "smoke": 0.18,
    "gas": 0.17,
    "water": 0.12,
    "vibration": 0.10,
    "flame": 0.13,
    "occupancy": 0.05,
    "battery": 0.05,
}


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Restrict a value to the inclusive minimum and maximum range."""

    return max(minimum, min(value, maximum))


def _increasing_risk(
    value: float | None,
    safe_limit: float,
    critical_limit: float,
) -> float:
    """
    Convert a sensor value into a 0–100 risk score.

    Values at or below safe_limit produce 0 risk.
    Values at or above critical_limit produce 100 risk.
    Values between the limits are scaled linearly.
    """

    if value is None:
        return 0.0

    if critical_limit <= safe_limit:
        raise ValueError("critical_limit must be greater than safe_limit")

    if value <= safe_limit:
        return 0.0

    if value >= critical_limit:
        return 100.0

    risk = (
        (value - safe_limit)
        / (critical_limit - safe_limit)
        * 100.0
    )

    return round(_clamp(risk), 2)


def _decreasing_risk(
    value: float | None,
    critical_limit: float,
    safe_limit: float,
) -> float:
    """
    Convert a decreasing value, such as battery voltage, into risk.

    Values at or above safe_limit produce 0 risk.
    Values at or below critical_limit produce 100 risk.
    """

    if value is None:
        return 0.0

    if safe_limit <= critical_limit:
        raise ValueError("safe_limit must be greater than critical_limit")

    if value >= safe_limit:
        return 0.0

    if value <= critical_limit:
        return 100.0

    risk = (
        (safe_limit - value)
        / (safe_limit - critical_limit)
        * 100.0
    )

    return round(_clamp(risk), 2)


def _risk_level(score: float) -> RiskLevel:
    """Map the final numeric score to a severity level."""

    if score >= 75:
        return RiskLevel.CRITICAL

    if score >= 50:
        return RiskLevel.HIGH

    if score >= 25:
        return RiskLevel.MEDIUM

    return RiskLevel.LOW


def calculate_risk(
    *,
    temperature_c: float | None = None,
    humidity_percent: float | None = None,
    smoke_ppm: float | None = None,
    gas_ppm: float | None = None,
    water_level_percent: float | None = None,
    vibration_level: float | None = None,
    flame_detected: bool = False,
    occupancy_count: int = 0,
    battery_voltage: float | None = None,
) -> RiskResult:
    """
    Calculate the final fused risk score.

    The method first normalizes every sensor into a 0–100 score,
    applies category weights, and then applies emergency overrides.
    """

    temperature_risk = _increasing_risk(
        temperature_c,
        safe_limit=30.0,
        critical_limit=60.0,
    )

    humidity_risk = _increasing_risk(
        humidity_percent,
        safe_limit=70.0,
        critical_limit=100.0,
    )

    smoke_risk = _increasing_risk(
        smoke_ppm,
        safe_limit=30.0,
        critical_limit=300.0,
    )

    gas_risk = _increasing_risk(
        gas_ppm,
        safe_limit=50.0,
        critical_limit=500.0,
    )

    water_risk = _increasing_risk(
        water_level_percent,
        safe_limit=10.0,
        critical_limit=100.0,
    )

    vibration_risk = _increasing_risk(
        vibration_level,
        safe_limit=0.2,
        critical_limit=3.0,
    )

    flame_risk = 100.0 if flame_detected else 0.0

    occupancy_risk = _increasing_risk(
        float(occupancy_count),
        safe_limit=20.0,
        critical_limit=100.0,
    )

    battery_risk = _decreasing_risk(
        battery_voltage,
        critical_limit=3.3,
        safe_limit=4.5,
    )

    breakdown = RiskBreakdown(
        temperature=temperature_risk,
        humidity=humidity_risk,
        smoke=smoke_risk,
        gas=gas_risk,
        water=water_risk,
        vibration=vibration_risk,
        flame=flame_risk,
        occupancy=occupancy_risk,
        battery=battery_risk,
    )

    weighted_score = sum(
        breakdown.to_dict()[category] * weight
        for category, weight in RISK_WEIGHTS.items()
    )

    reasons: list[str] = []

    if temperature_risk >= 50:
        reasons.append("Elevated temperature detected.")

    if humidity_risk >= 50:
        reasons.append("Unsafe humidity level detected.")

    if smoke_risk >= 50:
        reasons.append("Elevated smoke concentration detected.")

    if gas_risk >= 50:
        reasons.append("Elevated gas concentration detected.")

    if water_risk >= 50:
        reasons.append("High water level detected.")

    if vibration_risk >= 50:
        reasons.append("Abnormal vibration detected.")

    if flame_detected:
        reasons.append("Flame sensor triggered.")

    if occupancy_risk >= 50:
        reasons.append("High occupancy detected.")

    if battery_risk >= 50:
        reasons.append("Low device battery voltage detected.")

    # Emergency override 1:
    # A detected flame must always produce a critical-level score.
    if flame_detected:
        weighted_score = max(weighted_score, 90.0)

    # Emergency override 2:
    # Simultaneously high smoke and gas indicate likely fire/toxic gas.
    if smoke_risk >= 80 and gas_risk >= 80:
        weighted_score = max(weighted_score, 85.0)

        reasons.append(
            "Combined smoke and gas emergency condition detected."
        )

    # Emergency override 3:
    # Extremely high water level indicates severe flooding.
    if water_risk >= 90:
        weighted_score = max(weighted_score, 80.0)

        reasons.append(
            "Severe flooding condition detected."
        )

    final_score = round(
        _clamp(weighted_score),
        2,
    )

    if not reasons:
        reasons.append("Sensor values are within normal operating limits.")

    return RiskResult(
        score=final_score,
        level=_risk_level(final_score),
        breakdown=breakdown,
        reasons=tuple(reasons),
    )