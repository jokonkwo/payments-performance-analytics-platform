{{
    config(
        materialized='table'
    )
}}

SELECT
    payment_intent_id,
    charge_id,
    merchant_account_id,
    card_bin,
    CAST(created_at AS DATE)            AS date_day,
    amount_cents,
    amount_usd_cents,
    interchange_amount_cents,
    interchange_rate_bps,
    network_fee_cents,
    stripe_fee_cents,
    COALESCE(interchange_amount_cents, 0)
        + COALESCE(network_fee_cents, 0)
        + COALESCE(stripe_fee_cents, 0) AS total_fees_cents,
    auth_quality_segment,
    interchange_cost_tier,
    decline_category,
    shopper_interaction,
    outcome_type,
    card_funding,
    card_brand,
    card_network,
    card_wallet,
    card_country,
    currency,
    interchange_program,
    radar_risk_level,
    outcome_risk_level,
    is_authorized,
    is_disputed,
    is_guest,
    is_network_token,
    is_3ds_authenticated,
    network_token_opportunity,
    three_ds_opportunity,
    is_below_benchmark
FROM {{ ref('int_payment_enriched') }}
