{{
    config(
        materialized='view'
    )
}}

SELECT
    -- Identifiers
    json_extract_string(raw_payload, '$.id')                             AS id,
    json_extract_string(raw_payload, '$.charge_id')                     AS charge_id,
    json_extract_string(raw_payload, '$.merchant_account_id')           AS merchant_account_id,
    json_extract_string(raw_payload, '$.merchant_name')                 AS merchant_name,
    json_extract_string(raw_payload, '$.customer_id')                   AS customer_id,

    -- Attempt info
    CAST(json_extract(raw_payload, '$.attempt_number') AS INTEGER)      AS attempt_number,

    -- Timestamps
    CAST(json_extract(raw_payload, '$.created') AS BIGINT)              AS created,
    json_extract_string(raw_payload, '$.created_at')                    AS created_at,

    -- Card attributes
    json_extract_string(raw_payload, '$.card_brand')                    AS card_brand,
    json_extract_string(raw_payload, '$.card_funding')                  AS card_funding,
    json_extract_string(raw_payload, '$.card_country')                  AS card_country,
    json_extract_string(raw_payload, '$.card_last4')                    AS card_last4,
    CAST(json_extract(raw_payload, '$.card_exp_month') AS INTEGER)      AS card_exp_month,
    CAST(json_extract(raw_payload, '$.card_exp_year') AS INTEGER)       AS card_exp_year,
    json_extract_string(raw_payload, '$.card_fingerprint')              AS card_fingerprint,
    json_extract_string(raw_payload, '$.card_network')                  AS card_network,
    json_extract_string(raw_payload, '$.card_wallet')                   AS card_wallet,
    json_extract_string(raw_payload, '$.card_bin')                      AS card_bin,
    CAST(json_extract(raw_payload, '$.network_token_used') AS BOOLEAN)  AS network_token_used,

    -- Checks
    json_extract_string(raw_payload, '$.checks_cvc_check')              AS checks_cvc_check,
    json_extract_string(raw_payload, '$.checks_address_postal_code_check') AS checks_address_postal_code_check,
    json_extract_string(raw_payload, '$.checks_address_line1_check')    AS checks_address_line1_check,

    -- 3DS
    json_extract_string(raw_payload, '$.three_d_secure_result')         AS three_d_secure_result,
    json_extract_string(raw_payload, '$.three_d_secure_version')        AS three_d_secure_version,
    json_extract_string(raw_payload, '$.three_d_secure_result_reason')  AS three_d_secure_result_reason,

    -- Outcome
    json_extract_string(raw_payload, '$.outcome_network_status')        AS outcome_network_status,
    json_extract_string(raw_payload, '$.outcome_type')                  AS outcome_type,
    json_extract_string(raw_payload, '$.outcome_risk_level')            AS outcome_risk_level,
    CAST(json_extract(raw_payload, '$.outcome_risk_score') AS INTEGER)  AS outcome_risk_score,
    json_extract_string(raw_payload, '$.outcome_reason')                AS outcome_reason,
    json_extract_string(raw_payload, '$.failure_code')                  AS failure_code,
    json_extract_string(raw_payload, '$.outcome_network_decline_code')  AS outcome_network_decline_code,

    -- Amounts
    CAST(json_extract(raw_payload, '$.amount') AS INTEGER)              AS amount,
    CAST(json_extract(raw_payload, '$.amount_captured') AS INTEGER)     AS amount_captured,
    json_extract_string(raw_payload, '$.currency')                      AS currency,
    CAST(json_extract(raw_payload, '$.amount_usd_cents') AS INTEGER)    AS amount_usd_cents,

    -- Billing
    json_extract_string(raw_payload, '$.billing_address_country')       AS billing_address_country,
    json_extract_string(raw_payload, '$.billing_address_postal_code')   AS billing_address_postal_code,

    -- Customer
    json_extract_string(raw_payload, '$.customer_email')                AS customer_email,
    json_extract_string(raw_payload, '$.customer_ip_country')           AS customer_ip_country,

    -- Device / channel
    json_extract_string(raw_payload, '$.device_type')                   AS device_type,
    json_extract_string(raw_payload, '$.shopper_interaction')           AS shopper_interaction,
    CAST(json_extract(raw_payload, '$.is_guest_checkout') AS BOOLEAN)   AS is_guest_checkout,
    json_extract_string(raw_payload, '$.statement_descriptor')          AS statement_descriptor,

    -- Radar
    CAST(json_extract(raw_payload, '$.radar_risk_score') AS INTEGER)    AS radar_risk_score,
    json_extract_string(raw_payload, '$.radar_risk_level')              AS radar_risk_level,
    json_extract_string(raw_payload, '$.radar_outcome')                 AS radar_outcome,

    -- Disputes
    CAST(json_extract(raw_payload, '$.disputed') AS BOOLEAN)            AS disputed,
    json_extract_string(raw_payload, '$.dispute_reason')                AS dispute_reason,

    -- Fees
    CAST(json_extract(raw_payload, '$.interchange_amount_cents') AS INTEGER)  AS interchange_amount_cents,
    CAST(json_extract(raw_payload, '$.interchange_rate_bps') AS INTEGER)      AS interchange_rate_bps,
    json_extract_string(raw_payload, '$.interchange_program')           AS interchange_program,
    CAST(json_extract(raw_payload, '$.network_fee_cents') AS INTEGER)   AS network_fee_cents,
    CAST(json_extract(raw_payload, '$.stripe_fee_cents') AS INTEGER)    AS processor_fee_cents,

    -- Settlement
    json_extract_string(raw_payload, '$.balance_transaction_id')        AS balance_transaction_id,
    json_extract_string(raw_payload, '$.settlement_date')               AS settlement_date,

    -- Metadata
    _ingested_at,
    _source_file

FROM {{ source('raw', 'stripe_charges') }}
