import pytest

@pytest.mark.parametrize("lat", [200, -200, "abc"])
def test_risk_invalid_lat(client, lat):
    response = client.get(f"/risk?lat={lat}&lon=-118.53")
    assert response.status_code == 422 

def test_risk_missing_params(client):
    response = client.get("/risk")
    assert response.status_code == 422