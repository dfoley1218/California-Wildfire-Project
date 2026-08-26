import pandas as pd
import geopandas as gpd
from app.database import engine

# determine the years for which we have fire perimeter data
def get_STAC_years():
    sql = """
        SELECT DISTINCT "YEAR_"
        FROM fire_perimeters
        WHERE "YEAR_" IS NOT NULL
        ORDER BY "YEAR_" DESC

        """
    stac_years = pd.read_sql(sql, engine)
    return stac_years

if __name__ == "__main__":
    print(get_STAC_years())

# export fire perimeters for a given year to data/stac_assets/fires_{year}.geojson
def export_year_to_geojson(year):
    year=int(year) 
    # ensure year is an integer
    sql = f"""
        SELECT "FIRE_NAME", "YEAR_", "GIS_ACRES",
            ST_TRANSFORM(geometry, 4326) AS geometry
            FROM fire_perimeters
            WHERE "YEAR_" = {year}
            ORDER BY "YEAR_" DESC
            """
    gdf = gpd.read_postgis(sql, engine, geom_col="geometry")
    gdf.to_file(f"data/stac_assets/fires_{year}.geojson", driver="GeoJSON")

if __name__ == "__main__":
    for year in get_STAC_years()["YEAR_"]:
        export_year_to_geojson(year)
