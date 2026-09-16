import pandas as pd
from sqlalchemy import text
from app.database import engine

CREATE_VIEWS_SQL = """
CREATE OR REPLACE VIEW fires_train AS
SELECT * FROM fire_perimeters
WHERE "YEAR_" IS NOT NULL AND "YEAR_" <= 2023;

CREATE OR REPLACE VIEW fires_test AS
SELECT * FROM fire_perimeters
WHERE "YEAR_" IS NOT NULL AND "YEAR_" IN (2024, 2025);
"""


def print_schema():
    schema = pd.read_sql(
        """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'fire_perimeters'
        ORDER BY ordinal_position
        """,
        engine,
    )
    print("=== fire_perimeters schema ===")
    print(schema.to_string(index=False))


def create_views():
    with engine.begin() as conn:
        conn.execute(text(CREATE_VIEWS_SQL))
    print("\n=== views created ===")
    print("fires_train: \"YEAR_\" IS NOT NULL AND \"YEAR_\" <= 2023")
    print("fires_test:  \"YEAR_\" IS NOT NULL AND \"YEAR_\" IN (2024, 2025)")


def print_row_counts():
    total = pd.read_sql("SELECT COUNT(*) AS n FROM fire_perimeters", engine).iloc[0]["n"]
    train = pd.read_sql("SELECT COUNT(*) AS n FROM fires_train", engine).iloc[0]["n"]
    test = pd.read_sql("SELECT COUNT(*) AS n FROM fires_test", engine).iloc[0]["n"]
    excluded = total - train - test

    print("\n=== row counts ===")
    print(f"fire_perimeters (total): {total}")
    print(f"fires_train (<=2023):    {train}")
    print(f"fires_test (2024-2025):  {test}")
    print(f"excluded (null YEAR_):   {excluded}")
    assert train + test + excluded == total, "counts don't add up to total"


def print_year_quality_checks():
    print("\n=== YEAR_ data-quality checks ===")

    nulls = pd.read_sql(
        'SELECT COUNT(*) AS n FROM fire_perimeters WHERE "YEAR_" IS NULL', engine
    ).iloc[0]["n"]
    print(f"null YEAR_ rows: {nulls} (excluded from both views)")

    bounds = pd.read_sql(
        'SELECT MIN("YEAR_") AS min_year, MAX("YEAR_") AS max_year FROM fire_perimeters',
        engine,
    ).iloc[0]
    print(f"YEAR_ range: {bounds['min_year']:.0f}-{bounds['max_year']:.0f}")

    recent_counts = pd.read_sql(
        """
        SELECT "YEAR_", COUNT(*) AS n
        FROM fire_perimeters
        WHERE "YEAR_" IN (2023, 2024, 2025)
        GROUP BY "YEAR_"
        ORDER BY "YEAR_"
        """,
        engine,
    )
    print("rows per year, 2023-2025 (2025 is likely a partial year):")
    print(recent_counts.to_string(index=False))

    mismatches = pd.read_sql(
        """
        SELECT COUNT(*) AS n FROM fire_perimeters
        WHERE "YEAR_" IS NOT NULL AND "ALARM_DATE" IS NOT NULL
        AND "YEAR_" <> EXTRACT(YEAR FROM "ALARM_DATE")
        """,
        engine,
    ).iloc[0]["n"]
    print(f'rows where YEAR_ != EXTRACT(YEAR FROM ALARM_DATE): {mismatches}')

    null_alarm = pd.read_sql(
        'SELECT COUNT(*) AS n FROM fire_perimeters WHERE "ALARM_DATE" IS NULL', engine
    ).iloc[0]["n"]
    print(f"null ALARM_DATE rows: {null_alarm} (not used by this split, matters for date-based joins later)")


if __name__ == "__main__":
    print_schema()
    create_views()
    print_row_counts()
    print_year_quality_checks()
