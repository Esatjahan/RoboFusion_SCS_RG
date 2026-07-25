from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_risk_preview_normal_condition():
    response = client.post(
        "/api/v1/risk/preview",
        json={
            "temperature_c": 27.5,
            "humidity_percent": 61.2,
            "smoke_ppm": 18.0,
            "gas_ppm": 25.0,
            "water_level_percent": 4.0,
            "vibration_level": 0.15,
            "flame_detected": False,
            "occupancy_count": 8,
            "battery_voltage": 4.95,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["score"] == 0.0

    assert data["level"] == "LOW"


def test_risk_preview_flame_emergency():
    response = client.post(
        "/api/v1/risk/preview",
        json={
            "temperature_c": 35.0,
            "smoke_ppm": 40.0,
            "gas_ppm": 60.0,
            "flame_detected": True,
            "battery_voltage": 4.7,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["score"] >= 90.0

    assert data["level"] == "CRITICAL"

    assert "Flame sensor triggered." in data["reasons"]


def test_risk_preview_rejects_empty_payload():
    response = client.post(
        "/api/v1/risk/preview",
        json={},
    )

    assert response.status_code == 422