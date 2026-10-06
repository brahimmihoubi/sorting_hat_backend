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


def test_questionnaire_retrieval():
    """Verify GET /api/questions returns 8 active questions and 32 answers ordered correctly."""
    response = client.get("/api/questions")
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) == 8

    # Verify ordering Q1 through Q8
    for i, q in enumerate(questions, start=1):
        assert q["display_order"] == i
        assert len(q["answers"]) == 4

        # Verify A, B, C, D ordering
        for j, ans in enumerate(q["answers"], start=1):
            assert ans["display_order"] == j
            # Verify hidden classification details are absent
            assert "category" not in ans
            assert "weight" not in ans
            assert "department_id" not in ans
