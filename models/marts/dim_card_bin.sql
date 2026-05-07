{{
    config(
        materialized='table'
    )
}}

WITH base AS (
    SELECT DISTINCT
        card_bin,
        card_brand,
        card_funding,
        card_country
    FROM {{ ref('stg_stripe_charges') }}
    WHERE card_bin IS NOT NULL
),

with_issuer AS (
    SELECT
        card_bin,
        card_brand,
        card_funding,
        card_country,
        -- Derive issuer bank from card_bin first digit and card_country
        CASE
            -- AMEX (starts with 3) — few major issuers
            WHEN LEFT(card_bin, 1) = '3' THEN 'American Express'

            -- Visa (starts with 4)
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'US' AND LEFT(card_bin, 2) IN ('41','42') THEN 'Chase'
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'US' AND LEFT(card_bin, 2) IN ('43','44') THEN 'Bank of America'
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'US' AND LEFT(card_bin, 2) IN ('45','46') THEN 'Wells Fargo'
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'US' AND LEFT(card_bin, 2) IN ('47','48') THEN 'Citi'
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'US'                                       THEN 'Capital One'
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'GB'  THEN 'Barclays'
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'DE'  THEN 'Deutsche Bank'
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'FR'  THEN 'BNP Paribas'
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'CA'  THEN 'Royal Bank of Canada'
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'MX'  THEN 'BBVA Mexico'
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'AU'  THEN 'Commonwealth Bank'
            WHEN LEFT(card_bin, 1) = '4' AND card_country = 'NL'  THEN 'ING Bank'
            WHEN LEFT(card_bin, 1) = '4'                           THEN 'HSBC'

            -- Mastercard (starts with 5)
            WHEN LEFT(card_bin, 1) = '5' AND card_country = 'US' AND LEFT(card_bin, 2) IN ('51','52') THEN 'Chase'
            WHEN LEFT(card_bin, 1) = '5' AND card_country = 'US' AND LEFT(card_bin, 2) IN ('53','54') THEN 'Citi'
            WHEN LEFT(card_bin, 1) = '5' AND card_country = 'US' AND LEFT(card_bin, 2) IN ('55')      THEN 'Capital One'
            WHEN LEFT(card_bin, 1) = '5' AND card_country = 'US'                                       THEN 'Bank of America'
            WHEN LEFT(card_bin, 1) = '5' AND card_country = 'GB'  THEN 'HSBC'
            WHEN LEFT(card_bin, 1) = '5' AND card_country = 'DE'  THEN 'Commerzbank'
            WHEN LEFT(card_bin, 1) = '5' AND card_country = 'FR'  THEN 'Societe Generale'
            WHEN LEFT(card_bin, 1) = '5' AND card_country = 'CA'  THEN 'TD Bank'
            WHEN LEFT(card_bin, 1) = '5' AND card_country = 'MX'  THEN 'Santander Mexico'
            WHEN LEFT(card_bin, 1) = '5' AND card_country = 'AU'  THEN 'ANZ Bank'
            WHEN LEFT(card_bin, 1) = '5' AND card_country = 'NL'  THEN 'Rabobank'
            WHEN LEFT(card_bin, 1) = '5'                           THEN 'Santander'

            -- Discover (starts with 6)
            WHEN LEFT(card_bin, 1) = '6' THEN 'Discover Financial'

            ELSE 'Unknown Issuer'
        END AS issuer_bank,

        -- Issuer tier based on brand
        CASE
            WHEN card_brand = 'visa'       THEN 'Visa Issuer'
            WHEN card_brand = 'mastercard' THEN 'Mastercard Issuer'
            WHEN card_brand = 'amex'       THEN 'Amex Issuer'
            WHEN card_brand = 'discover'   THEN 'Discover Issuer'
            ELSE 'Other'
        END AS issuer_tier

    FROM base
)

SELECT * FROM with_issuer
