"""
Automated unit tests for Flask API endpoints and telemetry pipeline.
"""

import pytest
from backend.server import app, state, dispatch_telemetry


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "service" in data


def test_status_endpoint(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.get_json()
    assert "azure_status" in data
    assert "demo_mode" in data
    assert "student_name" in data
    assert "roll_number" in data


def test_telemetry_latest_fields(client):
    # Dispatch an event with ASCII for "Hello"
    dispatch_telemetry("72,101,108,108,111", source="test")

    response = client.get("/api/telemetry/latest")
    assert response.status_code == 200
    data = response.get_json()

    # Verify all 6 required assignment fields
    assert "student_name" in data
    assert "roll_number" in data
    assert "azure_status" in data
    assert "raw_ascii" in data
    assert "converted_string" in data
    assert "timestamp" in data

    # Verify converted values
    assert data["raw_ascii"] == "72,101,108,108,111"
    assert data["converted_string"] == "Hello"
    assert data["valid"] is True


def test_telemetry_simulate_endpoint(client):
    response = client.post("/api/telemetry/simulate", json={"payload": "65,66,67"})
    assert response.status_code == 200

    latest_resp = client.get("/api/telemetry/latest")
    latest = latest_resp.get_json()
    assert latest["raw_ascii"] == "65,66,67"
    assert latest["converted_string"] == "ABC"


def test_telemetry_history_endpoint(client):
    client.post("/api/telemetry/simulate", json={"payload": "79,75"})  # OK
    response = client.get("/api/telemetry/history")
    assert response.status_code == 200
    data = response.get_json()
    assert "history" in data
    assert len(data["history"]) > 0
    assert data["history"][0]["converted_string"] == "OK"


def test_legacy_endpoint(client):
    response = client.get("/api/latest")
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "timestamp" in data
