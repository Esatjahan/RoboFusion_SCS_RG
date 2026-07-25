from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_test_sensor_reading(
    *,
    zone_id: int = 1,
    risk_type: str = "low",
) -> dict:
    """
    Create one sensor reading through the public API.

    The sensor-reading endpoint automatically creates and returns
    the corresponding stored risk assessment.
    """

    unique_device_id = (
        f"TEST-RISK-GET-{risk_type.upper()}-{uuid4().hex[:10]}"
    )

    if risk_type == "critical":
        payload = {
            "zone_id": zone_id,
            "device_id": unique_device_id,
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
    else:
        payload = {
            "zone_id": zone_id,
            "device_id": unique_device_id,
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

    return body


def assert_risk_record_structure(risk: dict) -> None:
    """
    Verify that a stored risk assessment has all required fields.
    """

    required_fields = {
        "id",
        "sensor_reading_id",
        "zone_id",
        "score",
        "level",
        "temperature_risk",
        "humidity_risk",
        "smoke_risk",
        "gas_risk",
        "water_risk",
        "vibration_risk",
        "flame_risk",
        "occupancy_risk",
        "battery_risk",
        "reasons",
        "created_at",
    }

    assert required_fields.issubset(risk.keys())

    assert isinstance(risk["id"], int)
    assert isinstance(risk["sensor_reading_id"], int)
    assert isinstance(risk["zone_id"], int)
    assert isinstance(risk["score"], float | int)
    assert risk["level"] in {
        "LOW",
        "MODERATE",
        "HIGH",
        "CRITICAL",
    }
    assert isinstance(risk["reasons"], list)
    assert isinstance(risk["created_at"], str)


def test_list_risk_assessments_returns_newest_first():
    """
    The collection endpoint should return stored assessments
    from newest to oldest.
    """

    created = create_test_sensor_reading(
        risk_type="critical",
    )

    created_risk = created["risk"]

    response = client.get(
        "/api/v1/risk-assessments",
        params={
            "skip": 0,
            "limit": 100,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)
    assert len(body) >= 1

    first_risk = body[0]

    assert_risk_record_structure(first_risk)

    assert first_risk["id"] == created_risk["id"]
    assert (
        first_risk["sensor_reading_id"]
        == created_risk["sensor_reading_id"]
    )
    assert first_risk["zone_id"] == created_risk["zone_id"]
    assert first_risk["level"] == "CRITICAL"


def test_get_risk_assessment_by_id_returns_record():
    """
    A valid assessment ID should return exactly one stored record.
    """

    created = create_test_sensor_reading(
        risk_type="low",
    )

    created_risk = created["risk"]
    assessment_id = created_risk["id"]

    response = client.get(
        f"/api/v1/risk-assessments/{assessment_id}",
    )

    assert response.status_code == 200

    body = response.json()

    assert_risk_record_structure(body)

    assert body["id"] == assessment_id
    assert (
        body["sensor_reading_id"]
        == created_risk["sensor_reading_id"]
    )
    assert body["zone_id"] == 1
    assert body["score"] == 0
    assert body["level"] == "LOW"


def test_get_unknown_risk_assessment_returns_404():
    """
    A risk-assessment ID that does not exist should return 404.
    """

    assessment_id = 999999999

    response = client.get(
        f"/api/v1/risk-assessments/{assessment_id}",
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == (
        f"Risk assessment with ID {assessment_id} "
        "was not found."
    )


def test_list_zone_risk_assessments_returns_zone_history():
    """
    The zone history endpoint should return assessments belonging
    only to the requested zone.
    """

    created = create_test_sensor_reading(
        zone_id=1,
        risk_type="critical",
    )

    created_risk = created["risk"]

    response = client.get(
        "/api/v1/zones/1/risk-assessments",
        params={
            "skip": 0,
            "limit": 100,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)
    assert len(body) >= 1

    assessment_ids = {
        assessment["id"]
        for assessment in body
    }

    assert created_risk["id"] in assessment_ids

    for assessment in body:
        assert_risk_record_structure(assessment)
        assert assessment["zone_id"] == 1


def test_get_latest_zone_risk_returns_newest_record():
    """
    The latest-risk endpoint should return the newest stored
    assessment for the requested zone.
    """

    create_test_sensor_reading(
        zone_id=1,
        risk_type="low",
    )

    newest = create_test_sensor_reading(
        zone_id=1,
        risk_type="critical",
    )

    newest_risk = newest["risk"]

    response = client.get(
        "/api/v1/zones/1/latest-risk",
    )

    assert response.status_code == 200

    body = response.json()

    assert_risk_record_structure(body)

    assert body["id"] == newest_risk["id"]
    assert (
        body["sensor_reading_id"]
        == newest_risk["sensor_reading_id"]
    )
    assert body["zone_id"] == 1
    assert body["score"] == 90
    assert body["level"] == "CRITICAL"


def test_unknown_zone_risk_history_returns_404():
    """
    Risk history for a zone that does not exist should return 404.
    """

    zone_id = 999999999

    response = client.get(
        f"/api/v1/zones/{zone_id}/risk-assessments",
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == (
        f"Zone with ID {zone_id} was not found."
    )


def test_unknown_zone_latest_risk_returns_404():
    """
    Latest risk for a zone that does not exist should return 404.
    """

    zone_id = 999999999

    response = client.get(
        f"/api/v1/zones/{zone_id}/latest-risk",
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == (
        f"Zone with ID {zone_id} was not found."
    )