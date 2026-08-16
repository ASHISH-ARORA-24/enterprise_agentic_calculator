from app.main import app
from app.settings import settings
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Test client — spins up the app in memory, no real server needed.
# ---------------------------------------------------------------------------

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------


def test_liveness_returns_200() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness_returns_ready_in_normal_mode() -> None:
    settings.fault_mode = "none"
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_readiness_returns_not_ready_in_fault_mode() -> None:
    settings.fault_mode = "unhealthy"
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "not_ready"
    assert response.json()["reason"] == "simulated_failure"
    settings.fault_mode = "none"  # restore after test


# ---------------------------------------------------------------------------
# Calculate — successful operations
# ---------------------------------------------------------------------------


def test_calculate_add() -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operation": "add", "a": "10", "b": "5"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "15"
    assert data["operation"] == "add"
    assert "request_id" in data


def test_calculate_subtract() -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operation": "subtract", "a": "10", "b": "4"},
    )
    assert response.status_code == 200
    assert response.json()["result"] == "6"


def test_calculate_multiply() -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operation": "multiply", "a": "25", "b": "8"},
    )
    assert response.status_code == 200
    assert response.json()["result"] == "200"


def test_calculate_divide() -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operation": "divide", "a": "10", "b": "4"},
    )
    assert response.status_code == 200
    assert response.json()["result"] == "2.5"


def test_calculate_decimal_precision() -> None:
    # With float, 0.1 + 0.2 would be 0.30000000000000004
    response = client.post(
        "/api/v1/calculate",
        json={"operation": "add", "a": "0.1", "b": "0.2"},
    )
    assert response.status_code == 200
    assert response.json()["result"] == "0.3"


def test_calculate_returns_unique_request_id_each_time() -> None:
    r1 = client.post("/api/v1/calculate", json={"operation": "add", "a": 1, "b": 1})
    r2 = client.post("/api/v1/calculate", json={"operation": "add", "a": 1, "b": 1})
    assert r1.json()["request_id"] != r2.json()["request_id"]


# ---------------------------------------------------------------------------
# Calculate — validation errors (422)
# ---------------------------------------------------------------------------


def test_calculate_invalid_operation_returns_422() -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operation": "explode", "a": 5, "b": 3},
    )
    assert response.status_code == 422


def test_calculate_missing_field_returns_422() -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operation": "add", "a": 5},  # missing b
    )
    assert response.status_code == 422


def test_calculate_wrong_type_returns_422() -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operation": "add", "a": "hello", "b": 3},
    )
    assert response.status_code == 422


def test_calculate_divide_by_zero_returns_422_with_typed_error() -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operation": "divide", "a": 5, "b": 0},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "DIVIDE_BY_ZERO"


# ---------------------------------------------------------------------------
# Fault injection
# ---------------------------------------------------------------------------


def test_fault_mode_calculate_500_returns_500() -> None:
    settings.fault_mode = "calculate_500"
    response = client.post(
        "/api/v1/calculate",
        json={"operation": "add", "a": 1, "b": 1},
    )
    assert response.status_code == 500
    assert response.json()["detail"]["code"] == "SIMULATED_FAILURE"
    settings.fault_mode = "none"  # restore after test


# ---------------------------------------------------------------------------
# Version endpoint
# ---------------------------------------------------------------------------


def test_version_returns_service_info() -> None:
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "calculator-service"
    assert "version" in data
    assert "environment" in data
