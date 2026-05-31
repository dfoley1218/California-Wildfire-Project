from fastapi import FastAPI
from app.queries import get_nearby_fires, largest_fires_by_year

app = FastAPI(title="California Wildfire API")


@app.get("/")
def root():
    return {"message": "California Wildfire API is running"}


@app.get("/fires/nearby")
def nearby_fires(lat: float, lon: float, radius_km: float = 50):
    gdf = get_nearby_fires(lat, lon, radius_km)
    return gdf[["FIRE_NAME", "YEAR_", "GIS_ACRES"]].to_dict(orient="records")

@app.get("/fires/largest")
def get_largest_fires_by_year(year: int):
    gdf = largest_fires_by_year(year)
    return gdf[["FIRE_NAME", "YEAR_", "GIS_ACRES"]].to_dict(orient="records")