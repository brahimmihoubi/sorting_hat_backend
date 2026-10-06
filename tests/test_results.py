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


def test_result_retrieval_and_interest():
    """Verify result retrieval by result_id and department interest submission."""
    # 1. Create participant
    p_resp = client.post(
        "/api/participants",
        json={
            "full_name": "Result Test User",
            "email": "result_user@example.com",
            "academic_year": "Master 1",
        },
    )
    p_id = p_resp.json()["id"]

    # 2. Get questions
    q_resp = client.get("/api/questions")
    questions = q_resp.json()
    responses = [{"question_id": q["id"], "answer_id": q["answers"][0]["id"]} for q in questions]

    # 3. Sort
    sort_resp = client.post("/api/sort", json={"participant_id": p_id, "responses": responses})
    res_data = sort_resp.json()
    result_id = res_data["result_id"]

    # 4. Fetch result
    get_res = client.get(f"/api/results/{result_id}")
    assert get_res.status_code == 200
    assert get_res.json()["result_id"] == result_id
    assert get_res.json()["department"]["slug"] == "development"

    # 5. Submit interest
    int_resp = client.post(
        f"/api/results/{result_id}/interest",
        json={"interested": True, "message": "Can't wait!", "contact_preference": "Email"},
    )
    assert int_resp.status_code == 200
    assert int_resp.json()["status"] == "success"
