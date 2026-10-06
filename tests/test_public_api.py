import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.seed.seed_data import seed_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """Setup database schema and seed data for public API tests."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_db(db)
    db.close()


def test_get_departments():
    """Test GET /api/departments returns active 4 departments."""
    response = client.get("/api/departments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    slugs = [d["slug"] for d in data]
    assert "development" in slugs
    assert "design" in slugs
    assert "events" in slugs
    assert "social_media" in slugs


def test_get_questions():
    """Test GET /api/questions returns 8 questions without leaking hidden weights."""
    response = client.get("/api/questions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8

    # Verify first question structure
    q1 = data[0]
    assert "text" in q1
    assert "answers" in q1
    assert len(q1["answers"]) == 4

    # Ensure no hidden attributes exposed in answers
    ans1 = q1["answers"][0]
    assert "text" in ans1
    assert "display_order" in ans1
    assert "weight" not in ans1
    assert "category" not in ans1


def test_full_public_sorting_flow():
    """Test full public participant lifecycle: register -> submit answers -> get result -> post interest."""
    # 1. Register participant
    part_resp = client.post(
        "/api/participants",
        json={
            "full_name": "API Test Participant",
            "email": "api_test@example.com",
            "academic_year": "Master 2",
        },
    )
    assert part_resp.status_code == 201
    participant_data = part_resp.json()
    participant_id = participant_data["id"]
    assert "session_token" in participant_data

    # 2. Get questions to construct response payload
    q_resp = client.get("/api/questions")
    questions = q_resp.json()

    # Pick option A (index 0) for each question
    responses = [{"question_id": q["id"], "answer_id": q["answers"][0]["id"]} for q in questions]

    # 3. Submit sorting payload to /api/sort
    sort_resp = client.post(
        "/api/sort",
        json={
            "participant_id": participant_id,
            "responses": responses,
        },
    )
    assert sort_resp.status_code == 200
    sort_data = sort_resp.json()
    result_id = sort_data["result_id"]
    assert sort_data["department"]["slug"] == "development"
    assert "scores" in sort_data

    # 4. Fetch result by result_id
    res_resp = client.get(f"/api/results/{result_id}")
    assert res_resp.status_code == 200
    fetched_res = res_resp.json()
    assert fetched_res["result_id"] == result_id

    # 5. Submit department interest
    interest_resp = client.post(
        f"/api/results/{result_id}/interest",
        json={
            "interested": True,
            "message": "Excited to join Development team!",
            "contact_preference": "Email",
        },
    )
    assert interest_resp.status_code == 200
    assert interest_resp.json()["status"] == "success"
