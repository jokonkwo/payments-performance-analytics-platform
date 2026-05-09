# Data Schema — Full Field Reference

Complete reference for all 56 fields in the raw transaction 
schema. Modeled after real payment processor API structures.

## The Same 5 Records

The table below shows the same 5 records from the README 
raw layer section — use this alongside the field definitions 
below to understand what each value means.

| id | charge_id | merchant_account_id | merchant_name | customer_id | attempt_number | created | created_at | card_brand | card_funding | card_country | card_last4 | card_exp_month | card_exp_year | card_fingerprint | card_network | card_wallet | card_bin | network_token_used | checks_cvc_check | checks_address_postal_code_check | checks_address_line1_check | three_d_secure_result | three_d_secure_version | three_d_secure_result_reason | outcome_network_status | outcome_type | outcome_risk_level | outcome_risk_score | outcome_reason | failure_code | outcome_network_decline_code | amount | amount_captured | currency | amount_usd_cents | billing_address_country | billing_address_postal_code | customer_email | customer_ip_country | device_type | shopper_interaction | is_guest_checkout | statement_descriptor | radar_risk_score | radar_risk_level | radar_outcome | disputed | dispute_reason | interchange_amount_cents | interchange_rate_bps | interchange_program | network_fee_cents | stripe_fee_cents | balance_transaction_id | settlement_date |
|:---|:---|:---|:---|:---|---:|---:|:---|:---|:---|:---|---:|---:|---:|:---|:---|:---|---:|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|---:|:---|:---|---:|---:|---:|:---|---:|:---|:---|:---|:---|:---|:---|:---|:---|---:|:---|:---|:---|:---|---:|---:|:---|---:|---:|:---|:---|
| pi_vCoj6YkBQraizYesFHtIjrez | ch_QM0LApaSLjuJTaKMZKh5ioaP | acct_beau000001 | Merchant_0001_Beauty | null | 1 | 1704070613 | 2024-01-01T00:56:53+00:00 | visa | debit | US | 5599 | 10 | 2028 | pNaF2up8SjUSF2N9 | visa | null | 49857374 | False | pass | pass | pass | null | null | null | approved_by_network | authorized | elevated | 73 | null | null | 00 | 5846 | 5846 | usd | 5846 | US | 98101 | null | US | pos_terminal | pos | True | BEAUTY1 | 81 | highest | review | False | null | 52 | 89 | REGULATED_DEBIT | 8 | 199 | txn_cuxplVxJ5zHBpL5il7Pqr0xl | 2024-01-02 |
| pi_eW7DF8mgupKtzh5KX1Sb5vkc | ch_HeuypsExD4BI8jbFXch0vwiI | acct_beau000001 | Merchant_0001_Beauty | null | 1 | 1704072758 | 2024-01-01T01:32:38+00:00 | visa | debit | GB | 7052 | 6 | 2027 | BJuO1yEeJbXcdSbR | visa | apple_pay | 45989189 | False | pass | unchecked | pass | null | null | null | approved_by_network | authorized | normal | 28 | null | null | 00 | 6312 | 6312 | usd | 6312 | GB | EC1A 1BB | null | GB | pos_terminal | pos | True | BEAUTY1 | 3 | normal | allow | False | null | 45 | 72 | SUPERMARKET | 8 | 213 | txn_sHfTQvHW5noaZKWbbvGUVST1 | 2024-01-02 |
| pi_gtxfufzmfhEFgkM355a5Si9r | null | acct_beau000001 | Merchant_0001_Beauty | null | 1 | 1704128312 | 2024-01-01T16:58:32+00:00 | mastercard | credit | US | 9696 | 5 | 2027 | 4T4QOc6zmwbKZFQ7 | mastercard | null | 55493235 | False | pass | pass | pass | null | null | null | declined_by_network | issuer_declined | normal | 3 | null | do_not_honor | 05 | 2060 | 0 | usd | 2060 | US | 33101 | null | US | pos_terminal | pos | True | BEAUTY1 | 68 | elevated | review | False | null | null | null | null | null | null | null | null |
| pi_uZo03LzftvUWfGY5HSdOz7Bm | ch_zd3ZLBLA2h0pV6OHpBEiEDxL | acct_reta000003 | Merchant_0003_Retail | null | 1 | 1704067644 | 2024-01-01T00:07:24+00:00 | visa | credit | GB | 9016 | 12 | 2026 | mwNNjVd6RluKjw0u | visa | null | 43950326 | False | null | unchecked | unchecked | exempted | 2.1.0 | null | approved_by_network | authorized | highest | 91 | null | null | 00 | 26467 | 26467 | usd | 26467 | GB | 1010 | null | GB | mobile | ecommerce | True | RETAIL3 | 70 | elevated | review | False | null | 531 | 201 | STD_IRF | 31 | 797 | txn_ISyKrqZlOfXve7e8qT97PVX6 | 2024-01-03 |
| pi_tvH9TP3ptPwafA5reVZbUXMk | ch_Ls2VNM3ND6ElrUNLoXkHFh0v | acct_beau000001 | Merchant_0001_Beauty | null | 1 | 1705644324 | 2024-01-19T06:05:24+00:00 | visa | debit | US | 5691 | 2 | 2026 | ChTcmXuMApNRkC4I | visa | apple_pay | 46172566 | False | pass | pass | pass | null | null | null | approved_by_network | authorized | elevated | 46 | null | null | 00 | 2486 | 2486 | usd | 2486 | US | 85001 | null | US | pos_terminal | pos | True | BEAUTY1 | 78 | highest | review | True | unrecognized | 20 | 83 | SUPERMARKET | 4 | 102 | txn_JJ3Ske2USh216ksmgbg3urpH | 2024-01-20 |

