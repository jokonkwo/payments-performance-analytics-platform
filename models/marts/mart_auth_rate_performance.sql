{{
    config(
        materialized='table'
    )
}}

WITH base AS (
    SELECT
        merchant_account_id,
        shopper_interaction,
        auth_quality_segment,
        DATE_TRUNC('month', date_day)       AS month,
        is_authorized,
        decline_category,
        amount_usd_cents
    FROM {{ ref('fct_payment_transactions') }}
),

aggregated AS (
    SELECT
        merchant_account_id,
        shopper_interaction,
        auth_quality_segment,
        month,

        COUNT(*)                                                        AS transaction_attempts,
        SUM(CASE WHEN is_authorized THEN 1 ELSE 0 END)                 AS authorized_count,
        COUNT(*) - SUM(CASE WHEN is_authorized THEN 1 ELSE 0 END)      AS declined_count,

        -- Auth rate
        CAST(SUM(CASE WHEN is_authorized THEN 1 ELSE 0 END) AS DOUBLE)
            / NULLIF(COUNT(*), 0)                                       AS auth_rate,

        -- Decline breakdown by category
        SUM(CASE WHEN decline_category = 'hard_decline'         THEN 1 ELSE 0 END) AS hard_decline_count,
        SUM(CASE WHEN decline_category = 'soft_decline_retryable' THEN 1 ELSE 0 END) AS soft_decline_count,
        SUM(CASE WHEN decline_category = 'fraud_decline'        THEN 1 ELSE 0 END) AS fraud_decline_count,
        SUM(CASE WHEN decline_category = 'auth_data_decline'    THEN 1 ELSE 0 END) AS auth_data_decline_count,

        AVG(amount_usd_cents)                                           AS avg_amount_usd_cents

    FROM base
    GROUP BY 1, 2, 3, 4
),

with_benchmarks AS (
    SELECT
        *,
        -- Hardcoded benchmark auth rates per merchant+channel
        CASE
            WHEN merchant_account_id = 'acct_luxecart001'    AND shopper_interaction = 'ecommerce'  THEN 0.81
            WHEN merchant_account_id = 'acct_quickserve002'  AND shopper_interaction = 'pos'        THEN 0.94
            WHEN merchant_account_id = 'acct_quickserve002'  AND shopper_interaction = 'ecommerce'  THEN 0.83
            WHEN merchant_account_id = 'acct_streamsub003'   AND shopper_interaction = 'recurring'  THEN 0.74
            WHEN merchant_account_id = 'acct_globalgoods004' AND shopper_interaction = 'ecommerce'  THEN 0.79
            WHEN merchant_account_id = 'acct_medpay005'      AND shopper_interaction = 'moto'       THEN 0.76
            ELSE 0.80
        END AS benchmark_auth_rate

    FROM aggregated
)

SELECT
    merchant_account_id,
    shopper_interaction,
    auth_quality_segment,
    month,
    transaction_attempts,
    authorized_count,
    declined_count,
    auth_rate,
    hard_decline_count,
    soft_decline_count,
    fraud_decline_count,
    auth_data_decline_count,
    benchmark_auth_rate,
    auth_rate - benchmark_auth_rate                                     AS auth_rate_vs_benchmark,
    CAST(declined_count * avg_amount_usd_cents AS BIGINT)               AS potential_revenue_at_risk_cents
FROM with_benchmarks
