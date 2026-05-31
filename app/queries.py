import geopandas as gpd
from app.database import engine


def get_nearby_fires(lat: float, lon: float, radius_km: float):
    sql = f"""
        SELECT "FIRE_NAME", "YEAR_", "GIS_ACRES", geometry
        FROM fire_perimeters
        WHERE ST_DWithin(
            ST_Transform(geometry, 4326)::geography,
            ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)::geography,
            {radius_km * 1000}
        )
        ORDER BY "GIS_ACRES" DESC
    """
    return gpd.read_postgis(sql, engine, geom_col="geometry")

def largest_fires_by_year(year: int):
    sql = f"""
        SELECT "FIRE_NAME", "YEAR_", "GIS_ACRES", geometry
        FROM fire_perimeters
        WHERE "YEAR_" = {year}
        ORDER BY "GIS_ACRES" DESC
        LIMIT 10
    """
    return gpd.read_postgis(sql, engine, geom_col="geometry")