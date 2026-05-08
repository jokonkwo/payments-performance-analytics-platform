# Scripts

---

## Pipeline Overview

```
generate_synthetic_data.py
└── data/landing/raw_charges.ndjson.gz
ingest_raw.py
└── data/processed/payments.duckdb (raw.stripe_charges)
dbt run
└── All models in dependency order
push_to_motherduck.py
└── payments_performance database (gold layer only)
```

---

## generate_synthetic_data.py

Generates realistic synthetic payment transaction data 
modeled after real payment processor API schemas.

```bash
python scripts/generate_synthetic_data.py \
    --num-merchants 50 \
    --seed 42
```

**Parameters:**
- `--num-merchants` — number of merchants to generate 
  (default: 50)
- `--seed` — random seed for reproducibility (default: 42)

**What it generates:**
- Merchant profiles derived dynamically from vertical and 
  size tier — no hardcoded profiles
- Daily transaction volumes via Poisson sampling with 
  seasonal variance, weekend multipliers, and holiday spikes
- BIN pool of 500-2000 unique BINs per merchant so the same 
  BINs repeat across transactions (realistic)
- All auth rates, CVC coverage, interchange rates, and 
  3DS distributions derived from merchant attributes

**Output:** `data/landing/raw_charges.ndjson.gz`  
**Expected runtime:** ~15 minutes for 50 merchants

---

## ingest_raw.py

Reads the compressed NDJSON file and loads all records into 
a DuckDB raw table as JSON blobs.

```bash
python scripts/ingest_raw.py
```

**Output:** `data/processed/payments.duckdb` 
table `raw.stripe_charges`  
**Expected runtime:** ~10 minutes for 8.25M rows

---

## push_to_motherduck.py

Exports the gold layer from local DuckDB to MotherDuck. 
Requires a MotherDuck token set as an environment variable.

```bash
export MOTHERDUCK_TOKEN="your_token_here"
python scripts/push_to_motherduck.py
```

**Tables pushed:**
- fct_payment_transactions
- mart_auth_rate_performance
- mart_interchange_performance
- mart_fraud_and_disputes
- mart_payment_optimization_recommendations
- dim_merchant
- dim_card_bin
- dim_date

**MotherDuck database:** payments_performance  
**Expected runtime:** ~20 minutes (dominated by fact table)

---

## data/ folders

```
data/
├── landing/     # generated NDJSON — gitignored, regenerate
│                # with generate_synthetic_data.py
└── processed/   # DuckDB file — gitignored, rebuilt with
                 # ingest_raw.py + dbt run
```

Neither folder is committed to git. The scripts are the 
source of truth — clone the repo and run the pipeline to 
reproduce the full dataset.
