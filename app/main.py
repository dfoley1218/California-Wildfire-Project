from fastapi import FastAPI
from app.queries import get_local_fires, largest_fires_by_year, get_fire_by_name, get_local_firms

app = FastAPI(title="California Wildfire API")


@app.get("/")
def root():
    return {"message": "California Wildfire API is running"}

@app.get("/fires/nearby")
def get_nearby_fires(lat: float, lon: float, radius_km: float = 50):
    gdf = get_local_fires(lat, lon, radius_km)
    return gdf[["FIRE_NAME", "YEAR_", "GIS_ACRES"]].to_dict(orient="records")

@app.get("/fires/largest")
def get_largest_fires_by_year(year: int):
    gdf = largest_fires_by_year(year)
    return gdf[["FIRE_NAME", "YEAR_", "GIS_ACRES"]].to_dict(orient="records")

@app.get("/fires/{fire_name}")
def get_fires_by_name(fire_name: str):
        gdf = get_fire_by_name(fire_name)
        return gdf[["FIRE_NAME", "YEAR_", "GIS_ACRES"]].to_dict(orient="records")

@app.get("/firms/nearby")
def get_nearby_NASA_firms_data(lat: float, lon: float, radius_km: float = 50):
    gdf = get_local_firms(lat, lon, radius_km)
    return gdf[["latitude", "longitude", "brightness", "confidence", "acq_date"]].to_dict(orient="records")