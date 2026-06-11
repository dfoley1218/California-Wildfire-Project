import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "online"}

def test_risk(client):
    response = client.get("/risk?lat=34.04&lon=-118.53")
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "factors" in data