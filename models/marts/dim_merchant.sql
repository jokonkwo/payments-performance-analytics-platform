{{
    config(
        materialized='table'
    )
}}

SELECT
    merchant_account_id,
    MAX(merchant_name) AS merchant_name,
    CASE merchant_account_id
        WHEN 'acct_luxecart001'    THEN '5999'
        WHEN 'acct_quickserve002'  THEN '5812'
        WHEN 'acct_streamsub003'   THEN '7372'
        WHEN 'acct_globalgoods004' THEN '5999'
        WHEN 'acct_medpay005'      THEN '8099'
    END AS merchant_mcc,
    CASE merchant_account_id
        WHEN 'acct_luxecart001'    THEN 'Premium Ecommerce'
        WHEN 'acct_quickserve002'  THEN 'Quick Service Restaurant'
        WHEN 'acct_streamsub003'   THEN 'Software / Subscription'
        WHEN 'acct_globalgoods004' THEN 'Cross-Border Marketplace'
        WHEN 'acct_medpay005'      THEN 'Healthcare / Medical'
    END AS merchant_vertical,
    -- Primary shopper interaction: most common channel for this merchant
    (
        SELECT shopper_interaction
        FROM {{ ref('stg_stripe_charges') }} inner_q
        WHERE inner_q.merchant_account_id = outer_q.merchant_account_id
        GROUP BY shopper_interaction
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) AS primary_shopper_interaction,
    MIN(created_at) AS onboarded_at
FROM {{ ref('stg_stripe_charges') }} outer_q
GROUP BY 1
