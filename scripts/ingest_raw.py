"""
Ingest raw_charges.ndjson.gz into DuckDB as raw.stripe_charges.
"""
import gzip
import json
import os
import sys
from datetime import datetime, timezone

import duckdb

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(REPO_ROOT, "data", "landing", "raw_charges.ndjson.gz")
DB_PATH = os.path.join(REPO_ROOT, "data", "processed", "payments.duckdb")


def main():
    print("=" * 60)
    print("Payments Raw Ingestion — DuckDB Loader")
    print("=" * 60)

    if not os.path.exists(INPUT_PATH):
        print(f"ERROR: Input file not found: {INPUT_PATH}")
        sys.exit(1)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    print(f"Source: {INPUT_PATH}")
    print(f"Target: {DB_PATH}")

    con = duckdb.connect(DB_PATH)

    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.stripe_charges (
            raw_payload  VARCHAR,
            _ingested_at TIMESTAMP,
            _source_file VARCHAR
        )
    """)

    # Truncate if re-running
    con.execute("DELETE FROM raw.stripe_charges")

    source_file = os.path.basename(INPUT_PATH)
    ingested_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    print("Reading and loading records...")

    CHUNK_SIZE = 50000
    chunk = []
    total = 0

    with gzip.open(INPUT_PATH, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunk.append((line, ingested_at, source_file))
            if len(chunk) >= CHUNK_SIZE:
                con.executemany(
                    "INSERT INTO raw.stripe_charges VALUES (?, ?, ?)", chunk
                )
                total += len(chunk)
                chunk = []
                print(f"  Loaded {total:,} rows...")

        if chunk:
            con.executemany(
                "INSERT INTO raw.stripe_charges VALUES (?, ?, ?)", chunk
            )
            total += len(chunk)

    # Verify
    result = con.execute("SELECT COUNT(*) FROM raw.stripe_charges").fetchone()
    row_count = result[0]

    print(f"\nVerification: {row_count:,} rows in raw.stripe_charges")

    # Quick sanity sample
    sample = con.execute("""
        SELECT
            json_extract_string(raw_payload, '$.merchant_name') AS merchant,
            COUNT(*) AS cnt
        FROM raw.stripe_charges
        GROUP BY 1
        ORDER BY 2 DESC
    """).fetchall()

    print("\nRow counts by merchant:")
    for row in sample:
        print(f"  {row[0]}: {row[1]:,}")

    con.close()
    print(f"\nDone. Database: {DB_PATH}")


if __name__ == "__main__":
    main()
