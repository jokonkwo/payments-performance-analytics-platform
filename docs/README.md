# Documentation

---

## Metric Definitions

**Gross Payment Volume (GPV)** — Total USD value of authorized 
and captured transactions. The top-line volume metric for any 
payment business. Defined as `SUM(amount_usd_cents) / 100`.

**Authorization Rate** — Share of attempted transactions that 
result in a network approval. Calculated as authorized count 
divided by total attempts. A 1-2 percentage point gap from 
benchmark can represent significant revenue leakage at scale.

**Effective Interchange Rate (bps)** — Actual blended 
interchange cost as a basis point rate across all authorized 
transactions. Because interchange varies by card type, funding 
source, channel, and program tier, the effective rate tells 
you more than any single posted rate.

**CVC Coverage Rate** — Proportion of transactions where a 
CVC check was submitted and returned a pass result. Low CVC 
coverage is a common driver of soft declines and elevated 
interchange in card-not-present channels.

**Network Token Coverage Rate** — Share of transactions 
processed using a network token rather than a raw PAN. Higher 
token coverage is associated with improved authorization rates 
and reduced interchange in some programs.

**Dispute Rate** — Disputes initiated as a percentage of 
authorized transactions. Tracked by merchant segment, 
vertical, and risk category to separate structural risk from 
specific transaction patterns.

**Cost Per Transaction** — Total processing cost (interchange 
+ network fees) divided by transaction count. Useful for 
benchmarking across channels and quantifying the cost impact 
of card mix shifts.

---

## Layer Documentation

### raw/
Reads compressed NDJSON from local storage and unnests JSON 
into typed columns using DuckDB json_extract functions. No 
business logic. One view model that makes the raw payload 
queryable as structured columns.

### staging/
Cleans, deduplicates, and standardizes raw fields. 
Deduplication on payment_intent_id, timestamp casting, 
boolean normalization, null handling, and outcome_type 
standardization. This layer is the contract between ingestion 
and analytics — all downstream models build from here.

### intermediate/
Applies payments domain logic. Auth quality scoring 
(fully_authenticated → unauthenticated), decline 
categorization (hard/soft/fraud), interchange tier 
classification (optimized/standard/premium), network token 
opportunity flags, and 3DS opportunity flags. This is where 
raw transaction data becomes payments-intelligent data.

### marts/
Business-ready aggregations and dimensional model. Each mart 
answers a specific question the GTM team needs. Fact table 
stays at transaction grain. Aggregation marts group by 
merchant, channel, card type, and time period.

---

## Production Architecture Notes

This project uses DuckDB for local development. In a 
production environment:

- **Ingestion** — Kafka or Fivetran replacing the custom 
  Python script; raw events stream directly to the warehouse
- **Warehouse** — Snowflake or BigQuery with date partitioning 
  and merchant clustering replacing DuckDB
- **Incremental models** — staging and intermediate would use 
  dbt incremental materialization with created_at watermarks, 
  processing only new records on each run
- **Retention** — bronze layer maintained on a 13-month 
  rolling window aligned with payment network dispute windows; 
  full history archived in S3 or GCS
- **Sharing** — Snowflake Data Sharing or BigQuery Authorized 
  Views replacing the MotherDuck push script
