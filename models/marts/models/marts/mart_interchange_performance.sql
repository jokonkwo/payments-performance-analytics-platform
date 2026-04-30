-- Aggregated payment performance metrics by transaction attributes

SELECT
    funding_source,
    shopper_interaction,
    mcc,

    COUNT(*) AS transaction_count,
    SUM(transaction_amount) AS gross_payment_volume,
    SUM(interchange_amount) AS total_interchange_cost,

    SUM(interchange_amount) / NULLIF(SUM(transaction_amount), 0)
        AS interchange_rate

FROM fct_payment_transactions
GROUP BY 1,2,3