---

## Field Definitions

### Identity & Routing

| Field | Type | Null? | Description |
|---|---|---|---|
| id | string | Never | PaymentIntent ID. Prefix `pi_` + 24 chars. Primary grain key. |
| charge_id | string | Yes — null on declines | Charge object ID. Prefix `ch_`. Only created on authorized transactions. |
| merchant_account_id | string | Never | Merchant account ID. Prefix `acct_`. |
| merchant_name | string | Never | Human-readable merchant name. |
| customer_id | string | Yes — null for guests | Customer object ID. Prefix `cus_`. Null when no saved profile. |
| attempt_number | integer | Never | Retry attempt number. 1 = first try, 2+ = retry after decline. |
| created | integer | Never | Unix timestamp in seconds. |
| created_at | string | Never | ISO 8601 timestamp with UTC timezone. |
| statement_descriptor | string | Never | Text appearing on cardholder's bank statement. |

> **On prefixed IDs:** Each object type has a unique prefix so IDs are self-describing in logs and debugging. `pi_` = PaymentIntent, `ch_` = Charge, `acct_` = Account, `cus_` = Customer, `txn_` = BalanceTransaction. This is standard Stripe API design.

---

### Card Instrument

| Field | Type | Null? | Description |
|---|---|---|---|
| card_brand | string | Never | Card network. Values: `visa` `mastercard` `amex` `discover` |
| card_funding | string | Never | Funding type. Values: `credit` `debit` `prepaid` `commercial` |
| card_bin | string | Never | First 8 digits of card number (BIN8). Identifies issuer and card program. |
| card_country | string | Never | ISO 3166-1 alpha-2 issuer country. |
| card_last4 | string | Never | Last 4 digits of PAN. |
| card_exp_month | integer | Never | Expiration month (1-12). |
| card_exp_year | integer | Never | Expiration year. |
| card_fingerprint | string | Never | Unique card identifier — same card = same fingerprint across transactions. |
| card_network | string | Never | Processing network. Usually matches card_brand. |
| card_wallet | string | Yes | Digital wallet. Values: `apple_pay` `google_pay` `link` null |
| network_token_used | boolean | Never | True if network token replaced raw PAN. Token transactions have higher auth rates. |

---

### Authorization Checks

| Field | Type | Null? | Description |
|---|---|---|---|
| checks_cvc_check | string | Yes — null = not submitted | CVC result. Values: `pass` `fail` `unavailable` `unchecked` null |
| checks_address_postal_code_check | string | Yes | Postal AVS result. Values: `pass` `fail` `unavailable` `unchecked` null |
| checks_address_line1_check | string | Yes | Address AVS result. Values: `pass` `fail` `unavailable` `unchecked` null |
| three_d_secure_result | string | Yes — null if not triggered | 3DS outcome. Values: `authenticated` `attempt_acknowledged` `exempted` `failed` `not_supported` null |
| three_d_secure_version | string | Yes | Protocol version. Values: `1.0.2` `2.1.0` `2.2.0` null |
| three_d_secure_result_reason | string | Yes | Why 3DS failed or was skipped. Values: `abandoned` `bypassed` `card_not_enrolled` `network_not_supported` null |

> **null vs unchecked:** `null` on a check field means the merchant never submitted that data — a data quality gap. `unchecked` means it was submitted but not yet verified. This distinction matters for optimization analysis.

---

### Authorization Outcome

