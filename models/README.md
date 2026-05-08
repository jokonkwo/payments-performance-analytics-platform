# Data Models

---

## Star Schema

The mart layer implements a star schema centered on 
`fct_payment_transactions` at authorization-attempt grain. 
Dimension tables provide merchant, card, and date context.

```
                dim_date
                   │
dim_merchant ──── fct_payment_transactions ──── dim_card_bin
```

---

## Model Inventory

| Model | Layer | Materialization | Description |
|---|---|---|---|
| raw_stripe_charges | raw | view | JSON unnesting from raw payload |
| stg_stripe_charges | staging | table | Cleaned, typed, deduplicated |
| int_payment_enriched | intermediate | view | Payments domain logic |
| dim_date | marts | table | Date spine 2024-01-01 to 2024-12-31 |
| dim_merchant | marts | table | One row per merchant |
| dim_card_bin | marts | table | One row per unique BIN |
| fct_payment_transactions | marts | table | Core fact at attempt grain |
| mart_auth_rate_performance | marts | table | Auth rate vs benchmark |
| mart_interchange_performance | marts | table | Interchange cost analysis |
| mart_fraud_and_disputes | marts | table | Fraud and dispute patterns |
| mart_payment_optimization_recommendations | marts | table | Prioritized merchant actions |

---

## Dependency Order

```
raw.stripe_charges (source)
└── raw_stripe_charges
    └── stg_stripe_charges
        └── int_payment_enriched
            ├── fct_payment_transactions
            ├── dim_merchant
            ├── dim_card_bin
            ├── mart_auth_rate_performance
            ├── mart_interchange_performance
            ├── mart_fraud_and_disputes
            └── mart_payment_optimization_recommendations
```

---

## Running Individual Models

```bash
# Run a single model
dbt run --select mart_auth_rate_performance --profiles-dir .

# Run a model and all its upstream dependencies
dbt run --select +mart_auth_rate_performance --profiles-dir .

# Run all mart models
dbt run --select marts --profiles-dir .

# Run tests on a single model
dbt test --select mart_auth_rate_performance --profiles-dir .

# Full refresh (rebuilds all tables from scratch)
dbt run --profiles-dir . --full-refresh
```

---

## Key Modeling Decisions

**Auth quality scoring** — transactions are scored as 
fully_authenticated, cvc_only, postal_only, 
partially_authenticated, or unauthenticated based on the 
combination of CVC and AVS check results. This drives both 
the auth rate analysis and the interchange tier assignment.

**Decline categorization** — hard declines (lost/stolen card, 
invalid card number) are separated from soft declines 
(do_not_honor, insufficient_funds, velocity) and fraud blocks. 
Only soft declines are flagged as retryable opportunities.

**Benchmark auth rates** — benchmarks are set per 
vertical and channel combination based on industry-standard 
ranges, not derived from the data itself. This makes the gap 
analysis meaningful rather than circular.
