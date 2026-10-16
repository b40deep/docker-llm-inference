from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


def test_health_reports_demo_mode(monkeypatch):
    monkeypatch.setattr("app.main.get_settings", lambda: None)
    app.dependency_overrides[get_settings] = lambda: type("Settings", (), {"upstream_configured": False})()
    try:
        response = TestClient(app).get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "services": {"inference": "demo"}}
    finally:
        app.dependency_overrides.clear()
