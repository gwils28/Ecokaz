from ecokaz_api.main import create_app
from fastapi.testclient import TestClient


def test_health_reports_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.0.0"}
