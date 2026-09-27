import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
TEST_DEVICE = "TEST-FURNACE-99"


def test_ingest_telemetry_success():
    payload = {
        "device_id": TEST_DEVICE,
        "ts_shell_temp_c": 1550.0,
        "b_ext_leakage_flux_mt": 12.5,
        "v_n_neutral_voltage_v": 680.0,
        "i_n_coil_current_a": 4200.0,
        "delta_pc_cooling_pressure_bar": 4.2,
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["device_id"] == TEST_DEVICE
    assert "id" in data
    assert data["ts_shell_temp_c"] == 1550.0


def test_ingest_telemetry_validation_error():
    invalid_payload = {
        "device_id": TEST_DEVICE,
        "ts_shell_temp_c": 1550.0,
        "b_ext_leakage_flux_mt": -10.0,  # Below minimum 0.0
        "v_n_neutral_voltage_v": 680.0,
        "i_n_coil_current_a": 4200.0,
        "delta_pc_cooling_pressure_bar": 4.2,
    }
    response = client.post("/api/v1/telemetry", json=invalid_payload)
    assert response.status_code == 422


def test_get_device_telemetry():
    response = client.get(f"/api/v1/telemetry/{TEST_DEVICE}?limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_device_stats_with_anomaly():
    hot_payload = {
        "device_id": TEST_DEVICE,
        "ts_shell_temp_c": 1650.0,  # Exceeds 1600 C threshold
        "b_ext_leakage_flux_mt": 14.0,
        "v_n_neutral_voltage_v": 690.0,
        "i_n_coil_current_a": 4600.0,
        "delta_pc_cooling_pressure_bar": 3.8,
    }
    client.post("/api/v1/telemetry", json=hot_payload)

    response = client.get(f"/api/v1/telemetry/{TEST_DEVICE}/stats?hours=1.0")
    assert response.status_code == 200
    stats = response.json()
    assert stats["sample_count"] >= 1
    assert stats["max_shell_temp_c"] >= 1650.0
    assert stats["thermal_anomaly_detected"] is True


def test_log_maintenance_event():
    event_payload = {
        "device_id": TEST_DEVICE,
        "event_type": "CLASS_A_REFRACTORY",
        "start_time": "2026-09-27T10:00:00Z",
        "description": "Refractory wall patch inspection",
    }
    response = client.post("/api/v1/maintenance", json=event_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["event_type"] == "CLASS_A_REFRACTORY"