import pytest

@pytest.mark.parametrize("lat", [200, -200, "abc"])
def test_risk_invalid_lat(client, lat):
    response = client.get(f"/risk?lat={lat}&lon=-118.53")
    assert response.status_code == 422 