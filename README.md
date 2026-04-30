# Payments Performance Analytics Platform

## Business Problem

Merchants often lack visibility into the operational drivers of payment processing costs, interchange fees, and transaction performance.

This project simulates an Analytics Engineering workflow for a payments optimization organization by transforming transaction-level payment data into reusable analytics marts, governed metrics, and operational recommendation layers.

## Project Goals

- Standardize transaction-level payment data into trusted analytical models
- Build reusable payment performance marts
- Define governed business metrics for payment optimization
- Surface operational recommendations for reducing interchange costs
- Demonstrate analytics engineering workflows using dbt, SQL, Python, and DuckDB

## Architecture

Raw CSV → Staging Models → Intermediate Models → Payment Performance Marts → Dashboards & Recommendations

## Analytics Engineering Concepts

- Dimensional Modeling
- Metrics Governance
- Data Quality Testing
- dbt Modeling
- Semantic Layer Design
- Operational Analytics
- Payment Performance Optimization

## Example Metrics

- Gross Payment Volume (GPV)
- Interchange Cost
- Interchange Rate
- Debit vs Credit Mix
- AVS Coverage %
- CVC Coverage %
- Cost per Transaction

## Example Business Questions

- Which transaction segments drive the highest interchange costs?
- How does shopper interaction impact interchange rates?
- Do AVS/CVC verification patterns correlate with transaction cost?
- Which BIN ranges contribute disproportionately to payment fees?

## Operational Recommendation Layer

The platform includes a recommendation mart that surfaces payment optimization opportunities based on interchange behavior, authentication quality, and transaction characteristics.

Example recommendations:
- Improve AVS/CVC verification coverage
- Investigate high interchange transaction segments
- Optimize payment routing strategies
- Analyze debit vs credit transaction mix
