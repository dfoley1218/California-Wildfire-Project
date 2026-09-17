
import time

import geopandas as gpd
import pandas as pd
from sqlalchemy import text

from app.database import engine

STATE_SHP = "data/raw/tl_2023_us_state.shp"

# ST_HexagonGrid's size argument is the hexagon EDGE length, so a 2000 m edge
# gives cells of 10.39 km2, measuring 3.46 km flat-to-flat.

HEX_EDGE_M = 2000

BUILD_GRID_SQL = f"""
DROP TABLE IF EXISTS grid_cells;

CREATE TABLE grid_cells AS
SELECT
    row_number() OVER (ORDER BY h.i, h.j) AS cell_id,
    h.i,
    h.j,
    h.geom AS geometry
FROM ca_boundary b
CROSS JOIN ST_HexagonGrid({HEX_EDGE_M}, b.geometry) AS h
WHERE ST_Intersects(b.geometry, h.geom);

-- CREATE TABLE AS leaves the column as untyped `geometry`, which reports SRID 0
-- in geometry_columns and loses the CRS on export even though the values are 3310.
ALTER TABLE grid_cells ALTER COLUMN geometry TYPE geometry(Polygon, 3310);

ALTER TABLE grid_cells ADD PRIMARY KEY (cell_id);
CREATE INDEX grid_cells_geom_idx ON grid_cells USING GIST (geometry);
ANALYZE grid_cells;
"""


def load_ca_boundary():
    states = gpd.read_file(STATE_SHP)
    ca = states[states["STUSPS"] == "CA"][["STUSPS", "NAME", "geometry"]].to_crs(3310)
    ca.to_postgis("ca_boundary", engine, if_exists="replace", index=False)
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ca_boundary_geom_idx "
                "ON ca_boundary USING GIST (geometry)"
            )
        )
        conn.execute(text("ANALYZE ca_boundary"))
    print(f"=== ca_boundary loaded from {STATE_SHP} (EPSG:3310) ===")


def build_grid():
    print(f"\n=== building grid_cells ({HEX_EDGE_M} m hexagon edge) ===")
    start = time.time()
    with engine.begin() as conn:
        conn.execute(text(BUILD_GRID_SQL))
    print(f"built in {time.time() - start:.1f}s")


def report_grid():
    stats = pd.read_sql(
        """
        SELECT
            count(*) AS cells,
            min(ST_Area(geometry)) / 1e6 AS min_area_km2,
            max(ST_Area(geometry)) / 1e6 AS max_area_km2,
            sum(ST_Area(geometry)) / 1e6 AS grid_area_km2
        FROM grid_cells
        """,
        engine,
    ).iloc[0]
    ca_area = pd.read_sql(
        "SELECT ST_Area(geometry) / 1e6 AS km2 FROM ca_boundary", engine
    ).iloc[0]["km2"]

    print("\n=== grid_cells ===")
    print(f"cells: {int(stats['cells'])}")
    print(f"cell area: {stats['min_area_km2']:.2f}-{stats['max_area_km2']:.2f} km2 (equal-area, unclipped)")
    print(f"grid covers {stats['grid_area_km2']:,.0f} km2 vs California's {ca_area:,.0f} km2 "
          f"({stats['grid_area_km2'] / ca_area - 1:+.1%} from fringe cells overhanging the border)")


def benchmark_spatial_join():
    """Time the Task 1.4-style join so the cost of later steps is known, not guessed."""
    print("\n=== spatial join benchmark ===")
    for table, label in [("fires_test", "554 perimeters"), ("fire_perimeters", "22,810 perimeters")]:
        start = time.time()
        matched = pd.read_sql(
            f"""
            SELECT count(DISTINCT g.cell_id) AS n
            FROM grid_cells g
            JOIN {table} f ON ST_Intersects(g.geometry, f.geometry)
            """,
            engine,
        ).iloc[0]["n"]
        elapsed = time.time() - start
        print(f"{table} ({label}): {matched} cells touched, {elapsed:.1f}s")


if __name__ == "__main__":
    load_ca_boundary()
    build_grid()
    report_grid()
    benchmark_spatial_join()
