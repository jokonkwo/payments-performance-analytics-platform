{{
    config(
        materialized='view'
    )
}}

WITH base AS (
    SELECT * FROM {{ ref('stg_stripe_charges') }}
),

enriched AS (
    SELECT
        *,

        -- 1. Auth quality segment based on CVC and postal code checks
        CASE
            WHEN checks_cvc_check = 'pass'
                 AND checks_address_postal_code_check = 'pass'
                THEN 'fully_authenticated'
            WHEN checks_cvc_check = 'pass'
                 AND (checks_address_postal_code_check != 'pass'
                      OR checks_address_postal_code_check IS NULL)
                THEN 'cvc_only'
            WHEN checks_address_postal_code_check = 'pass'
                 AND (checks_cvc_check != 'pass'
                      OR checks_cvc_check IS NULL)
                THEN 'postal_only'
            WHEN checks_cvc_check IN ('unchecked', 'unavailable')
                 OR checks_address_postal_code_check IN ('unchecked', 'unavailable')
                THEN 'partially_authenticated'
            ELSE 'unauthenticated'
        END AS auth_quality_segment,

        -- 2. Interchange cost tier
        CASE
            WHEN interchange_rate_bps IS NULL THEN NULL
            WHEN interchange_rate_bps > 250    THEN 'premium'
            WHEN interchange_rate_bps >= 150   THEN 'standard'
            ELSE 'optimized'
        END AS interchange_cost_tier,

        -- 3. Decline category
        CASE
            WHEN is_authorized THEN NULL
            WHEN failure_code IN ('lost_card', 'stolen_card', 'invalid_card')
                THEN 'hard_decline'
            WHEN failure_code IN (
                'insufficient_funds', 'do_not_honor',
                'card_velocity_exceeded', 'transaction_not_allowed'
            )   THEN 'soft_decline_retryable'
            WHEN failure_code = 'suspected_fraud'
                 OR outcome_risk_level = 'highest'
                THEN 'fraud_decline'
            WHEN failure_code IN ('incorrect_cvc', 'expired_card')
                THEN 'auth_data_decline'
            WHEN failure_code IS NOT NULL
                THEN 'soft_decline_retryable'
            ELSE NULL
        END AS decline_category,

        -- 4. Below benchmark flag (hardcoded benchmark auth rates per merchant+channel)
        CASE
            WHEN merchant_account_id = 'acct_luxecart001'
                 AND shopper_interaction = 'ecommerce'
                 AND NOT is_authorized
                THEN TRUE
            WHEN merchant_account_id = 'acct_quickserve002'
                 AND shopper_interaction = 'pos'
                 AND NOT is_authorized
                THEN TRUE
            WHEN merchant_account_id = 'acct_streamsub003'
                 AND shopper_interaction = 'recurring'
                 AND NOT is_authorized
                THEN TRUE
            WHEN merchant_account_id = 'acct_globalgoods004'
                 AND shopper_interaction = 'ecommerce'
                 AND NOT is_authorized
                THEN TRUE
            WHEN merchant_account_id = 'acct_medpay005'
                 AND shopper_interaction = 'moto'
                 AND NOT is_authorized
                THEN TRUE
            ELSE FALSE
        END AS is_below_benchmark,

        -- 5. Network token opportunity: authorized non-token ecommerce/recurring
        (
            NOT network_token_used
            AND shopper_interaction IN ('ecommerce', 'recurring')
            AND is_authorized
        ) AS network_token_opportunity,

        -- 6. 3DS opportunity: authorized ecommerce, high value, not already 3DS
        (
            NOT (three_d_secure_result = 'authenticated')
            AND amount_usd_cents > 20000
            AND shopper_interaction = 'ecommerce'
            AND is_authorized
        ) AS three_ds_opportunity

    FROM base
)

SELECT * FROM enriched
