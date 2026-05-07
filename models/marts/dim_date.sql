{{
    config(
        materialized='table'
    )
}}

WITH date_spine AS (
    SELECT CAST(range AS DATE) AS date_day
    FROM range(DATE '2024-01-01', DATE '2025-01-01', INTERVAL '1 day')
)

SELECT
    date_day,
    DAYOFWEEK(date_day)                AS day_of_week,
    DAYNAME(date_day)                  AS day_name,
    WEEKOFYEAR(date_day)               AS week_of_year,
    MONTH(date_day)                    AS month_number,
    MONTHNAME(date_day)                AS month_name,
    QUARTER(date_day)                  AS quarter,
    YEAR(date_day)                     AS year,
    DAYOFWEEK(date_day) IN (0, 6)      AS is_weekend,
    date_day = LAST_DAY(date_day)      AS is_month_end
FROM date_spine
