import pytest

from app.core.risk_engine import (
    RiskLevel,
    calculate_risk,
)


def test_normal_sensor_values_produce_low_risk():
    result = calculate_risk(
        temperature_c=27.5,
        humidity_percent=61.2,
        smoke_ppm=18.0,
        gas_ppm=25.0,
        water_level_percent=4.0,
        vibration_level=0.15,
        flame_detected=False,
        occupancy_count=8,
        battery_voltage=4.95,
    )

    assert result.score == 0.0

    assert result.level == RiskLevel.LOW

    assert (
        "Sensor values are within normal operating limits."
        in result.reasons
    )


def test_elevated_temperature_is_normalized():
    result = calculate_risk(
        temperature_c=45.0,
        battery_voltage=4.8,
    )

    assert result.breakdown.temperature == 50.0

    assert result.level == RiskLevel.LOW


def test_flame_detection_forces_critical_risk():
    result = calculate_risk(
        temperature_c=35.0,
        smoke_ppm=40.0,
        gas_ppm=60.0,
        flame_detected=True,
        battery_voltage=4.7,
    )

    assert result.score >= 90.0

    assert result.level == RiskLevel.CRITICAL

    assert "Flame sensor triggered." in result.reasons


def test_combined_smoke_and_gas_forces_critical_risk():
    result = calculate_risk(
        smoke_ppm=270.0,
        gas_ppm=450.0,
        battery_voltage=4.8,
    )

    assert result.score >= 85.0

    assert result.level == RiskLevel.CRITICAL

    assert (
        "Combined smoke and gas emergency condition detected."
        in result.reasons
    )


def test_severe_flooding_forces_critical_risk():
    result = calculate_risk(
        water_level_percent=95.0,
        battery_voltage=4.8,
    )

    assert result.score >= 80.0

    assert result.level == RiskLevel.CRITICAL

    assert (
        "Severe flooding condition detected."
        in result.reasons
    )


def test_low_battery_is_maintenance_risk_only():
    result = calculate_risk(
        temperature_c=25.0,
        battery_voltage=3.3,
    )

    assert result.breakdown.battery == 100.0

    assert result.score == 5.0

    assert result.level == RiskLevel.LOW


def test_score_never_exceeds_one_hundred():
    result = calculate_risk(
        temperature_c=150.0,
        humidity_percent=100.0,
        smoke_ppm=1000.0,
        gas_ppm=1000.0,
        water_level_percent=100.0,
        vibration_level=10.0,
        flame_detected=True,
        occupancy_count=500,
        battery_voltage=0.0,
    )

    assert result.score == 100.0

    assert result.level == RiskLevel.CRITICAL


@pytest.mark.parametrize(
    ("score", "expected_level"),
    [
        (0.0, RiskLevel.LOW),
        (24.99, RiskLevel.LOW),
        (25.0, RiskLevel.MEDIUM),
        (49.99, RiskLevel.MEDIUM),
        (50.0, RiskLevel.HIGH),
        (74.99, RiskLevel.HIGH),
        (75.0, RiskLevel.CRITICAL),
        (100.0, RiskLevel.CRITICAL),
    ],
)
def test_risk_level_boundaries(
    score,
    expected_level,
):
    from app.core.risk_engine import _risk_level

    assert _risk_level(score) == expected_level