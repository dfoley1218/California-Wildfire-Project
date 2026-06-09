"""Unit tests for the risk scoring logic.

These test pure math only — no database required — because
calculate_risk_score takes plain values in and returns a dict.
"""

from app.scoring import calculate_risk_score


def test_max_risk_inside_burn():
    # A point sitting inside a recent, fire-dense area should score near 100.
    nearest = {"distance_m": 0, "YEAR_": 2025, "FIRE_NAME": "PALISADES"}
    result = calculate_risk_score(nearest, fire_count=273)
    assert result["risk_score"] > 95
    assert result["factors"]["proximity"]["score"] == 100
    assert result["factors"]["density"]["score"] == 100


def test_low_risk_remote_point():
    # Far from any fire, no nearby fires, and an old fire -> low score.
    nearest = {"distance_m": 60_000, "YEAR_": 1950, "FIRE_NAME": "OLD"}
    result = calculate_risk_score(nearest, fire_count=0)
    assert result["risk_score"] < 20
    # 60 km is past PROXIMITY_MAX_KM (50) -> proximity clamps to 0.
    assert result["factors"]["proximity"]["score"] == 0
    # 0 nearby fires -> density 0.
    assert result["factors"]["density"]["score"] == 0


def test_score_breakdown_structure():
    # The response always exposes the three factors for transparency.
    nearest = {"distance_m": 10_000, "YEAR_": 2020, "FIRE_NAME": "MID"}
    result = calculate_risk_score(nearest, fire_count=5)
    assert "risk_score" in result
    for factor in ("proximity", "density", "recency"):
        assert factor in result["factors"]
        assert "score" in result["factors"][factor]


def test_scores_stay_within_bounds():
    # Even extreme inputs must keep every sub-score in [0, 100].
    nearest = {"distance_m": 999_999, "YEAR_": 1800, "FIRE_NAME": "ANCIENT"}
    result = calculate_risk_score(nearest, fire_count=10_000)
    for factor in ("proximity", "density", "recency"):
        score = result["factors"][factor]["score"]
        assert 0 <= score <= 100
