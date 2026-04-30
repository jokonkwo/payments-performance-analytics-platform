-- Card BIN dimension

SELECT DISTINCT
    bin,
    issuer_country_code,
    funding_source

FROM stg_payment_transactions
