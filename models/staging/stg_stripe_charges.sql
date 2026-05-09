{{
    config(
        materialized='table'
    )
}}

WITH source AS (
    SELECT * FROM {{ ref('raw_stripe_charges') }}
),

typed AS (
    SELECT
        -- Identifiers
        id                                  AS payment_intent_id,
        charge_id,
        merchant_account_id,
        merchant_name,
        customer_id,
        attempt_number,

        -- Timestamps
        created,
        CAST(created_at AS TIMESTAMP WITH TIME ZONE)    AS created_at,

        -- Card
        LOWER(card_brand)                   AS card_brand,
        LOWER(card_funding)                 AS card_funding,
        UPPER(card_country)                 AS card_country,
        card_last4,
        card_exp_month,
        card_exp_year,
        card_fingerprint,
        LOWER(card_network)                 AS card_network,
        card_wallet,
        card_bin,
        COALESCE(network_token_used, FALSE) AS network_token_used,

        -- Checks
        checks_cvc_check,
        checks_address_postal_code_check,
        checks_address_line1_check,

        -- 3DS
        three_d_secure_result,
        three_d_secure_version,
        three_d_secure_result_reason,

        -- Outcome
        outcome_network_status,
        outcome_type,
        outcome_risk_level,
        outcome_risk_score,
        outcome_reason,
        failure_code,
        outcome_network_decline_code,

        -- Amounts
        amount                              AS amount_cents,
        amount_captured,
        LOWER(currency)                     AS currency,
        amount_usd_cents,

        -- Billing
        UPPER(billing_address_country)      AS billing_address_country,
        billing_address_postal_code,

        -- Customer
        LOWER(customer_email)               AS customer_email,
        UPPER(customer_ip_country)          AS customer_ip_country,

        -- Device / channel
        device_type,
        LOWER(shopper_interaction)          AS shopper_interaction,
        COALESCE(is_guest_checkout, FALSE)  AS is_guest_checkout,
        statement_descriptor,

        -- Radar
        radar_risk_score,
        LOWER(radar_risk_level)             AS radar_risk_level,
        LOWER(radar_outcome)                AS radar_outcome,

        -- Disputes
        COALESCE(disputed, FALSE)           AS disputed,
        dispute_reason,

        -- Fees
        interchange_amount_cents,
        interchange_rate_bps,
        interchange_program,
        network_fee_cents,
        processor_fee_cents,

        -- Settlement
        balance_transaction_id,
        CAST(settlement_date AS DATE)       AS settlement_date,

        -- Metadata
        _ingested_at,
        _source_file

    FROM source
    WHERE id IS NOT NULL
      AND amount IS NOT NULL
),

deduped AS (
    SELECT *
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY payment_intent_id
                ORDER BY attempt_number DESC, _ingested_at DESC
            ) AS _row_num
        FROM typed
    ) t
    WHERE _row_num = 1
),

final AS (
    SELECT
        payment_intent_id,
        charge_id,
        merchant_account_id,
        merchant_name,
        customer_id,
        attempt_number,
        created,
        created_at,
        card_brand,
        card_funding,
        card_country,
        card_last4,
        card_exp_month,
        card_exp_year,
        card_fingerprint,
        card_network,
        card_wallet,
        card_bin,
        network_token_used,
        checks_cvc_check,
        checks_address_postal_code_check,
        checks_address_line1_check,
        three_d_secure_result,
        three_d_secure_version,
        three_d_secure_result_reason,
        outcome_network_status,
        outcome_type,
        outcome_risk_level,
        outcome_risk_score,
        outcome_reason,
        failure_code,
        outcome_network_decline_code,
        amount_cents,
        amount_captured,
        currency,
        amount_usd_cents,
        billing_address_country,
        billing_address_postal_code,
        customer_email,
        customer_ip_country,
        device_type,
        shopper_interaction,
        is_guest_checkout,
        statement_descriptor,
        radar_risk_score,
        radar_risk_level,
        radar_outcome,
        disputed,
        dispute_reason,
        interchange_amount_cents,
        interchange_rate_bps,
        interchange_program,
        network_fee_cents,
        processor_fee_cents,
        balance_transaction_id,
        settlement_date,
        _ingested_at,
        _source_file,

        -- Derived booleans
        (outcome_type = 'authorized')                                           AS is_authorized,
        disputed                                                                AS is_disputed,
        is_guest_checkout                                                       AS is_guest,
        network_token_used                                                      AS is_network_token,
        (three_d_secure_result = 'authenticated')                               AS is_3ds_authenticated

    FROM deduped
)

SELECT * FROM final
