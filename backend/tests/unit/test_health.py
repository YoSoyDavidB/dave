from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test that health endpoint returns healthy status."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "0.1.0"


def test_detailed_health_check(client: TestClient) -> None:
    """Test that detailed health endpoint returns service status."""
    response = client.get("/api/v1/health/detailed")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert "llm" in data["services"]
    assert "github" in data["services"]
