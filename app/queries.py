import geopandas as gpd
import pandas as pd
from app.database import engine


def health_check():
    sql = f"""
        SELECT 1
    """
    try:
        pd.read_sql(sql, engine)
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

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

def fire_summary_stats():
    sql = f"""
        SELECT COUNT(*) AS total_fires, 
                SUM("GIS_ACRES") AS total_acres, 
                AVG("GIS_ACRES") AS avg_acres,
                MIN("YEAR_") AS earliest_year,
                MAX("YEAR_") AS latest_year
        FROM fire_perimeters
    """
    return pd.read_sql(sql, engine).iloc[0].to_dict()

def fire_stats_by_year():
    sql = f"""
        SELECT "YEAR_", COUNT(*) AS total_fires, SUM("GIS_ACRES") AS total_acres
        FROM fire_perimeters
        WHERE "YEAR_" IS NOT NULL
        GROUP BY "YEAR_"
        ORDER BY "YEAR_"
    """
    return pd.read_sql(sql, engine).to_dict(orient="records")

def get_fire_geojson_by_name(fire_name: str):
    # ST_Transform to 4326: GeoJSON spec requires WGS84 coordinates
    sql = f"""
        SELECT "FIRE_NAME", "YEAR_", "GIS_ACRES", ST_Transform(geometry, 4326) AS geometry
        FROM fire_perimeters
        WHERE "FIRE_NAME" ILIKE '%%{fire_name}%%'
        ORDER BY "YEAR_" DESC
        """
    gdf = gpd.read_postgis(sql, engine, geom_col="geometry")
    return gdf

def get_fire_geojson_nearby(lat: float, lon: float, radius_km: float):
    sql = f"""
        SELECT "FIRE_NAME", "YEAR_", "GIS_ACRES", ST_Transform(geometry, 4326) AS geometry
        FROM fire_perimeters
        WHERE ST_DWithin(
            ST_Transform(geometry, 4326)::geography,
            ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)::geography,
            {radius_km * 1000}
        )
        ORDER BY "YEAR_" DESC
    """
    gdf = gpd.read_postgis(sql, engine, geom_col="geometry")
    return gdf

