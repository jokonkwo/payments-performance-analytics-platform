import os
import sys
import time

import duckdb

LOCAL_DB = "data/processed/payments.duckdb"
MD_DATABASE = "payments_performance"

TABLES = [
    "fct_payment_transactions",
    "mart_auth_rate_performance",
    "mart_interchange_performance",
    "mart_fraud_and_disputes",
    "mart_payment_optimization_recommendations",
    "dim_merchant",
    "dim_card_bin",
    "dim_date",
]


def main():
    token = os.environ.get("MOTHERDUCK_TOKEN")
    if not token:
        print("Error: MOTHERDUCK_TOKEN environment variable is not set.")
        print("Set it with: export MOTHERDUCK_TOKEN=<your token>")
        sys.exit(1)

    print(f"Connecting to local DuckDB at {LOCAL_DB}...")
    local = duckdb.connect(LOCAL_DB, read_only=True)

    print("Connecting to MotherDuck...")
    try:
        md = duckdb.connect(f"md:?motherduck_token={token}")
    except Exception as e:
        print(f"Error: Could not connect to MotherDuck — {e}")
        sys.exit(1)

    md.execute(f"CREATE DATABASE IF NOT EXISTS {MD_DATABASE}")
    md.execute(f"USE {MD_DATABASE}")

    total_rows = 0
    script_start = time.perf_counter()

    for table in TABLES:
        print(f"Pushing {table}...")
        t0 = time.perf_counter()

        df = local.execute(f"SELECT * FROM main.{table}").df()
        row_count = len(df)

        md.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM df")

        elapsed = time.perf_counter() - t0
        total_rows += row_count
        print(f"  {row_count:,} rows pushed in {elapsed:.2f}s")

    total_elapsed = time.perf_counter() - script_start
    print(f"\nDone. {total_rows:,} total rows pushed in {total_elapsed:.2f}s")

    local.close()
    md.close()


if __name__ == "__main__":
    main()
