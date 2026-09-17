"""
Health Endpoint Tests for CareFlow AI.

Verifies that the /api/v1/health endpoint returns structured status
and reports database connectivity health appropriately.
"""


def test_health_check_returns_200_and_structured_payload(client):
    """
    Test that GET /api/v1/health returns HTTP 200 OK and includes
    both API service status and database connectivity status.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "data" in data

    payload = data["data"]
    assert payload["status"] == "ok"
    assert payload["service"] == "CareFlow AI"
    # database status should be reported without crashing the application
    assert payload["database"] in ["ok", "unavailable"]


def test_root_endpoint_returns_200(client):
    """
    Test that root endpoint returns service info and health check path.
    """
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "online"
    assert data["health_check"] == "/api/v1/health"
