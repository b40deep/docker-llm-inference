from fastapi.testclient import TestClient

from app.auth import create_session, verify_password
from app.config import Settings
from app.main import app


def test_verify_password_accepts_exact_match():
    assert verify_password("correct", Settings(app_password="correct"))


def test_verify_password_rejects_wrong_match():
    assert not verify_password("incorrect", Settings(app_password="correct"))


def test_session_validation_requires_a_valid_bearer_token():
    settings = Settings(app_password="correct")
    session = create_session(settings)
    client = TestClient(app)

    assert client.get("/api/auth/session").status_code == 401
    assert client.get("/api/auth/session", headers={"Authorization": f"Bearer {session.token}"}).json() == {
        "authenticated": True
    }
