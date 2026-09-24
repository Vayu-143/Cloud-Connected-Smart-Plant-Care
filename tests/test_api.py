from fastapi.testclient import TestClient

from backend.app import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"


def test_health():

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


def test_sensor_data():

    sensor_data = {

        "device_id": "TEST-001",

        "soil_moisture": 50,

        "temperature": 28,

        "humidity": 60

    }


    response = client.post(
        "/api/sensor",
        json=sensor_data
    )


    assert response.status_code == 200

    data = response.json()

    assert data["soil_moisture"] == 50

    assert data["temperature"] == 28

    assert data["humidity"] == 60


def test_invalid_moisture():

    sensor_data = {

        "device_id": "TEST-002",

        "soil_moisture": 150,

        "temperature": 28,

        "humidity": 60

    }


    response = client.post(
        "/api/sensor",
        json=sensor_data
    )


    assert response.status_code == 422


def test_threshold():

    response = client.put(
        "/api/threshold",
        json={
            "threshold": 35
        }
    )


    assert response.status_code == 200

    data = response.json()

    assert data["threshold"] == 35