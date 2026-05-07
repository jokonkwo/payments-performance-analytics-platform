{{
    config(
        materialized='table'
    )
}}

WITH authorized AS (
    SELECT
        merchant_account_id,
        card_funding,
        card_brand,
        shopper_interaction,
        interchange_program,
        DATE_TRUNC('month', date_day)           AS month,
        amount_usd_cents,
        interchange_amount_cents,
        interchange_rate_bps,
        interchange_cost_tier
    FROM {{ ref('fct_payment_transactions') }}
    WHERE is_authorized = TRUE
)

SELECT
    merchant_account_id,
    card_funding,
    card_brand,
    shopper_interaction,
    interchange_program,
    month,

    COUNT(*)                                                            AS transaction_count,
    SUM(amount_usd_cents)                                               AS total_volume_cents,
    SUM(interchange_amount_cents)                                       AS total_interchange_cents,
    AVG(interchange_rate_bps)                                           AS avg_interchange_rate_bps,

    -- Effective interchange rate: actual cost / volume * 10000 bps
    CAST(SUM(interchange_amount_cents) AS DOUBLE)
        / NULLIF(SUM(amount_usd_cents), 0) * 10000                     AS effective_interchange_rate_bps,

    SUM(CASE WHEN interchange_cost_tier = 'premium' THEN 1 ELSE 0 END) AS premium_cost_transaction_count,

    -- Optimization opportunity: cost of premium tier vs. 150 bps target
    SUM(
        CASE
            WHEN interchange_cost_tier = 'premium'
            THEN CAST(amount_usd_cents * (interchange_rate_bps - 150) AS DOUBLE) / 10000
            ELSE 0
        END
    )                                                                   AS interchange_optimization_opportunity_cents

FROM authorized
GROUP BY 1, 2, 3, 4, 5, 6
