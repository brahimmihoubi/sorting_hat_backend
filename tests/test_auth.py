import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.seed.seed_data import seed_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_auth_database():
    """Setup schema and seed admin user."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_db(db)
    db.close()


def test_admin_login_success():
    """Test successful admin login with valid credentials."""
    response = client.post(
        "/api/admin/login",
        json={
            "email": "admin@sdg.dz",
            "password": "admin123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["admin_email"] == "admin@sdg.dz"


def test_admin_login_invalid_password():
    """Test login rejection with invalid password."""
    response = client.post(
        "/api/admin/login",
        json={
            "email": "admin@sdg.dz",
            "password": "wrong_password",
        },
    )
    assert response.status_code == 401


def test_protected_admin_me_endpoint():
    """Test token verification on protected /api/admin/me route."""
    # Attempt without token -> 401
    unauth_resp = client.get("/api/admin/me")
    assert unauth_resp.status_code == 401

    # Login to get valid token
    login_resp = client.post(
        "/api/admin/login",
        json={
            "email": "admin@sdg.dz",
            "password": "admin123",
        },
    )
    token = login_resp.json()["access_token"]

    # Attempt with Bearer header -> 200 OK
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/admin/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "admin@sdg.dz"


def test_admin_logout():
    """Test protected admin logout endpoint."""
    login_resp = client.post(
        "/api/admin/login",
        json={
            "email": "admin@sdg.dz",
            "password": "admin123",
        },
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout_resp = client.post("/api/admin/logout", headers=headers)
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "success"
