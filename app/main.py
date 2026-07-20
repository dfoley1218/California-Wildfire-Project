from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
import json
from app.queries import health_check, get_local_fires, largest_fires_by_year, get_fire_by_name, get_local_firms, fire_summary_stats, fire_stats_by_year, get_fire_geojson_by_name, get_fire_geojson_nearby, get_nearest_fire, count_fires_in_radius
from app.scoring import calculate_risk_score

app = FastAPI(title="California Wildfire API")


@app.get("/")
def root():
    # Send visitors of the bare base URL to the interactive Swagger docs.
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    if health_check():
        return {"status": "online"}
    else:
        return {"status": "offline"}

@app.get("/fires/nearby")
def get_nearby_fires(lat: float, lon: float, radius_km: float = 50):
    gdf = get_local_fires(lat, lon, radius_km)
    return gdf[["FIRE_NAME", "YEAR_", "GIS_ACRES"]].to_dict(orient="records")

@app.get("/fires/largest")
def get_largest_fires_by_year(year: int):
    gdf = largest_fires_by_year(year)
    return gdf[["FIRE_NAME", "YEAR_", "GIS_ACRES"]].to_dict(orient="records")

@app.get("/fires/summary")
def get_fire_summary_stats():
    return fire_summary_stats()

@app.get("/fires/stats_by_year")
def get_fire_stats_by_year():
    return fire_stats_by_year()

@app.get("/fires/geojson/nearby")
def get_fire_geojson_nearby_route(lat: float, lon: float, radius_km: float = 50):
    gdf = get_fire_geojson_nearby(lat, lon, radius_km)
    return json.loads(gdf.to_json())

@app.get("/fires/geojson/{fire_name}")
def get_fire_geojson(fire_name: str):
    gdf = get_fire_geojson_by_name(fire_name)
    return json.loads(gdf.to_json())

@app.get("/fires/{fire_name}")
def get_fires_by_name(fire_name: str):
        gdf = get_fire_by_name(fire_name)
        return gdf[["FIRE_NAME", "YEAR_", "GIS_ACRES"]].to_dict(orient="records")

@app.get("/firms/nearby")
def get_nearby_NASA_firms_data(lat: float, lon: float, radius_km: float = 50):
    gdf = get_local_firms(lat, lon, radius_km)
    return gdf[["latitude", "longitude", "brightness", "confidence", "acq_date"]].to_dict(orient="records")

@app.get("/risk")
def get_risk_score(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    nearest = get_nearest_fire(lat, lon)
    fire_count = count_fires_in_radius(lat, lon, 20)
    return calculate_risk_score(nearest, fire_count)




