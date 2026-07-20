# California Wildfire Risk & Impact API

[![Test](https://github.com/dfoley1218/California-Wildfire-Project/actions/workflows/test.yml/badge.svg)](https://github.com/dfoley1218/California-Wildfire-Project/actions/workflows/test.yml)
[![Live Demo](https://img.shields.io/badge/Live_Demo-Map_Explorer-2ea44f)](https://california-wildfire-project.pages.dev/)
[![Live API](https://img.shields.io/badge/Live_API-Swagger_Docs-1f6feb)](https://california-wildfire-project.onrender.com/docs)

**🗺️ [Explore the interactive map](https://california-wildfire-project.pages.dev/)** · **📖 [Try the live API](https://california-wildfire-project.onrender.com/docs)**

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
- [What's Next](#whats-next)
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
│   ├── scoring.py            # Risk-score logic (pure math, no DB)
│   └── database.py           # SQLAlchemy engine + env config
├── tests/                    # pytest test suite
│   ├── __init__.py
│   ├── test_main.py          # API route tests (TestClient)
│   └── test_scoring.py       # Risk-score unit tests (no DB)
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

The app reads a single **`DATABASE_URL`** connection string from a `.env` file (which is gitignored). Create one in the project root:

```env
DATABASE_URL=postgresql+psycopg2://your_user:your_password@localhost:5432/wildfire_db
```

This is consumed in [`app/database.py`](app/database.py). Using one URL keeps configuration simple and works directly with hosted Postgres providers (e.g. [Neon](https://neon.tech)), whose connection strings include SSL parameters:

```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

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

**Live:** `https://california-wildfire-project.onrender.com` — try the interactive docs at [**`/docs`**](https://california-wildfire-project.onrender.com/docs). *(Hosted on Render's free tier; the first request after a period of inactivity may take ~30–50s while the service wakes.)*

Base URL (local): `http://127.0.0.1:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Redirects to the interactive API docs (`/docs`). |
| `GET` | `/health` | Database connectivity check (`SELECT 1`). |
| `GET` | `/fires/nearby?lat=&lon=&radius_km=` | Fire perimeters within `radius_km` of a point (`ST_DWithin`). |
| `GET` | `/fires/largest?year=` | Top 10 fires by acreage for a given year. |
| `GET` | `/fires/summary` | Totals: fire count, total/avg acres, earliest & latest year. |
| `GET` | `/fires/stats_by_year` | Fire count + total acres grouped by year. |
| `GET` | `/fires/geojson/nearby?lat=&lon=&radius_km=` | Fires near a point as a GeoJSON FeatureCollection (WGS84). |
| `GET` | `/fires/geojson/{fire_name}` | Fire perimeter(s) matching a name, as a GeoJSON FeatureCollection (WGS84). |
| `GET` | `/fires/{fire_name}` | Fire records matching a name (tabular, case-insensitive `ILIKE`). |
| `GET` | `/firms/nearby?lat=&lon=&radius_km=` | NASA FIRMS satellite detections near a point. |
| `GET` | `/risk?lat=&lon=` | **Wildfire risk score (0–100)** for a location, with a factor breakdown. |

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

### Example: wildfire risk score

```bash
curl "http://127.0.0.1:8000/risk?lat=34.04&lon=-118.53"
```

```json
{
  "risk_score": 99.6,
  "factors": {
    "proximity": { "score": 100.0, "nearest_fire_km": 0.0, "nearest_fire": "PALISADES", "year": 2025 },
    "density":   { "score": 100.0, "fires_within_radius": 273 },
    "recency":   { "score": 98.0, "most_recent_year": 2025 }
  }
}
```

A point inside the 2025 Palisades burn area scores ~99.6; a remote point far from any fire history scores near 0. The response always returns the **factor breakdown** alongside the headline score, so the result is transparent rather than a black box.

> **Implementation note — route ordering.** Specific paths (`/fires/summary`, `/fires/largest`, `/fires/geojson/nearby`) are declared *before* the catch-all wildcards (`/fires/geojson/{fire_name}`, `/fires/{fire_name}`) so FastAPI matches the literal paths first.

---

## The Risk Model

The `/risk` endpoint computes a wildfire risk score from **0–100** by combining three factors, each normalized to 0–100 and then weighted:

```
risk = (proximity × 0.5) + (density × 0.3) + (recency × 0.2)
```

| Factor | What it measures | Sub-score formula |
|--------|------------------|-------------------|
| **Proximity** | Distance to the nearest historical fire (`ST_Distance`). | `max(0, 100 − km × (100 / 50))` — 0 km → 100, ≥ 50 km → 0 |
| **Density** | Count of fires within 20 km (`ST_DWithin` + `COUNT`). | `min(100, count × (100 / 20))` — saturates at 20 fires |
| **Recency** | Years since the most recent nearby fire. | `max(0, 100 − years × (100 / 50))` — this year → 100, ≥ 50 yrs → 0 |

The weights and thresholds are **named constants** at the top of [`app/scoring.py`](app/scoring.py), so they are easy to inspect, tune, and test.

> **On the weights — an honest note.** These weights are a **heuristic**, not trained values: they encode the domain assumption that recent, close fire activity is the strongest risk signal. The principled next step (see Roadmap) is to gather ground-truth burn outcomes and fit the weights with a logistic regression, so the data determines them rather than the author. Because the scoring logic is a pure function ([`calculate_risk_score`](app/scoring.py)) decoupled from the database queries, swapping in trained weights is a localized change — and the logic is unit-tested in [`tests/test_scoring.py`](tests/test_scoring.py) with no database required.

> **On implementation — two copies, one source of truth.** The live map
> (deployed separately on Cloudflare Pages) runs a client-side JavaScript
> port of this scoring logic for instant, no-network results while panning
> the map. The Python version in `app/scoring.py` above is canonical — it's
> the one covered by `tests/test_scoring.py`, and the JS is a manual port of
> it, not an independent implementation. If the two ever disagree, the
> Python version is correct.

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

```bash
pytest
```

The suite has two layers:

- **[`tests/test_scoring.py`](tests/test_scoring.py)** — unit tests for the risk-score logic. Because [`calculate_risk_score`](app/scoring.py) is pure math decoupled from the database, these run with **no PostGIS required** and cover the high-risk case, the low-risk case, the factor-breakdown structure, and score-bounds clamping.
- **[`tests/test_main.py`](tests/test_main.py)** — API route tests via FastAPI's `TestClient` (backed by httpx), covering the root route and the shape of `/fires/nearby` responses.

> The route tests in `test_main.py` hit the live database, so PostGIS must be running and populated for them to pass meaningfully. The scoring tests have no such dependency.

---

## What's Next

The core pipeline — notebooks, PostGIS, FastAPI, and the `/risk` endpoint — is
complete and tested. The scoring weights are currently a hand-set heuristic
(see [The Risk Model](#the-risk-model)); the next iteration is gathering
ground-truth burn outcomes and fitting them with a logistic regression instead.
Beyond that: adding terrain (slope/elevation) as a fourth risk factor via the
elevation raster already produced in the notebooks, indexing `ST_DWithin`
queries for performance, and deploying the API to a public URL alongside the
live map.

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
