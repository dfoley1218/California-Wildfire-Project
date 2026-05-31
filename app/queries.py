import geopandas as gpd
import pandas as pd
from app.database import engine



def get_local_fires(lat: float, lon: float, radius_km: float):
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

def get_fire_by_name(fire_name: str):
    sql = f"""
        SELECT "FIRE_NAME", "YEAR_", "GIS_ACRES", geometry
        FROM fire_perimeters
        WHERE "FIRE_NAME" ILIKE '%%{fire_name}%%'
        ORDER BY "YEAR_" DESC
        """
    return gpd.read_postgis(sql, engine, geom_col="geometry")

def get_local_firms(lat: float, lon: float, radius_km: float):
    sql = f"""
        SELECT latitude, longitude, brightness, confidence, acq_date
        FROM firms_fires
        WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)::geography, {radius_km * 1000})
        ORDER BY acq_date DESC
    """
    return pd.read_sql(sql, engine)