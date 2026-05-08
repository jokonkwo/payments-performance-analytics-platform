# Payments Performance Analytics Platform

**An end-to-end analytics engineering project transforming raw payment transaction events into merchant-facing optimization intelligence.**

---

## The Business Problem

Payment processors and merchants generate millions of authorization attempts every day. Without a structured data layer sitting beneath that volume, the signals buried in the noise — why auth rates leak, which interchange tiers are avoidable, where fraud risk concentrates — stay invisible. Business teams are left making decisions from aggregate dashboards that can't tell them *which* merchants, *which* channels, or *which* card segments to act on.

This platform models raw transaction events into a queryable, tested, and documented analytics layer that turns payment data into specific, quantified merchant recommendations — the kind a payments-focused analytics engineer or account executive would walk into a merchant conversation with.

---

## 🔗 Interactive Demo

📖 **Data Docs** (dbt lineage + model documentation): [https://jokonkwo.github.io/payments-performance-analytics-platform/](https://jokonkwo.github.io/payments-performance-analytics-platform/)

📊 **Live Data** (MotherDuck — coming soon): [Coming soon]

---

## What This Project Demonstrates

This is built for a technical reviewer who wants to assess analytics engineering depth. Here is what the project explicitly covers:

- **End-to-end pipeline** from raw compressed NDJSON events to governed, documented marts
- **Medallion architecture** — raw → staging → intermediate → marts, with clear separation of concerns at each layer
- **Dimensional modeling** — fact and dimension tables designed around authorization-grain transaction data
- **dbt best practices** — column-level documentation, schema tests, generic and singular tests, and metric definitions in YAML
- **Domain logic in SQL** — authorization quality scoring, decline classification (hard vs. soft vs. fraud), interchange tier assignment, and benchmark gap calculations embedded directly in transformation models
- **Recommendation layer** — a mart that produces prioritized, quantified optimization opportunities per merchant segment, not just descriptive aggregations
- **Designed for scale** — 10M+ transactions across 50+ dynamically generated merchants, with the generation logic parameterized and reproducible

---

## Business Questions This Platform Answers

These are the questions a payments-adjacent business team would bring to the data layer:

1. **Authorization rate leakage** — Which merchant segments have authorization rates below vertical benchmarks, and what is the estimated revenue impact of closing that gap?

2. **Interchange cost concentration** — Where are interchange costs highest, and which combinations of funding source, channel, and card type are driving above-benchmark effective rates?

3. **Authentication data gaps** — Which transaction segments lack sufficient CVC, AVS, or 3DS coverage, and what is the risk exposure created by those gaps?

4. **Decline classification** — How are declines distributed across hard, soft, and fraud categories? Which soft declines are retryable, and what does the retry opportunity look like at scale?

5. **Token and 3DS adoption** — Where are network token and 3DS adoption gaps creating authorization rate drag and cost optimization opportunities that the merchant has not yet captured?

---

## Data Model Overview

| Attribute | Detail |
|---|---|
| Merchant portfolio | 50 dynamically generated merchants across 15 payment verticals and 4 size tiers |
| Volume | ~10M authorization attempts across 12 months of 2024 |
| Grain | One row per authorization attempt |
| Schema | Grounded in real payment processor API field structures and published network interchange programs |

Verticals covered include retail, QSR, subscription, healthcare, travel, marketplace, grocery, gaming, education, beauty, automotive, real estate, nonprofit, B2B SaaS, and logistics. Merchants are generated with realistic attributes — channel mix, average order value, auth rate, card funding mix, geographic distribution, and dispute rate — all derived from vertical and size tier, not hardcoded.

---

## Architecture

```
Raw NDJSON (S3 / cloud storage simulation)
         │
         ▼
DuckDB raw table  ──  JSON unnesting, no transformation
         │
         ▼
Staging  ──  Type casting, field renaming, deduplication, null handling
         │
         ▼
Intermediate  ──  Payments domain logic, enrichment, classification
         │
         ▼
Marts  ──  Dimensional model, aggregations, benchmark comparisons
         │
         ▼
Optimization recommendations  ──  Prioritized, quantified merchant actions
```

---

## Layer Documentation

### `raw/`

The raw layer reads compressed NDJSON files from local storage and loads them into a DuckDB table without any transformation. The schema mirrors what a payment processor API would emit — one record per authorization attempt, with nested fields for card checks, 3DS outcome, radar risk scoring, and interchange metadata. Nothing is renamed or interpreted here. The raw layer exists so the rest of the pipeline has a stable, auditable source to build from.

### `staging/`

Staging is where raw events become typed, trusted records. Field names are standardized, timestamps are cast to proper types, boolean flags are normalized, and null patterns are made consistent. A deduplication step removes any duplicate payment intent IDs before data flows downstream. This layer is what all intermediate and mart models build on — it acts as the contract between ingestion and analytics.

### `intermediate/`

The intermediate layer is where payments domain logic lives. Raw authorization outcomes are classified into hard declines, soft declines, and fraud blocks. CVC and AVS checks are scored for quality. 3DS outcomes are interpreted alongside network token flags to produce enriched authorization quality signals per transaction. Card BIN metadata, merchant attributes, and channel context are joined here, resulting in a single enriched transaction spine that the mart layer can aggregate from cleanly.

### `marts/`

The mart layer is the analytical output. It includes:

- **`fct_payment_transactions`** — the core fact table at authorization-attempt grain, with all enriched fields from intermediate
- **`dim_merchant`**, **`dim_card_bin`**, **`dim_date`** — conformed dimensions used consistently across all aggregation models
- **`mart_auth_rate_performance`** — authorization rate by merchant, channel, and card segment, compared to vertical benchmarks with estimated revenue impact of gap closure
- **`mart_interchange_performance`** — effective interchange rate by funding type, card brand, and channel; flags above-benchmark segments
- **`mart_fraud_and_disputes`** — dispute rate, fraud signal distribution, and decline breakdown by risk category and merchant segment
- **`mart_payment_optimization_recommendations`** — a prioritized, merchant-level recommendation table with quantified impact estimates covering auth rate, interchange cost, token adoption, and authentication coverage

### `metrics.yml`

Governed metric definitions using the dbt Semantic Layer format. Key business metrics — authorization rate, gross payment volume, effective interchange rate, dispute rate, CVC coverage — are defined once with canonical logic and reusable across any downstream consumption layer, including BI tools and notebooks.

---

## Key Metric Definitions

**Gross Payment Volume (GPV)** — The total USD value of authorized and captured transactions across a time period. The top-line volume metric for any payment business.

**Authorization Rate** — The share of attempted transactions that result in a network approval. Calculated as approved authorizations divided by total attempts. Even a 1–2 percentage point gap from benchmark can represent significant revenue leakage at scale.

**Effective Interchange Rate (bps)** — The actual blended interchange cost as a basis point rate, calculated across all authorized transactions. Because interchange varies by card type, funding source, channel, and program tier, the effective rate tells you more than any single posted rate.

**CVC Coverage Rate** — The proportion of transactions where a CVC check was submitted and returned a pass result. Low CVC coverage is a common driver of soft declines and elevated interchange in card-not-present channels.

**Network Token Coverage Rate** — The share of transactions processed using a network token rather than a raw PAN. Higher token coverage is associated with improved authorization rates and, in some programs, reduced interchange.

**Dispute Rate** — Disputes initiated as a percentage of authorized transactions. Tracked by merchant segment, vertical, and risk category to separate structural risk from specific transaction patterns.

**Cost Per Transaction** — Total processing cost (interchange + network fees) divided by transaction count. Useful for benchmarking across channels and card mix, and for quantifying the cost impact of mix shifts.

---

## Running Locally

### Prerequisites

Python 3.9+ and git. All other dependencies install via pip.

### Steps

**1. Clone the repository and install dependencies**

```bash
git clone <repo-url>
cd payments-performance-analytics-platform
pip install -r requirements.txt
```

**2. Generate synthetic transaction data**

This creates ~10M transactions across 50 merchants and writes them to `data/landing/raw_charges.ndjson.gz`. The `--seed` flag makes output reproducible; `--num-merchants` controls portfolio size.

```bash
python scripts/generate_synthetic_data.py --num-merchants 50 --seed 42
```

**3. Load raw data into DuckDB**

Reads the compressed NDJSON file and loads it into a local DuckDB database at `data/processed/payments.duckdb`.

```bash
python scripts/ingest_raw.py
```

**4. Install dbt dependencies**

Downloads the dbt packages declared in `packages.yml` (DuckDB adapter and any utilities).

```bash
dbt deps --profiles-dir .
```

**5. Run all dbt models**

Executes the full transformation pipeline — raw → staging → intermediate → marts — in dependency order. DuckDB runs in-process; no external database or credentials needed.

```bash
dbt run --profiles-dir .
```

**6. Run data quality tests**

Executes the tests defined in schema YAML files: not-null, uniqueness, accepted-value, and referential integrity checks across all layers.

```bash
dbt test --profiles-dir .
```

**7. Run a specific model (optional)**

```bash
dbt run --select mart_auth_rate_performance --profiles-dir .
```

---

## Data Disclaimer

Transaction data in this project is synthetically generated to mirror real payment processor event schemas. Field names, structures, and outcome codes are grounded in publicly documented payment processor APIs. Interchange rates are derived from published Visa and Mastercard interchange schedules, not proprietary fee data. Merchant profiles and transaction patterns are simulated; any resemblance to actual merchant data is coincidental. This project is intended for portfolio and educational purposes.
