import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.seed.seed_data import seed_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_db(db)
    db.close()


def test_participant_creation():
    """Verify POST /api/participants creates a session with unique token and status 'started'."""
    response = client.post(
        "/api/participants",
        json={
            "full_name": "Test Participant",
            "email": "participant@example.com",
            "academic_year": "Licence 2",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Test Participant"
    assert data["email"] == "participant@example.com"
    assert data["status"] == "started"
    assert data["session_token"].startswith("sdg_session_")
