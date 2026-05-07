# Payments Performance Analytics Platform

## Project Overview
This is a payments analytics dbt project using DuckDB as the warehouse. It simulates the data layer a Stripe Global Payments Performance (GPP) Analytics Engineer would build to help merchants diagnose authorization rate leakage, interchange cost drivers, and payment optimization opportunities.

## Tech Stack
- **Data generation**: Python (scripts/generate_synthetic_data.py)
- **Warehouse**: DuckDB (data/processed/payments.duckdb)
- **Transformation**: dbt-duckdb
- **Data**: ~1M synthetic Stripe-like payment records across 5 merchants

## Data Pipeline
NDJSON (data/landing/) -> DuckDB raw table (raw.stripe_charges) -> dbt models

## Model Dependency Order
raw -> staging -> intermediate -> marts

## Common Commands

### Generate synthetic data
```bash
python scripts/generate_synthetic_data.py
```

### Load into DuckDB
```bash
python scripts/ingest_raw.py
```

### Install dbt packages
```bash
dbt deps --profiles-dir .
```

### Run all models
```bash
dbt run --profiles-dir .
```

### Run tests
```bash
dbt test --profiles-dir .
```

### Run specific model
```bash
dbt run --select model_name --profiles-dir .
```

## Key Business Context
This platform helps Stripe GPP AEs walk into merchant conversations armed with data about:
- Auth rate gaps vs benchmarks by channel
- CVC/AVS coverage issues driving declines
- Network token adoption opportunities
- Interchange cost optimization by funding type
- Dispute rate analysis by risk segment

## Merchants
- MERCH_001 LuxeCart: Premium ecommerce, 350K txns, auth rate issue from missing CVC on guest checkouts
- MERCH_002 QuickServe: QSR/POS, 280K txns, healthy auth rates
- MERCH_003 StreamSub: Subscription, 180K txns, stale credentials on renewals
- MERCH_004 GlobalGoods: Cross-border, 120K txns, 3DS friction on EU cards
- MERCH_005 MedPay: Healthcare MOTO, 70K txns, prepaid/HSA card declines
