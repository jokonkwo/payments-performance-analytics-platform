-- Enriched payment transaction logic layer

SELECT
    payment_creation_day,
    txn_reference,

    bin,
    issuer_country_code,

    funding_source,

    shopper_interaction,

    mcc,

    cvc_supplied,
    avs_supplied,

    transaction_amount,
    interchange_amount,

    interchange_amount / NULLIF(transaction_amount, 0)
        AS interchange_rate,

    CASE
        WHEN interchange_amount / NULLIF(transaction_amount, 0) > 0.025
            THEN 'HIGH_COST'
        WHEN interchange_amount / NULLIF(transaction_amount, 0) > 0.015
            THEN 'MEDIUM_COST'
        ELSE 'LOW_COST'
    END AS interchange_cost_tier,

    CASE
        WHEN avs_supplied = TRUE
            AND cvc_supplied = TRUE
            THEN 'FULLY_AUTHENTICATED'

        WHEN avs_supplied = TRUE
            OR cvc_supplied = TRUE
            THEN 'PARTIALLY_AUTHENTICATED'

        ELSE 'UNAUTHENTICATED'
    END AS auth_quality_segment

FROM stg_payment_transactions
