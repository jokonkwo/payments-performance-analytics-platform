# Payments Performance Analytics Platform

**An end-to-end analytics engineering project transforming raw 
payment transaction events into merchant-facing optimization 
intelligence.**

---

## Live Demo

| | |
|---|---|
| 📊 **Dashboard** | [Payments Performance Analytics](https://app.motherduck.com/dives/b88b73e6-c16e-4459-bd20-ed72e6b4ae3c) *(free MotherDuck account required)* |
| 📖 **Data Docs** | [dbt lineage + model documentation](https://jokonkwo.github.io/payments-performance-analytics-platform/) |
| 🗄️ **Query the data** | See [MotherDuck access](#motherduck-access) below |

![Dashboard](docs/screenshots/dashboard.png)

---

## The Business Problem

Payment processors and merchants generate millions of 
authorization attempts every day. Without a structured data 
layer, the signals buried in that volume — why auth rates 
leak, which interchange tiers are avoidable, where fraud 
risk concentrates — stay invisible. Business teams are left 
making decisions from aggregate dashboards that cannot tell 
them which merchants, which channels, or which card segments 
to act on.

This platform models raw transaction events into a queryable, 
tested, and documented analytics layer that turns payment data 
into specific, quantified merchant recommendations.

---

## What This Project Demonstrates

- **End-to-end pipeline** — raw compressed NDJSON → DuckDB 
  raw table → dbt staging → intermediate → marts
- **Medallion architecture** — clear separation of concerns 
  at each layer with appropriate materialization strategies
- **Dimensional modeling** — star schema with fact and 
  dimension tables designed around authorization-grain data
- **dbt best practices** — column-level docs, schema tests, 
  generic and singular tests across all layers
- **Payments domain logic** — auth quality scoring, decline 
  classification, interchange tier assignment, and benchmark 
  gap calculations embedded in SQL
- **Recommendation layer** — prioritized, quantified 
  optimization opportunities per merchant, not just 
  descriptive aggregations
- **Scale** — 8.25M transactions across 50 dynamically 
  generated merchants across 15 verticals

---

## Business Questions This Platform Answers

1. **Auth rate leakage** — Which merchant segments have 
   authorization rates below vertical benchmarks, and what 
   is the estimated revenue impact of closing that gap?

2. **Interchange cost concentration** — Where are interchange 
   costs highest, and which combinations of funding source, 
   channel, and card type are driving above-benchmark 
   effective rates?

3. **Authentication data gaps** — Which transaction segments 
   lack sufficient CVC, AVS, or 3DS coverage, and what is 
   the risk exposure created by those gaps?

4. **Decline classification** — How are declines distributed 
   across hard, soft, and fraud categories? Which soft 
   declines are retryable?

5. **Token and 3DS adoption** — Where are network token and 
   3DS adoption gaps creating authorization rate drag and 
   cost optimization opportunities?

---

## The Data — From Raw to Insight

### Raw Input — Bronze Layer

One row per authorization attempt, as emitted by a payment 
processor API. Messy field names, mixed types, nested checks, 
null patterns. This is what the pipeline starts with:

| id | card_brand | card_funding | shopper_interaction | amount | currency | checks_cvc_check | outcome_type | interchange_rate_bps | radar_risk_score |
|:---|:---|:---|:---|---:|:---|:---|:---|---:|---:|
| pi_vCoj6Yk... | visa | debit | pos | 5846 | usd | pass | authorized | 89 | 81 |
| pi_eW7DF8m... | visa | debit | pos | 6312 | usd | pass | authorized | 72 | 3 |
| pi_vWD5Kol... | discover | prepaid | pos | 5964 | usd | unchecked | authorized | 188 | 87 |
| pi_sDLOtUv... | amex | prepaid | pos | 7658 | usd | pass | authorized | 274 | 0 |
| pi_epSylOO... | visa | credit | pos | 4062 | usd | pass | authorized | 162 | 9 |

`amount` is in minor units (cents). `checks_cvc_check` uses 
Stripe's real API values. `interchange_rate_bps` is null on 
declines. This is the raw schema — no business logic applied.

### Gold Output — Optimization Recommendations

After raw → staging → intermediate → marts, the platform 
produces merchant-specific, quantified recommendations:

| merchant_name | recommendation_type | priority | affected_txns | annual_impact_usd | detail |
|:---|:---|:---|---:|---:|:---|
| Merchant_0047_Automotive | adopt_network_tokens | HIGH | 743,078 | $196.4M | High ecommerce/recurring volume not using network tokens |
| Merchant_0046_Realestate | improve_cvc_coverage | HIGH | 85,888 | $148.8M | High rate of transactions missing CVC data |
| Merchant_0008_Marketplace | adopt_network_tokens | HIGH | 721,936 | $59.6M | High ecommerce/recurring volume not using network tokens |
| Merchant_0046_Realestate | adopt_network_tokens | HIGH | 59,357 | $41.1M | High ecommerce/recurring volume not using network tokens |
| Merchant_0020_Automotive | adopt_network_tokens | HIGH | 165,986 | $30.7M | High ecommerce/recurring volume not using network tokens |
| Merchant_0047_Automotive | investigate_interchange_tier | MEDIUM | 178,403 | $29.5M | Significant volume qualifying at premium interchange tier |

The same raw transaction data that came in as JSON blobs 
comes out as specific, dollar-quantified actions a payments 
expert can walk into a merchant conversation with.

---

## Architecture
```
Raw NDJSON (S3 / cloud storage simulation)
│
▼
DuckDB raw table  ──  JSON unnesting, no transformation
│
▼
Staging  ──  Type casting, field renaming, deduplication
│
▼
Intermediate  ──  Payments domain logic and enrichment
│
▼
Marts  ──  Dimensional model, aggregations, benchmarks
│
▼
Optimization recommendations  ──  Quantified merchant actions
```

See [models/README.md](models/README.md) for full data model 
documentation and [docs/README.md](docs/README.md) for metric 
definitions and production architecture notes.

---

## Data Overview

| Attribute | Detail |
|---|---|
| Merchants | 50 dynamically generated across 15 verticals |
| Size tiers | Enterprise, large, mid, small |
| Volume | 8.25M authorization attempts |
| Period | 2024-01-01 to 2024-12-31 |
| Grain | One row per authorization attempt |
| Schema | Grounded in real payment processor API field structures |

Verticals: retail, QSR, subscription, healthcare, travel, 
marketplace, grocery, gaming, education, beauty, automotive, 
real estate, nonprofit, B2B SaaS, logistics.

---

## MotherDuck Access

Query the gold layer directly using DuckDB or MotherDuck 
(free account required):

```sql
ATTACH 'md:_share/payments_performance_jokonkwo/5ffa01f6-e26b-4e86-b999-79c010cdc71d';

-- Auth rate gaps by merchant and channel
SELECT 
    a.merchant_account_id,
    m.merchant_name,
    a.shopper_interaction,
    ROUND(AVG(a.auth_rate) * 100, 1) as avg_auth_rate_pct,
    ROUND(AVG(a.auth_rate_vs_benchmark) * 100, 1) as gap_vs_benchmark_pct,
    ROUND(SUM(a.potential_revenue_at_risk_cents) / 100.0, 0) 
        as revenue_at_risk_usd
FROM payments_performance.mart_auth_rate_performance a
JOIN payments_performance.dim_merchant m 
    ON a.merchant_account_id = m.merchant_account_id
GROUP BY 1, 2, 3
ORDER BY gap_vs_benchmark_pct ASC
LIMIT 15;
```

See [scripts/README.md](scripts/README.md) for the full list 
of available tables.

---

## Running Locally

See [scripts/README.md](scripts/README.md) for full setup 
instructions.

**Quick start:**
```bash
git clone https://github.com/jokonkwo/payments-performance-analytics-platform.git
cd payments-performance-analytics-platform
pip install -r requirements.txt
python scripts/generate_synthetic_data.py --num-merchants 50 --seed 42
python scripts/ingest_raw.py
dbt deps --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

---

## Data Disclaimer

Transaction data is synthetically generated to mirror real 
payment processor event schemas. Field names and structures 
are grounded in publicly documented payment processor APIs. 
Interchange rates are derived from published Visa and 
Mastercard interchange schedules, not proprietary fee data. 
This project is intended for portfolio and educational 
purposes.
