-- Core payment transaction fact table

SELECT
    payment_creation_day,
    txn_reference,

    bin,
    issuer_country_code,
    funding_source,
    shopper_interaction,
    mcc,

    transaction_amount,
    interchange_amount,
    interchange_rate,

    interchange_cost_tier,
    auth_quality_segment

FROM int_payment_enriched
