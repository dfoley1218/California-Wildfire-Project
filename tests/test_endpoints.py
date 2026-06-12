import pytest
from fastapi.testclient import TestClient
from app.main import app

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

def test_fires_geojson_nearby(client):
    response = client.get("/fires/geojson/nearby?lat=34.04&lon=-118.53&radius_km=20")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"

def test_fires_geojson_fire_name(client):
    response = client.get("/fires/geojson/fire_name?name=PALISADES")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"

def test_fires_nearby(client):
    response = client.get("/fires/nearby?lat=34.04&lon=-118.53&radius_km=20")
    assert response.status_code == 200
    data = response.json()

def test_fires_largest(client):
    response = client.get("/fires/largest?year=2025")
    assert response.status_code == 200
    data = response.json()

def test_fires_summary(client):
    response = client.get("/fires/summary")
    assert response.status_code == 200

def test_fires_stats_by_year(client):
    response = client.get("/fires/stats_by_year")
    assert response.status_code == 200

def test_fires_by_name(client):
    response = client.get("/fires/PALISADES")
    assert response.status_code == 200

def test_firms_nearby(client):
    response = client.get("/firms/nearby?lat=34.04&lon=-118.53&radius_km=20")
    assert response.status_code == 200
    data = response.json()