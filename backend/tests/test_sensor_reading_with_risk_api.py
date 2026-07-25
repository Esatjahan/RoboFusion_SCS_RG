from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_sensor_reading_returns_combined_low_risk_response():
    """Store a normal sensor reading and return a LOW risk assessment."""

    payload = {
        "zone_id": 1,
        "device_id": "TEST-COMBINED-LOW-001",
        "temperature_c": 28.5,
        "humidity_percent": 60,
        "smoke_ppm": 15,
        "gas_ppm": 20,
        "water_level_percent": 5,
        "vibration_level": 0.1,
        "flame_detected": False,
        "motion_detected": True,
        "occupancy_count": 7,
        "battery_voltage": 4.9,
    }

    response = client.post(
        "/api/v1/sensor-readings",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert "sensor_reading" in body
    assert "risk" in body

    sensor_reading = body["sensor_reading"]
    risk = body["risk"]

    assert sensor_reading["zone_id"] == payload["zone_id"]
    assert sensor_reading["device_id"] == payload["device_id"]

    assert sensor_reading["temperature_c"] == payload["temperature_c"]
    assert sensor_reading["humidity_percent"] == payload["humidity_percent"]
    assert sensor_reading["flame_detected"] is False

    assert risk["sensor_reading_id"] == sensor_reading["id"]
    assert risk["zone_id"] == payload["zone_id"]

    assert risk["score"] == 0
    assert risk["level"] == "LOW"

    assert risk["temperature_risk"] == 0
    assert risk["humidity_risk"] == 0
    assert risk["smoke_risk"] == 0
    assert risk["gas_risk"] == 0
    assert risk["water_risk"] == 0
    assert risk["vibration_risk"] == 0
    assert risk["flame_risk"] == 0
    assert risk["occupancy_risk"] == 0
    assert risk["battery_risk"] == 0

    assert isinstance(risk["reasons"], list)
    assert len(risk["reasons"]) >= 1


def test_create_sensor_reading_returns_combined_critical_risk_response():
    """Store a dangerous reading and return a CRITICAL assessment."""

    payload = {
        "zone_id": 1,
        "device_id": "TEST-COMBINED-CRITICAL-001",
        "temperature_c": 46.5,
        "humidity_percent": 39,
        "smoke_ppm": 180,
        "gas_ppm": 240,
        "water_level_percent": 12,
        "vibration_level": 1.8,
        "flame_detected": True,
        "motion_detected": True,
        "occupancy_count": 5,
        "battery_voltage": 4.72,
    }

    response = client.post(
        "/api/v1/sensor-readings",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    sensor_reading = body["sensor_reading"]
    risk = body["risk"]

    assert sensor_reading["device_id"] == payload["device_id"]
    assert sensor_reading["flame_detected"] is True

    assert risk["sensor_reading_id"] == sensor_reading["id"]
    assert risk["zone_id"] == payload["zone_id"]

    assert risk["score"] == 90
    assert risk["level"] == "CRITICAL"

    assert risk["flame_risk"] == 100

    assert any(
        "flame" in reason.lower()
        for reason in risk["reasons"]
    )


def test_create_sensor_reading_with_unknown_zone_returns_404():
    """Reject a sensor packet when the zone does not exist."""

    payload = {
        "zone_id": 999999,
        "device_id": "TEST-UNKNOWN-ZONE-001",
        "temperature_c": 25,
        "humidity_percent": 50,
        "smoke_ppm": 5,
        "gas_ppm": 5,
        "water_level_percent": 0,
        "vibration_level": 0,
        "flame_detected": False,
        "motion_detected": False,
        "occupancy_count": 0,
        "battery_voltage": 5,
    }

    response = client.post(
        "/api/v1/sensor-readings",
        json=payload,
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == (
        "Zone with ID 999999 was not found."
    )