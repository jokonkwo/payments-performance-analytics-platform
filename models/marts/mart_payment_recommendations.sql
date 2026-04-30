-- Operational recommendations for payment optimization

SELECT
    funding_source,
    shopper_interaction,
    auth_quality_segment,

    COUNT(*) AS transaction_count,

    SUM(transaction_amount) AS gross_payment_volume,

    SUM(interchange_amount) AS total_interchange_cost,

    AVG(interchange_rate) AS avg_interchange_rate,

    CASE
        WHEN AVG(interchange_rate) > 0.025
            THEN 'Investigate routing and authentication optimization opportunities'

        WHEN auth_quality_segment = 'UNAUTHENTICATED'
            THEN 'Increase AVS/CVC verification coverage'

        ELSE 'Performance within expected thresholds'
    END AS optimization_recommendation

FROM fct_payment_transactions
GROUP BY 1,2,3
