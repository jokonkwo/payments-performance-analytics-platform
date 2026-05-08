# Metric Definitions

Reference documentation for all governed business metrics in the Payments Performance Analytics Platform. These definitions represent the canonical logic for each metric — the single source of truth that downstream consumers (BI tools, notebooks, ad-hoc queries) should align to.

---

## Gross Payment Volume (GPV)

**Description:** Total value of authorized and captured transactions, expressed in USD. The primary top-line volume metric for any payment business. Excludes declined authorization attempts.

**Formula:** `SUM(amount_usd_cents) / 100`

**Source table:** `fct_payment_transactions`

**Filter:** `outcome_type = 'authorized'`

---

## Authorization Rate

**Description:** The share of payment attempts that result in a network approval. Calculated as approved authorizations divided by total attempts, including declines. A 1–2 percentage point gap from vertical benchmark can represent significant revenue leakage at scale.

**Formula:** `COUNT(*) FILTER (WHERE outcome_type = 'authorized') / NULLIF(COUNT(*), 0)`

**Source table:** `fct_payment_transactions`

**Filter:** None — denominator includes all attempts

---

## Effective Interchange Rate (bps)

**Description:** The actual blended interchange cost as a basis point rate, derived from realized interchange amounts relative to authorized volume. Because interchange varies by card type, funding source, channel, and program tier, the effective rate captures the true cost more accurately than any single posted rate.

**Formula:** `SUM(interchange_amount_cents) / NULLIF(SUM(amount_usd_cents), 0) * 10000`

**Source table:** `fct_payment_transactions`

**Filter:** `outcome_type = 'authorized'`

---

## Dispute Rate

**Description:** Disputes initiated as a percentage of authorized transactions. Tracked by merchant segment, vertical, and risk category to distinguish structural risk from isolated transaction patterns.

**Formula:** `COUNT(*) FILTER (WHERE disputed = true) / NULLIF(COUNT(*) FILTER (WHERE outcome_type = 'authorized'), 0)`

**Source table:** `fct_payment_transactions`

**Filter:** Denominator scoped to authorized transactions only

---

## Average Transaction Value (ATV)

**Description:** Mean transaction size in USD across authorized payments. Useful for cohort comparison and for contextualizing interchange rate movements — a shift in ATV can change effective interchange even with no change in card mix.

**Formula:** `AVG(amount_usd_cents) FILTER (WHERE outcome_type = 'authorized') / 100`

**Source table:** `fct_payment_transactions`

**Filter:** `outcome_type = 'authorized'`

---

## CVC Coverage Rate

**Description:** The proportion of transactions where a CVC check was submitted and returned a pass result. Low CVC coverage is a common driver of soft declines and elevated interchange in card-not-present channels.

**Formula:** `COUNT(*) FILTER (WHERE checks_cvc_check = 'pass') / NULLIF(COUNT(*), 0)`

**Source table:** `fct_payment_transactions`

**Filter:** None — denominator includes all attempts to surface coverage gaps

---

## Network Token Coverage Rate

**Description:** The share of authorized transactions processed using a network token rather than a raw PAN. Higher token coverage is associated with improved authorization rates and, in eligible programs, reduced interchange.

**Formula:** `COUNT(*) FILTER (WHERE network_token_used = true AND outcome_type = 'authorized') / NULLIF(COUNT(*) FILTER (WHERE outcome_type = 'authorized'), 0)`

**Source table:** `fct_payment_transactions`

**Filter:** `outcome_type = 'authorized'`

---

## Cost Per Transaction

**Description:** Total processing cost — interchange plus network fees plus processor fees — divided by transaction count. Useful for benchmarking across channels and card mix, and for quantifying the cost impact of portfolio mix shifts.

**Formula:** `SUM(total_fees_cents) FILTER (WHERE outcome_type = 'authorized') / NULLIF(COUNT(*) FILTER (WHERE outcome_type = 'authorized'), 0) / 100`

**Source table:** `fct_payment_transactions`

**Notes:** `total_fees_cents` is a derived column: `interchange_amount_cents + network_fee_cents + processor_fee_cents`
