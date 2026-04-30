-- Core fact table for payment transaction analytics

SELECT
    payment_creation_day,
    txn_reference,
    bin,
    funding_source,
    issuer_country_code,
    shopper_interaction,
    mcc,

    transaction_amount,
    interchange_amount,

    interchange_amount / NULLIF(transaction_amount, 0) AS interchange_rate

FROM stg_payment_transactions
