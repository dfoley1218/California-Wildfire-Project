import os
import pandas as pd
import geopandas as gpd
import pystac
from shapely.geometry import box, mapping
from datetime import datetime, timezone
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

# build a single Item for a given year's exported GeoJSON asset
def build_year_item(year):
    year = int(year)
    path = f"data/stac_assets/fires_{year}.geojson"
    gdf = gpd.read_file(path)
    west, south, east, north = gdf.total_bounds
    bbox = [west, south, east, north]
    geometry = mapping(box(west, south, east, north))

    item = pystac.Item(
        id=f"fires-{year}",
        geometry=geometry,
        bbox=bbox,
        datetime=datetime(year, 1, 1, tzinfo=timezone.utc),
        properties={"fire_count": len(gdf)},
    )
    item.add_asset(
        "fires",
        pystac.Asset(
            href=os.path.abspath(path),
            media_type=pystac.MediaType.GEOJSON,
            roles=["data"],
        ),
    )
    return item

# wrap every year's Item into one Collection
def build_fire_collection():
    years = get_STAC_years()["YEAR_"].astype(int).tolist()
    items = [build_year_item(year) for year in years]

    west = min(item.bbox[0] for item in items)
    south = min(item.bbox[1] for item in items)
    east = max(item.bbox[2] for item in items)
    north = max(item.bbox[3] for item in items)
    start = min(item.datetime for item in items)
    end = max(item.datetime for item in items)

    collection = pystac.Collection(
        id="cal-fire-perimeters",
        description="CAL FIRE historical fire perimeters, grouped by year",
        extent=pystac.Extent(
            spatial=pystac.SpatialExtent([[west, south, east, north]]),
            temporal=pystac.TemporalExtent([[start, end]]),
        ),
        license="proprietary",
    )
    for item in items:
        collection.add_item(item)
    return collection

if __name__ == "__main__":
    collection = build_fire_collection()
    collection.normalize_hrefs("data/stac_catalog")
    for item in collection.get_items():
        item.validate()
    collection.validate()
    collection.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
    print(f"Saved {len(list(collection.get_items()))} items to data/stac_catalog")