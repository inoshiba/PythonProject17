import os
import pytest
import random
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db
from models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def unique_user():
    email = f"user_{random.randint(1, 1000000)}@test.com"
    password = "secure_password123"
    return {"email": email, "password": password}


def test_full_application_flow(unique_user):
    signup_resp = client.post("/api/auth/signup", json=unique_user)
    assert signup_resp.status_code == 201

    signup_conflict = client.post("/api/auth/signup", json=unique_user)
    assert signup_conflict.status_code == 409

    login_data = {"username": unique_user["email"], "password": unique_user["password"]}
    login_resp = client.post("/api/auth/login", data=login_data)
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    bad_login = client.post(
        "/api/auth/login",
        data={"username": unique_user["email"], "password": "wrong_password"},
    )
    assert bad_login.status_code == 401

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    contact_data = {
        "first_name": "TestContact",
        "last_name": "Doe",
        "email": "contact@mail.com",
        "phone": "+380501112233",
        "birthday": "1990-01-01",
    }

    create_resp = client.post("/api/contacts", json=contact_data, headers=headers)
    assert create_resp.status_code == 201
    contact_id = create_resp.json()["id"]

    list_resp = client.get("/api/contacts", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    get_one = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert get_one.status_code == 200
    assert get_one.json()["first_name"] == "TestContact"

    get_none = client.get("/api/contacts/99999", headers=headers)
    assert get_none.status_code == 404

    contact_data["first_name"] = "UpdatedName"
    update_resp = client.put(
        f"/api/contacts/{contact_id}", json=contact_data, headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["first_name"] == "UpdatedName"

    update_none = client.put(
        "/api/contacts/99999", json=contact_data, headers=headers
    )
    assert update_none.status_code == 404

    delete_resp = client.delete(f"/api/contacts/{contact_id}", headers=headers)
    assert delete_resp.status_code == 204

    delete_none = client.delete("/api/contacts/99999", headers=headers)
    assert delete_none.status_code == 404

    refresh_resp = client.post(
        f"/api/auth/refresh?refresh_token={tokens['refresh_token']}"
    )
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()

    bad_refresh = client.post("/api/auth/refresh?refresh_token=invalid_token")
    assert bad_refresh.status_code == 401


def test_auth_errors_and_dependencies():
    resp = client.get("/api/contacts")
    assert resp.status_code == 401

    resp_bad_token = client.get(
        "/api/contacts", headers={"Authorization": "Bearer bad_token"}
    )
    assert resp_bad_token.status_code == 401