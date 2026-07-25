import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import delete, select

BACKEND_DIR = Path(__file__).resolve().parents[1]
TEST_ENV_FILE = BACKEND_DIR / ".env.test"


if not TEST_ENV_FILE.exists():
    raise RuntimeError(
        "Missing backend/.env.test file. "
        "Create it before running the test suite."
    )


# Must run before app modules are imported.
load_dotenv(TEST_ENV_FILE, override=True)


required_variables = (
    "DATABASE_HOST",
    "DATABASE_PORT",
    "DATABASE_NAME",
    "DATABASE_USER",
    "DATABASE_PASSWORD",
)

missing_variables = [
    variable
    for variable in required_variables
    if not os.getenv(variable)
]

if missing_variables:
    raise RuntimeError(
        "Missing required test database variables: "
        + ", ".join(missing_variables)
    )


test_database_name = os.getenv("DATABASE_NAME")

if test_database_name != "robofusion_test_db":
    raise RuntimeError(
        "Unsafe test database configuration. "
        "Pytest must use 'robofusion_test_db', "
        f"but DATABASE_NAME is {test_database_name!r}."
    )


if os.getenv("APP_ENV", "").lower() != "test":
    raise RuntimeError(
        "Unsafe test environment configuration. "
        "APP_ENV must be set to 'test'."
    )


# Import only after the test environment has been loaded.
from app.db.session import SessionLocal
from app.models.risk_assessment import RiskAssessment
from app.models.sensor_reading import SensorReading
from app.models.zone import Zone


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    """
    Prepare a predictable database state for the complete test session.

    The fixture:
    1. Removes data left by previous test runs.
    2. Creates the required Zone with ID 1.
    3. Cleans generated test records after the suite completes.
    """

    with SessionLocal() as db:
        # Delete child records first to respect foreign-key constraints.
        db.execute(delete(RiskAssessment))
        db.execute(delete(SensorReading))
        db.execute(delete(Zone))
        db.commit()

        test_zone = Zone(
            id=1,
            code="TEST-ZONE-001",
            name="Test Safety Zone",
            location="Automated Test Environment",
            description="Seed zone used only by the pytest suite.",
            is_active=True,
        )

        db.add(test_zone)
        db.commit()

        created_zone = db.scalar(
            select(Zone).where(Zone.id == 1)
        )

        if created_zone is None:
            raise RuntimeError(
                "Failed to create the required test Zone with ID 1."
            )

    yield

    with SessionLocal() as db:
        db.execute(delete(RiskAssessment))
        db.execute(delete(SensorReading))
        db.execute(delete(Zone))
        db.commit()