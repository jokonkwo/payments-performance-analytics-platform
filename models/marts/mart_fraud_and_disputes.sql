{{
    config(
        materialized='table'
    )
}}

WITH base AS (
    SELECT
        merchant_account_id,
        shopper_interaction,
        radar_risk_level,
        DATE_TRUNC('month', date_day)   AS month,
        is_authorized,
        is_disputed,
        decline_category,
        outcome_risk_level,
        amount_usd_cents
    FROM {{ ref('fct_payment_transactions') }}
)

SELECT
    merchant_account_id,
    shopper_interaction,
    radar_risk_level,
    month,

    COUNT(*)                                                                        AS transaction_count,
    SUM(CASE WHEN is_authorized THEN 1 ELSE 0 END)                                 AS authorized_count,
    SUM(CASE WHEN is_disputed THEN 1 ELSE 0 END)                                   AS disputed_count,

    -- Dispute rate: disputes / authorized
    CAST(SUM(CASE WHEN is_disputed THEN 1 ELSE 0 END) AS DOUBLE)
        / NULLIF(SUM(CASE WHEN is_authorized THEN 1 ELSE 0 END), 0)                AS dispute_rate,

    -- Fraud decline rate: fraud declines / all attempts
    CAST(SUM(CASE WHEN decline_category = 'fraud_decline' THEN 1 ELSE 0 END) AS DOUBLE)
        / NULLIF(COUNT(*), 0)                                                       AS fraud_decline_rate,

    -- High risk authorized: authorized with highest risk score
    SUM(
        CASE WHEN is_authorized AND outcome_risk_level = 'highest' THEN 1 ELSE 0 END
    )                                                                               AS high_risk_authorized_count,

    -- Estimated dispute exposure in cents
    CAST(
        SUM(CASE WHEN is_disputed THEN 1 ELSE 0 END)
        * AVG(CASE WHEN is_authorized THEN amount_usd_cents ELSE NULL END)
    AS BIGINT)                                                                      AS estimated_dispute_exposure_cents

FROM base
GROUP BY 1, 2, 3, 4
