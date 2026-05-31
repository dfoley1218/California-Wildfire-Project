from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_nearby_fires_returns_list():
    response = client.get("/fires/nearby?lat=34.01&lon=-118.49&radius_km=50")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_nearby_fires_result_shape():
    response = client.get("/fires/nearby?lat=34.01&lon=-118.49&radius_km=50")
    data = response.json()
    if len(data) > 0:
        assert "FIRE_NAME" in data[0]
        assert "YEAR_" in data[0]
        assert "GIS_ACRES" in data[0]
