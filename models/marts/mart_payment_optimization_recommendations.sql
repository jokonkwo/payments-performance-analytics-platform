{{
    config(
        materialized='table'
    )
}}

WITH merchant_names AS (
    SELECT DISTINCT merchant_account_id, merchant_name
    FROM {{ ref('fct_payment_transactions') }}
),

-- Pre-aggregate everything needed
merchant_stats AS (
    SELECT
        merchant_account_id,
        COUNT(*)                                                                    AS total_txns,
        SUM(CASE WHEN is_authorized THEN 1 ELSE 0 END)                             AS authorized_txns,
        SUM(CASE WHEN checks_cvc_check IS NULL THEN 1 ELSE 0 END)                  AS null_cvc_txns,
        SUM(CASE WHEN network_token_opportunity THEN 1 ELSE 0 END)                 AS token_opportunity_txns,
        SUM(CASE WHEN three_ds_opportunity THEN 1 ELSE 0 END)                      AS tds_opportunity_txns,
        SUM(CASE WHEN decline_category = 'hard_decline' THEN 1 ELSE 0 END)         AS hard_decline_txns,
        SUM(CASE WHEN interchange_cost_tier = 'premium' THEN 1 ELSE 0 END)         AS premium_tier_txns,
        AVG(amount_usd_cents)                                                       AS avg_amount_usd_cents,
        SUM(amount_usd_cents)                                                       AS total_volume_cents,
        -- Auth rate
        CAST(SUM(CASE WHEN is_authorized THEN 1 ELSE 0 END) AS DOUBLE)
            / NULLIF(COUNT(*), 0)                                                   AS auth_rate
    FROM {{ ref('fct_payment_transactions') }}
    -- Need CVC info from staging
    LEFT JOIN (
        SELECT payment_intent_id, checks_cvc_check
        FROM {{ ref('stg_stripe_charges') }}
    ) cvc_data USING (payment_intent_id)
    GROUP BY 1
),

-- 1. Improve CVC coverage
rec_cvc AS (
    SELECT
        s.merchant_account_id,
        mn.merchant_name,
        'improve_cvc_coverage'                                                      AS recommendation_type,
        s.null_cvc_txns                                                             AS affected_transaction_count,
        -- Estimated impact: ~5% auth rate lift on CVC-null transactions * avg amount
        CAST(s.null_cvc_txns * 0.05 * s.avg_amount_usd_cents * 12 AS BIGINT)       AS estimated_annual_impact_cents,
        CASE
            WHEN CAST(s.null_cvc_txns AS DOUBLE) / NULLIF(s.total_txns, 0) > 0.40 THEN 'high'
            WHEN CAST(s.null_cvc_txns AS DOUBLE) / NULLIF(s.total_txns, 0) > 0.20 THEN 'medium'
            ELSE 'low'
        END                                                                         AS priority,
        'High rate of transactions missing CVC data. Adding CVC collection to checkout flow '
            || 'can reduce soft declines and improve auth rate by ~3-5%.'           AS recommendation_detail
    FROM merchant_stats s
    JOIN merchant_names mn ON s.merchant_account_id = mn.merchant_account_id
    WHERE
        CAST(s.null_cvc_txns AS DOUBLE) / NULLIF(s.total_txns, 0) > 0.20
        AND s.auth_rate < 0.85
),

-- 2. Adopt network tokens
rec_tokens AS (
    SELECT
        s.merchant_account_id,
        mn.merchant_name,
        'adopt_network_tokens'                                                      AS recommendation_type,
        s.token_opportunity_txns                                                    AS affected_transaction_count,
        -- Estimated: ~2% auth lift from network tokens * avg amount * annual
        CAST(s.token_opportunity_txns * 0.02 * s.avg_amount_usd_cents * 12 AS BIGINT) AS estimated_annual_impact_cents,
        CASE
            WHEN s.token_opportunity_txns > 50000 THEN 'high'
            WHEN s.token_opportunity_txns > 10000 THEN 'medium'
            ELSE 'low'
        END                                                                         AS priority,
        'Significant volume of ecommerce/recurring transactions not using network tokens. '
            || 'Network tokenization reduces card-not-present declines and improves auth rates '
            || 'by 2-5% on eligible transactions.'                                 AS recommendation_detail
    FROM merchant_stats s
    JOIN merchant_names mn ON s.merchant_account_id = mn.merchant_account_id
    WHERE s.token_opportunity_txns > 1000
),

