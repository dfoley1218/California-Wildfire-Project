# --- Risk model config (heuristic weights; not trained — see README) ---
WEIGHT_PROXIMITY = 0.5
WEIGHT_DENSITY   = 0.3
WEIGHT_RECENCY   = 0.2

PROXIMITY_MAX_KM   = 50    # beyond this → proximity score 0
DENSITY_SATURATION = 20    # this many fires → density score 100
RECENCY_MAX_YEARS  = 50    # older than this → recency score 0
CURRENT_YEAR       = 2026

# proximity: nearest fire in km → 0–100
distance_km = nearest["distance_m"] / 1000
proximity = max(0, 100 - (distance_km * (100 / PROXIMITY_MAX_KM)))

# density: count of nearby fires → 0–100
density = min(100, fire_count * (100 / DENSITY_SATURATION))

# recency: years since most recent → 0–100
years_ago = CURRENT_YEAR - nearest["YEAR_"]
recency = max(0, 100 - (years_ago * (100 / RECENCY_MAX_YEARS)))

risk_score = (proximity * WEIGHT_PROXIMITY) + (density * WEIGHT_DENSITY) + (recency * WEIGHT_RECENCY)


def calculate_risk_score(nearest, fire_count):
    distance_km = nearest["distance_m"] / 1000
    year = nearest["YEAR_"]
    fire_name = nearest["FIRE_NAME"]
    years_ago = CURRENT_YEAR - year
    proximity = max(0, 100 - (distance_km * (100 / PROXIMITY_MAX_KM)))
    density = min(100, fire_count * (100 / DENSITY_SATURATION))
    recency = max(0, 100 - (years_ago * (100 / RECENCY_MAX_YEARS)))

    risk_score = (proximity * WEIGHT_PROXIMITY) + (density * WEIGHT_DENSITY) + (recency * WEIGHT_RECENCY)

    return {
        "risk_score": round(risk_score, 1),
        "factors": {
            "proximity": {"score": round(proximity, 1), "nearest_fire_km": round(distance_km, 2),
            "nearest_fire": fire_name, "year": int(year)},
            "density":   {"score": round(density, 1), "fires_within_radius": int(fire_count)},
            "recency":   {"score": round(recency, 1), "most_recent_year": int(year)},
        },
    }





