import pytest
from app.models.device import DeviceMaster

@pytest.fixture
def sample_device(db_session):
    device = DeviceMaster(
        device_id="DEV-TEST-001",
        device_name="Test Device",
        device_type="OPC",
        status="online"
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device

def test_list_devices(client, test_token, sample_device):
    response = client.get(
        "/api/v1/devices/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1
    assert data["items"][0]["device_id"] == "DEV-TEST-001"

def test_get_device_detail(client, test_token, sample_device):
    response = client.get(
        f"/api/v1/devices/{sample_device.device_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == "DEV-TEST-001"
    assert data["device_name"] == "Test Device"

def test_device_not_found(client, test_token):
    response = client.get(
        "/api/v1/devices/NONEXISTENT",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 404

def test_unauthorized_access(client, sample_device):
    response = client.get("/api/v1/devices/")
    assert response.status_code == 401
