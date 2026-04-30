# Architecture

This project models transaction-level payment data into reusable analytical layers using an Analytics Engineering workflow.

## Layers

### Staging
Standardizes raw payment transaction data.

### Intermediate
Applies reusable business transformations and enrichment logic.

### Marts
Aggregates payment performance metrics for downstream analytics, optimization, and operational recommendations.

## Intended Stack

- DuckDB
- dbt
- SQL
- Python
- Tableau / BI Layer