-- 3. Optimize 3DS
rec_3ds AS (
    SELECT
        s.merchant_account_id,
        mn.merchant_name,
        'optimize_3ds'                                                              AS recommendation_type,
        s.tds_opportunity_txns                                                      AS affected_transaction_count,
        -- Estimated: 50bps interchange savings + fraud reduction on high-value txns
        CAST(s.tds_opportunity_txns * s.avg_amount_usd_cents * 0.005 * 12 AS BIGINT) AS estimated_annual_impact_cents,
        CASE
            WHEN s.tds_opportunity_txns > 10000 THEN 'high'
            WHEN s.tds_opportunity_txns > 2000  THEN 'medium'
            ELSE 'low'
        END                                                                         AS priority,
        'High value ecommerce transactions ($200+) not using 3DS authentication. '
            || 'Implementing 3DS2 reduces chargebacks and shifts liability to issuer '
            || 'on applicable transactions.'                                        AS recommendation_detail
    FROM merchant_stats s
    JOIN merchant_names mn ON s.merchant_account_id = mn.merchant_account_id
    WHERE s.tds_opportunity_txns > 500
),

-- 4. Reduce hard declines
rec_hard_declines AS (
    SELECT
        s.merchant_account_id,
        mn.merchant_name,
        'reduce_hard_declines'                                                      AS recommendation_type,
        s.hard_decline_txns                                                         AS affected_transaction_count,
        -- Estimated: recover 80% of hard declines via card update flows
        CAST(s.hard_decline_txns * 0.80 * s.avg_amount_usd_cents * 12 AS BIGINT)   AS estimated_annual_impact_cents,
        CASE
            WHEN s.hard_decline_txns > 5000 THEN 'high'
            WHEN s.hard_decline_txns > 1000 THEN 'medium'
            ELSE 'low'
        END                                                                         AS priority,
        'Elevated hard decline volume (lost/stolen/invalid cards). Implement proactive '
            || 'card update emails and account updater service to reduce friction.'  AS recommendation_detail
    FROM merchant_stats s
    JOIN merchant_names mn ON s.merchant_account_id = mn.merchant_account_id
    WHERE s.hard_decline_txns > 100
),

-- 5. Investigate interchange tier
rec_interchange AS (
    SELECT
        s.merchant_account_id,
        mn.merchant_name,
        'investigate_interchange_tier'                                              AS recommendation_type,
        s.premium_tier_txns                                                         AS affected_transaction_count,
        -- Estimated savings: downgrade from premium (avg 300bps) to standard (175bps) = 125bps savings
        CAST(
            s.premium_tier_txns
            * s.avg_amount_usd_cents
            * 0.0125
            * 12
        AS BIGINT)                                                                  AS estimated_annual_impact_cents,
        CASE
            WHEN CAST(s.premium_tier_txns AS DOUBLE) / NULLIF(s.total_txns, 0) > 0.25 THEN 'high'
            WHEN CAST(s.premium_tier_txns AS DOUBLE) / NULLIF(s.total_txns, 0) > 0.10 THEN 'medium'
            ELSE 'low'
        END                                                                         AS priority,
        'Significant portion of authorized volume is qualifying at premium interchange tiers. '
            || 'Review transaction data completeness (Level II/III data, enhanced data) '
            || 'to qualify for lower interchange programs.'                         AS recommendation_detail
    FROM merchant_stats s
    JOIN merchant_names mn ON s.merchant_account_id = mn.merchant_account_id
    WHERE
        CAST(s.premium_tier_txns AS DOUBLE) / NULLIF(s.total_txns, 0) > 0.10
),

all_recs AS (
    SELECT * FROM rec_cvc
    UNION ALL
    SELECT * FROM rec_tokens
    UNION ALL
    SELECT * FROM rec_3ds
    UNION ALL
    SELECT * FROM rec_hard_declines
    UNION ALL
    SELECT * FROM rec_interchange
)

SELECT
    merchant_account_id,
    merchant_name,
    recommendation_type,
    affected_transaction_count,
    estimated_annual_impact_cents,
    priority,
    recommendation_detail
FROM all_recs
ORDER BY
    CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
    estimated_annual_impact_cents DESC
