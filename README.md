# California Wildfire Risk & Impact API

A production-grade geospatial project that analyzes California wildfire perimeters and serves the results through a REST API. It pairs a series of hands-on geospatial analysis notebooks (GeoPandas → Rasterio → PostGIS) with a [FastAPI](https://fastapi.tiangolo.com/) application backed by a PostGIS database, exposing spatial queries over **22,800+ CAL FIRE wildfire perimeters (1878–2024)** and **NASA FIRMS satellite fire detections** from the 2025 Los Angeles fires.

> **Why this project exists.** I lived in Santa Monica during the January 2025 Los Angeles wildfires. This project is both a personal response to that experience and a portfolio piece built toward geospatial software engineering work — it covers the full pipeline from raw geodata to a deployable spatial API.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Data Sources](#data-sources)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [The API](#the-api)
- [The Notebooks](#the-notebooks)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [References](#references)

---

## Features

- **Spatial proximity search** — find every historical fire perimeter within *N* kilometers of any latitude/longitude using PostGIS `ST_DWithin`.
- **GeoJSON output** — return fire perimeters as standards-compliant GeoJSON (WGS84), ready to drop into Leaflet, Mapbox, QGIS, or [geojson.io](https://geojson.io).
- **Aggregate statistics** — total acres burned, fire counts, and per-year breakdowns across the full historical record.
- **Satellite fire detections** — query NASA FIRMS VIIRS active-fire points near a location.
- **Health checks** — a `/health` endpoint that verifies live database connectivity.
- **Interactive analysis notebooks** — six notebooks covering CRS transformations, buffer/intersection analysis, raster elevation/slope, interactive Leafmap visualization, and PostGIS integration.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **API framework** | FastAPI + Uvicorn |
| **Spatial database** | PostgreSQL + PostGIS |
| **ORM / DB access** | SQLAlchemy, psycopg2 |
| **Geospatial (Python)** | GeoPandas, Shapely, pyogrio, Rasterio |
| **Visualization** | Matplotlib, contextily, Folium, Leafmap, ipywidgets |
| **Config** | python-dotenv |
| **Testing** | pytest, httpx (via FastAPI `TestClient`) |

---

## Architecture

```
                    ┌─────────────────────────────┐
   HTTP request     │        FastAPI app          │
  ───────────────►  │         (app/main.py)       │
                    │   routes & response shaping  │
                    └──────────────┬──────────────┘
                                   │  calls query functions
                                   ▼
                    ┌─────────────────────────────┐
                    │        app/queries.py        │
                    │   parameterized SQL +        │
                    │   GeoPandas / pandas readers │
                    └──────────────┬──────────────┘
                                   │  SQLAlchemy engine
                                   ▼
                    ┌─────────────────────────────┐
                    │   PostgreSQL + PostGIS        │
                    │   • fire_perimeters (22,810)  │
                    │   • firms_fires (NASA FIRMS)  │
                    └─────────────────────────────┘
```

The application is intentionally split into three small modules:

- **[`app/main.py`](app/main.py)** — FastAPI route definitions. Each route is thin: it calls a query function and shapes the response.
- **[`app/queries.py`](app/queries.py)** — all SQL lives here, returning `pandas`/`GeoPandas` results.
- **[`app/database.py`](app/database.py)** — builds the SQLAlchemy engine from environment variables.

---

## Data Sources

| Dataset | Description | Source |
|---------|-------------|--------|
| **CAL FIRE Fire Perimeters** | 22,810 wildfire perimeters back to 1878 (`firep24_1` layer). Key fields: `FIRE_NAME`, `YEAR_`, `GIS_ACRES`. | [fire.ca.gov](https://www.fire.ca.gov/what-we-do/fire-resource-assessment-program/fire-perimeters) |
| **Prescribed Burns** | Prescribed burn perimeters (`rxburn24_1` layer in the same geodatabase). | Same geodatabase |
| **NASA FIRMS** | VIIRS S-NPP active-fire satellite detections, California, Jan–Mar 2025. Fields: `latitude`, `longitude`, `brightness`, `confidence`, `acq_date`. | [firms.modaps.eosdis.nasa.gov](https://firms.modaps.eosdis.nasa.gov/) |
| **US Census TIGER** | California state and place boundaries for context layers. | [census.gov TIGER 2023](https://www2.census.gov/geo/tiger/TIGER2023/STATE/) |

**Native coordinate system:** EPSG:3310 (California Albers). Geometries are transformed to EPSG:4326 (WGS84) on the way out of the API so GeoJSON output renders correctly on standard web maps.

> **Note:** Raw data (`data/raw/`) and processed rasters (`data/processed/*.tif`) are **not** committed to the repository (see [`.gitignore`](.gitignore)). Download the CAL FIRE geodatabase from the source above and place it at `data/raw/fire24_1.gdb`.

---

## Project Structure

```
ca-wildfire-project/
├── README.md                 # This file
├── requirements.txt          # Pinned Python dependencies
├── .gitignore
├── app/                      # FastAPI application
│   ├── __init__.py
│   ├── main.py               # API routes
│   ├── queries.py            # SQL query functions
│   └── database.py           # SQLAlchemy engine + env config
├── tests/                    # pytest test suite
│   ├── __init__.py
│   └── test_main.py
├── notebooks/                # Geospatial analysis notebooks (see "The Notebooks")
│   ├── 01_explore_fire_perimeters.ipynb
│   ├── 02_crs_transformations.ipynb
│   ├── 03_buffers_intersections.ipynb
│   ├── 04_rasterio_elevation.ipynb
│   ├── 05_leafmap_la_fires.ipynb
│   └── 06_postgis_integration.ipynb
├── outputs/                  # Generated artifacts (e.g. interactive HTML maps)
│   └── la_fires_2025.html
└── data/
    ├── raw/                  # Source geodatabase (gitignored)
    └── processed/            # Derived rasters/datasets (gitignored)
```

---

## Getting Started

### Prerequisites

- **Python 3.11+** (developed on 3.14)
- **PostgreSQL 14+ with the PostGIS extension** — required for the API. The notebooks 01–05 run without it; notebook 06 and the API require it.

### 1. Clone and create an environment

Because of GDAL/GEOS native dependencies, **conda is strongly recommended on Windows**:

```bash
conda create -n ca-wildfire python=3.11 geopandas -c conda-forge
conda activate ca-wildfire
```

Or with pip + venv:

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install --upgrade pip setuptools wheel
```

### 2. Install dependencies

Dependencies are pinned in [`requirements.txt`](requirements.txt):

```bash
pip install -r requirements.txt
```

> On Windows, if pip fails to build `geopandas`/`rasterio` from source, install the geospatial stack via conda-forge first (see step 1) and then run the command above for the remaining packages.

### 3. Configure the database connection

The app reads credentials from environment variables via a `.env` file (which is gitignored). Create one in the project root:

```env
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_NAME=wildfire_db
```

These are consumed in [`app/database.py`](app/database.py) to build the connection string:
`postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}`

### 4. Load the data into PostGIS

Run **[`notebooks/06_postgis_integration.ipynb`](notebooks/06_postgis_integration.ipynb)** to create the `fire_perimeters` and `firms_fires` tables and load the geodatabase + FIRMS data into PostGIS.

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

Then open the interactive docs:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## The API

Base URL (local): `http://127.0.0.1:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root welcome message. |
| `GET` | `/health` | Database connectivity check (`SELECT 1`). |
| `GET` | `/fires/nearby?lat=&lon=&radius_km=` | Fire perimeters within `radius_km` of a point (`ST_DWithin`). |
| `GET` | `/fires/largest?year=` | Top 10 fires by acreage for a given year. |
| `GET` | `/fires/summary` | Totals: fire count, total/avg acres, earliest & latest year. |
| `GET` | `/fires/stats_by_year` | Fire count + total acres grouped by year. |
| `GET` | `/fires/geojson/{fire_name}` | Fire perimeter(s) matching a name, as a GeoJSON FeatureCollection (WGS84). |
| `GET` | `/fires/{fire_name}` | Fire records matching a name (tabular, case-insensitive `ILIKE`). |
| `GET` | `/firms/nearby?lat=&lon=&radius_km=` | NASA FIRMS satellite detections near a point. |

### Example: nearby fires

```bash
curl "http://127.0.0.1:8000/fires/nearby?lat=34.01&lon=-118.49&radius_km=50"
```

```json
[
  { "FIRE_NAME": "PALISADES", "YEAR_": 2025, "GIS_ACRES": 23448.0 },
  { "FIRE_NAME": "WOOLSEY",   "YEAR_": 2018, "GIS_ACRES": 96949.0 }
]
```

### Example: fire perimeter as GeoJSON

```bash
curl "http://127.0.0.1:8000/fires/geojson/EATON"
```

Returns a GeoJSON `FeatureCollection`. Paste the response into [geojson.io](https://geojson.io) to see the Eaton Fire perimeter rendered on a map.

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": { "FIRE_NAME": "EATON", "YEAR_": 2025, "GIS_ACRES": 14056.261 },
      "geometry": { "type": "MultiPolygon", "coordinates": [ /* ... WGS84 lon/lat ... */ ] }
    }
  ]
}
```

> **Implementation note — route ordering.** Specific paths (`/fires/summary`, `/fires/largest`, `/fires/geojson/{fire_name}`) are declared *before* the catch-all `/fires/{fire_name}` so FastAPI matches them first.

---

## The Notebooks

The notebooks build up the geospatial skills the API depends on, in order:

| # | Notebook | What it covers |
|---|----------|----------------|
| 01 | [`01_explore_fire_perimeters`](notebooks/01_explore_fire_perimeters.ipynb) | Loading the geodatabase, choropleth mapping with log-normalized acreage, top-10 largest fires, state boundary layers. |
| 02 | [`02_crs_transformations`](notebooks/02_crs_transformations.ipynb) | CRS reprojections, centroid distance calculations to major CA cities, fires within 100 km of Los Angeles. |
| 03 | [`03_buffers_intersections`](notebooks/03_buffers_intersections.ipynb) | Buffering fire perimeters and spatially intersecting them with populated-place boundaries. |
| 04 | [`04_rasterio_elevation`](notebooks/04_rasterio_elevation.ipynb) | Merging elevation tiles, computing & visualizing slope, composite raster+vector maps, and writing a Cloud-Optimized GeoTIFF (COG). |
| 05 | [`05_leafmap_la_fires`](notebooks/05_leafmap_la_fires.ipynb) | Interactive Leafmap visualization of the 2025 Los Angeles fires (output: [`outputs/la_fires_2025.html`](outputs/la_fires_2025.html)). |
| 06 | [`06_postgis_integration`](notebooks/06_postgis_integration.ipynb) | Loading wildfire + NASA FIRMS data into PostGIS, building spatial queries, and finding which FIRMS detections fell inside LA fire perimeters. |

Launch any notebook with:

```bash
jupyter notebook notebooks/01_explore_fire_perimeters.ipynb
```

---

## Testing

The test suite uses FastAPI's `TestClient` (backed by httpx). Tests in [`tests/test_main.py`](tests/test_main.py) cover the root route and the shape of `/fires/nearby` responses.

```bash
pytest
```

> The endpoint tests hit the live database, so PostGIS must be running and populated for them to pass meaningfully.

---

## Roadmap

- [x] Geospatial analysis notebooks (GeoPandas, Rasterio, COG, Leafmap)
- [x] PostGIS integration & spatial queries
- [x] FastAPI app with proximity, stats, GeoJSON, and FIRMS endpoints
- [ ] `GET /fires/geojson/nearby` — nearby fires as a GeoJSON FeatureCollection
- [ ] `GET /risk?lat=&lon=` — wildfire risk score (0–100) combining proximity, history, and terrain
- [ ] Expand pytest coverage; add CI via GitHub Actions
- [ ] Dockerize (app + PostGIS) and deploy
- [ ] Group endpoints with FastAPI **tags**; add a Leaflet demo map

---

## References

- [GeoPandas Documentation](https://geopandas.org/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Rasterio Documentation](https://rasterio.readthedocs.io/)
- [Leafmap Documentation](https://leafmap.org/)
- [GeoJSON Specification (RFC 7946)](https://datatracker.ietf.org/doc/html/rfc7946)
- [EPSG:3310 — California Albers](https://epsg.io/3310)
- [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/)
</content>
</invoke>
