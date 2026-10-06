import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.seed.seed_data import seed_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_admin_api_database():
    """Setup test database schema and seed data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_db(db)
    db.close()


def get_admin_headers():
    """Helper to authenticate admin user and return Bearer header."""
    resp = client.post(
        "/api/admin/login",
        json={"email": "admin@sdg.dz", "password": "admin123"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_unauthorized_access_to_admin_routes():
    """Verify that unauthenticated requests to admin routes are rejected with 401."""
    assert client.get("/api/admin/statistics").status_code == 401
    assert client.get("/api/admin/participants").status_code == 401
    assert client.get("/api/admin/results").status_code == 401
    assert client.get("/api/admin/questions").status_code == 401


def test_admin_statistics_endpoint():
    """Test GET /api/admin/statistics returns valid dashboard metrics."""
    headers = get_admin_headers()
    response = client.get("/api/admin/statistics", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "total_participants" in data
    assert "completed_sortings" in data
    assert "department_distribution" in data
    assert "department_percentages" in data
    assert "total_interests_submitted" in data
    assert "development" in data["department_distribution"]


def test_admin_list_participants_and_results():
    """Test listing participants and completed results via admin endpoints."""
    headers = get_admin_headers()

    p_resp = client.get("/api/admin/participants", headers=headers)
    assert p_resp.status_code == 200
    assert isinstance(p_resp.json(), list)

    r_resp = client.get("/api/admin/results", headers=headers)
    assert r_resp.status_code == 200
    assert isinstance(r_resp.json(), list)


def test_admin_crud_departments():
    """Test Admin department listing and updating."""
    headers = get_admin_headers()

    # List departments
    list_resp = client.get("/api/admin/departments", headers=headers)
    assert list_resp.status_code == 200
    depts = list_resp.json()
    assert len(depts) >= 4

    dev_dept = next(d for d in depts if d["slug"] == "development")

    # Update department short_description
    update_resp = client.put(
        f"/api/admin/departments/{dev_dept['id']}",
        json={"short_description": "Updated Development description"},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["short_description"] == "Updated Development description"