| Field | Type | Null? | Description |
|---|---|---|---|
| outcome_network_status | string | Never | Network result. Values: `approved_by_network` `declined_by_network` `not_sent_to_network` `reversed_after_approval` |
| outcome_type | string | Never | Outcome classification. Values: `authorized` `manual_review` `issuer_declined` `blocked` `invalid` |
| outcome_risk_level | string | Never | Risk bucket. Values: `normal` `elevated` `highest` |
| outcome_risk_score | integer | Never | Risk score 0-99. |
| outcome_reason | string | Yes — null on authorized | Why a non-authorized outcome occurred. |
| failure_code | string | Yes — null on authorized | Decline reason. Values: `card_declined` `insufficient_funds` `do_not_honor` `card_velocity_exceeded` `expired_card` `incorrect_cvc` `lost_card` `stolen_card` null |
| outcome_network_decline_code | string | Never | Raw 2-digit issuer response code. `00`=approved `05`=do not honor `51`=insufficient funds `61`=velocity `54`=expired `59`=suspected fraud |

> **Hard vs soft declines:** `lost_card` and `stolen_card` are hard declines — never retry. `do_not_honor`, `insufficient_funds`, and `card_velocity_exceeded` are soft declines — retryable with correct timing and updated data.

---

### Transaction Economics

| Field | Type | Null? | Description |
|---|---|---|---|
| amount | integer | Never | Amount in minor units (cents). $58.46 = 5846. |
| amount_captured | integer | Never | Captured amount. 0 on declines. |
| currency | string | Never | ISO 4217 lowercase. e.g. `usd` `eur` `gbp` `cad` |
| amount_usd_cents | integer | Never | USD-equivalent for cross-currency comparison. |
| interchange_amount_cents | integer | Yes — null on declines | Interchange fee in cents. |
| interchange_rate_bps | integer | Yes — null on declines | Interchange as basis points. 89 bps = 0.89%. |
| interchange_program | string | Yes — null on declines | Visa/MC tier name. e.g. `CPS_RETAIL` `REGULATED_DEBIT` `EIRF` `STD_IRF` `SUPERMARKET` |
| network_fee_cents | integer | Yes — null on declines | Network assessment fee separate from interchange. |
| stripe_fee_cents | integer | Yes — null on declines | Processor fee (2.9% + $0.30 standard). |
| balance_transaction_id | string | Yes — null on declines | Settlement record ID. Prefix `txn_`. |
| settlement_date | string | Yes — null on declines | Date funds moved. T+1 or T+2. |

> **On interchange programs:** These are real Visa and Mastercard tier names from published rate schedules. `REGULATED_DEBIT` applies the Durbin Amendment cap (~21 bps for large issuers). `STD_IRF` is the highest fallback tier — applied when auth data like CVC or AVS is missing. Row 4 above shows this directly: null CVC → `STD_IRF` → 201 bps vs 89 bps for the clean debit transaction in Row 1.

---

### Billing & Customer

| Field | Type | Null? | Description |
|---|---|---|---|
| billing_address_country | string | Never | ISO country from billing address. |
| billing_address_postal_code | string | Never | Billing postal code for AVS matching. |
| customer_email | string | Yes | Customer email. Null for guest checkouts. |
| customer_ip_country | string | Never | Country inferred from IP. May differ from card_country on cross-border transactions. |
| device_type | string | Yes | Values: `mobile` `desktop` `tablet` `pos_terminal` null |
| shopper_interaction | string | Never | Channel. Values: `ecommerce` `recurring` `moto` `pos` |
| is_guest_checkout | boolean | Never | True if no saved customer account. |

---

### Risk & Fraud

| Field | Type | Null? | Description |
|---|---|---|---|
| radar_risk_score | integer | Never | ML fraud score 0-99. Higher = riskier. |
| radar_risk_level | string | Never | Risk bucket. Values: `normal` `elevated` `highest` |
| radar_outcome | string | Never | Fraud decision. Values: `allow` `review` `block` |
| disputed | boolean | Never | True if cardholder later filed a dispute. |
| dispute_reason | string | Yes — null if not disputed | Dispute category. Values: `fraudulent` `product_not_received` `unrecognized` null |

---

## Null Pattern Summary

| Pattern | Affected Fields | Meaning |
|---|---|---|
| Null on declines | `charge_id` `interchange_*` `network_fee_cents` `stripe_fee_cents` `balance_transaction_id` `settlement_date` | Transaction never settled |
| Null for guests | `customer_id` `customer_email` | No saved customer profile |
| Null if not triggered | `three_d_secure_*` `card_wallet` | Feature not used |
| Null = not submitted | `checks_cvc_check` `checks_address_*` | Merchant did not send field — optimization gap |

---

## Schema Grounding

Field names and structures are modeled after real payment 
processor API schemas based on publicly documented APIs. 
Interchange program names are real Visa and Mastercard tier 
names from published rate schedules. Outcome codes and check 
result values match documented API response enumerations.
