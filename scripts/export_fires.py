import geopandas as gpd
from app.database import engine

sql = """
    SELECT "FIRE_NAME", "YEAR_", "GIS_ACRES",
        ST_TRANSFORM(geometry, 4326) AS geometry
    FROM fire_perimeters
    WHERE "YEAR_" >= 2018 and "GIS_ACRES" > 1000
    ORDER BY "GIS_ACRES" DESC
"""
gdf = gpd.read_postgis(sql, engine, geom_col="geometry")

gdf["geometry"] = gdf.simplify(0.0005)

gdf.to_file("frontend/fires.geojson", driver="GeoJSON")
print(f"Exported {len(gdf)} fires")

