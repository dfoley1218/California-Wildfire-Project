-- CI test database seed
-- Creates fire_perimeters and firms_fires tables with minimal realistic data.
-- Geometries are stored in EPSG:4326 so ST_Transform(geometry, 4326) in queries is a no-op.

CREATE EXTENSION IF NOT EXISTS postgis;

-- -----------------------------------------------------------------------
-- fire_perimeters
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fire_perimeters (
    id          SERIAL PRIMARY KEY,
    "FIRE_NAME" TEXT,
    "YEAR_"     INTEGER,
    "GIS_ACRES" DOUBLE PRECISION,
    geometry    geometry(MultiPolygon, 4326)
);

CREATE INDEX IF NOT EXISTS fire_perimeters_geom_idx
    ON fire_perimeters USING GIST (geometry);

-- Palisades Fire 2025 — small representative polygon near Santa Monica
INSERT INTO fire_perimeters ("FIRE_NAME", "YEAR_", "GIS_ACRES", geometry) VALUES (
    'PALISADES', 2025, 23448.0,
    ST_Multi(ST_GeomFromText(
        'POLYGON((-118.60 34.00, -118.50 34.00, -118.50 34.10, -118.60 34.10, -118.60 34.00))',
        4326
    ))
);

-- Woolsey Fire 2018
INSERT INTO fire_perimeters ("FIRE_NAME", "YEAR_", "GIS_ACRES", geometry) VALUES (
    'WOOLSEY', 2018, 96949.0,
    ST_Multi(ST_GeomFromText(
        'POLYGON((-118.80 34.00, -118.70 34.00, -118.70 34.10, -118.80 34.10, -118.80 34.00))',
        4326
    ))
);

-- Eaton Fire 2025 — Altadena / Pasadena area
INSERT INTO fire_perimeters ("FIRE_NAME", "YEAR_", "GIS_ACRES", geometry) VALUES (
    'EATON', 2025, 14056.0,
    ST_Multi(ST_GeomFromText(
        'POLYGON((-118.10 34.15, -118.00 34.15, -118.00 34.25, -118.10 34.25, -118.10 34.15))',
        4326
    ))
);

-- Dixie Fire 2021 — Northern California, far from LA test coords
INSERT INTO fire_perimeters ("FIRE_NAME", "YEAR_", "GIS_ACRES", geometry) VALUES (
    'DIXIE', 2021, 963309.0,
    ST_Multi(ST_GeomFromText(
        'POLYGON((-121.20 40.00, -121.00 40.00, -121.00 40.20, -121.20 40.20, -121.20 40.00))',
        4326
    ))
);

-- Old fire from 1980 — tests recency factor scoring
INSERT INTO fire_perimeters ("FIRE_NAME", "YEAR_", "GIS_ACRES", geometry) VALUES (
    'OLD', 1980, 5000.0,
    ST_Multi(ST_GeomFromText(
        'POLYGON((-117.30 34.10, -117.20 34.10, -117.20 34.20, -117.30 34.20, -117.30 34.10))',
        4326
    ))
);

-- -----------------------------------------------------------------------
-- firms_fires
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS firms_fires (
    id         SERIAL PRIMARY KEY,
    latitude   DOUBLE PRECISION,
    longitude  DOUBLE PRECISION,
    brightness DOUBLE PRECISION,
    confidence TEXT,
    acq_date   DATE,
    geom       geometry(Point, 4326)
);

CREATE INDEX IF NOT EXISTS firms_fires_geom_idx
    ON firms_fires USING GIST (geom);

-- Detection near Santa Monica (inside Palisades area)
INSERT INTO firms_fires (latitude, longitude, brightness, confidence, acq_date, geom) VALUES (
    34.05, -118.55, 325.4, 'high', '2025-01-10',
    ST_SetSRID(ST_MakePoint(-118.55, 34.05), 4326)
);

-- Detection near Altadena (inside Eaton area)
INSERT INTO firms_fires (latitude, longitude, brightness, confidence, acq_date, geom) VALUES (
    34.20, -118.05, 310.1, 'high', '2025-01-10',
    ST_SetSRID(ST_MakePoint(-118.05, 34.20), 4326)
);

-- Detection far from LA test coords
INSERT INTO firms_fires (latitude, longitude, brightness, confidence, acq_date, geom) VALUES (
    40.10, -121.10, 290.5, 'nominal', '2021-07-15',
    ST_SetSRID(ST_MakePoint(-121.10, 40.10), 4326)
);
