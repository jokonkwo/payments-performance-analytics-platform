-- Standardized staging layer for raw payment transactions

SELECT
    payment_creation_day,
    txn_reference,
    bin,
    funding_source,
    issuer_country_code,
    shopper_interaction,
    mcc,
    cvc_supplied,
    avs_supplied,
    transaction_amount,
    transaction_currency,
    interchange_amount,
    interchange_currency
FROM raw_payment_transactions
