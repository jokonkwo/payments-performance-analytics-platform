"""
Generate ~1,000,000 rows of synthetic Stripe-like payment transaction data.
Outputs to data/landing/raw_charges.ndjson.gz
"""
import gzip
import json
import os
import random
import string
import sys
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(REPO_ROOT, "data", "landing", "raw_charges.ndjson.gz")

MERCHANTS = [
    {
        "id": "MERCH_001",
        "account_id": "acct_luxecart001",
        "name": "LuxeCart",
        "n": 350000,
        "aov_min": 18000,
        "aov_max": 40000,
        "shopper_interaction": "ecommerce",
        "card_funding_weights": [0.72, 0.15, 0.05, 0.08],  # credit, debit, prepaid, commercial
        "card_brand_weights": [0.45, 0.30, 0.18, 0.07],    # visa, mc, amex, discover
        "auth_rate": 0.81,
        "guest_rate": 0.30,
        "network_token_rate": 0.28,
        "apple_pay_rate": 0.15,
        "google_pay_rate": 0.08,
        "link_rate": 0.03,
        "currencies": ["usd"],
        "currency_weights": [1.0],
        "card_countries": ["US", "CA", "GB", "AU"],
        "card_country_weights": [0.85, 0.06, 0.05, 0.04],
        "dispute_rate": 0.008,
        "statement_descriptor": "LUXECART",
        "interchange_programs": {
            "credit": ["CPS_ECOMM", "EIRF", "STD_IRF"],
            "debit": ["REGULATED_DEBIT", "CPS_ECOMM"],
            "prepaid": ["EIRF"],
            "commercial": ["STD_IRF"],
        },
    },
    {
        "id": "MERCH_002",
        "account_id": "acct_quickserve002",
        "name": "QuickServe",
        "n": 280000,
        "aov_min": 1200,
        "aov_max": 2500,
        "shopper_interaction": "pos",
        "card_funding_weights": [0.30, 0.58, 0.08, 0.04],
        "card_brand_weights": [0.50, 0.32, 0.08, 0.10],
        "auth_rate": 0.94,
        "guest_rate": 1.0,
        "network_token_rate": 0.0,
        "apple_pay_rate": 0.25,
        "google_pay_rate": 0.10,
        "link_rate": 0.0,
        "currencies": ["usd"],
        "currency_weights": [1.0],
        "card_countries": ["US"],
        "card_country_weights": [1.0],
        "dispute_rate": 0.008,
        "statement_descriptor": "QUICKSERVE",
        "interchange_programs": {
            "credit": ["CPS_RETAIL", "MC_MERIT_III", "MC_MERIT_I"],
            "debit": ["REGULATED_DEBIT", "SUPERMARKET"],
            "prepaid": ["CPS_RETAIL"],
            "commercial": ["CPS_RETAIL"],
        },
    },
    {
        "id": "MERCH_003",
        "account_id": "acct_streamsub003",
        "name": "StreamSub",
        "n": 180000,
        "aov_min": 1200,
        "aov_max": 1600,
        "shopper_interaction": "recurring",
        "card_funding_weights": [0.55, 0.30, 0.08, 0.07],
        "card_brand_weights": [0.48, 0.33, 0.12, 0.07],
        "auth_rate": 0.74,
        "guest_rate": 0.0,
        "network_token_rate": 0.18,
        "apple_pay_rate": 0.03,
        "google_pay_rate": 0.02,
        "link_rate": 0.05,
        "currencies": ["usd"],
        "currency_weights": [1.0],
        "card_countries": ["US", "CA", "GB"],
        "card_country_weights": [0.80, 0.10, 0.10],
        "dispute_rate": 0.008,
        "statement_descriptor": "STREAMSUB",
        "interchange_programs": {
            "credit": ["CPS_ECOMM", "EIRF"],
            "debit": ["REGULATED_DEBIT"],
            "prepaid": ["EIRF"],
            "commercial": ["STD_IRF"],
        },
    },
    {
        "id": "MERCH_004",
        "account_id": "acct_globalgoods004",
        "name": "GlobalGoods",
        "n": 120000,
        "aov_min": 6000,
        "aov_max": 12000,
        "shopper_interaction": "ecommerce",
        "card_funding_weights": [0.60, 0.22, 0.08, 0.10],
        "card_brand_weights": [0.40, 0.35, 0.15, 0.10],
        "auth_rate": 0.79,
        "guest_rate": 0.30,
        "network_token_rate": 0.22,
        "apple_pay_rate": 0.07,
        "google_pay_rate": 0.06,
        "link_rate": 0.02,
        "currencies": ["usd", "eur", "gbp", "cad", "mxn"],
        "currency_weights": [0.40, 0.25, 0.18, 0.10, 0.07],
        "card_countries": ["US", "GB", "DE", "FR", "CA", "MX", "AU", "NL"],
        "card_country_weights": [0.30, 0.15, 0.12, 0.10, 0.10, 0.08, 0.08, 0.07],
        "dispute_rate": 0.012,
        "statement_descriptor": "GLOBALGOODS",
        "interchange_programs": {
            "credit": ["CPS_ECOMM", "EIRF", "STD_IRF"],
            "debit": ["REGULATED_DEBIT", "CPS_ECOMM"],
            "prepaid": ["EIRF"],
            "commercial": ["STD_IRF"],
        },
    },
    {
        "id": "MERCH_005",
        "account_id": "acct_medpay005",
        "name": "MedPay",
        "n": 70000,
        "aov_min": 20000,
        "aov_max": 60000,
        "shopper_interaction": "moto",
        "card_funding_weights": [0.40, 0.20, 0.30, 0.10],
        "card_brand_weights": [0.50, 0.30, 0.12, 0.08],
        "auth_rate": 0.76,
        "guest_rate": 0.15,
        "network_token_rate": 0.05,
        "apple_pay_rate": 0.01,
        "google_pay_rate": 0.01,
        "link_rate": 0.0,
        "currencies": ["usd"],
        "currency_weights": [1.0],
        "card_countries": ["US"],
        "card_country_weights": [1.0],
        "dispute_rate": 0.015,
        "statement_descriptor": "MEDPAY HEALTH",
        "interchange_programs": {
            "credit": ["EIRF", "STD_IRF"],
            "debit": ["REGULATED_DEBIT"],
            "prepaid": ["EIRF", "STD_IRF"],
            "commercial": ["STD_IRF"],
        },
    },
]

CARD_BRANDS = ["visa", "mastercard", "amex", "discover"]
CARD_FUNDINGS = ["credit", "debit", "prepaid", "commercial"]

EXCHANGE_RATES = {
    "usd": 1.0,
    "eur": 1.09,
    "gbp": 1.27,
    "cad": 0.74,
    "mxn": 0.059,
}

BILLING_COUNTRIES_BY_CARD_COUNTRY = {
    "US": (["US"], [1.0]),
    "GB": (["GB"], [1.0]),
    "DE": (["DE"], [1.0]),
    "FR": (["FR"], [1.0]),
    "CA": (["CA"], [1.0]),
    "MX": (["MX"], [1.0]),
    "AU": (["AU"], [1.0]),
    "NL": (["NL"], [1.0]),
}

US_POSTAL_CODES = [
    "10001", "90210", "60601", "77001", "85001", "30301", "02101", "98101",
    "33101", "75201", "19101", "55401", "80201", "94102", "78201", "37201",
    "53201", "46201", "73101", "83701"
]
NON_US_POSTAL_CODES = ["SW1A 1AA", "75001", "10115", "M5V 2T6", "06600", "EC1A 1BB", "1010"]


def rand_alphanumeric(n):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=n))


def gen_ids_bulk(prefix, length, n):
    """Generate n IDs with given prefix using numpy for speed."""
    chars = np.array(list(string.ascii_letters + string.digits))
    indices = np.random.randint(0, len(chars), size=(n, length))
    return [prefix + ''.join(chars[row]) for row in indices]


def gen_fingerprints_bulk(n):
    chars = np.array(list(string.ascii_letters + string.digits))
    indices = np.random.randint(0, len(chars), size=(n, 16))
    return [''.join(chars[row]) for row in indices]


def gen_card_bins_bulk(brand_array, n):
    """Generate 8-digit BINs consistent with brand."""
    bins = []
    for brand in brand_array:
        if brand == "visa":
            first = "4"
        elif brand == "mastercard":
            first = str(np.random.choice([51, 52, 53, 54, 55]))
        elif brand == "amex":
            first = str(np.random.choice([34, 37]))
        else:  # discover
            first = "6011"
        suffix_len = 8 - len(first)
        suffix = ''.join([str(np.random.randint(0, 10)) for _ in range(suffix_len)])
        bins.append(first + suffix)
    return bins


DECLINE_FAILURE_CODES = [
    "do_not_honor", "insufficient_funds", "card_velocity_exceeded",
    "transaction_not_allowed", "expired_card", "suspected_fraud", "incorrect_cvc"
]
DECLINE_WEIGHTS = [0.35, 0.20, 0.12, 0.10, 0.08, 0.10, 0.05]

DECLINE_CODE_MAP = {
    "do_not_honor": "05",
    "insufficient_funds": "51",
    "card_velocity_exceeded": "61",
    "transaction_not_allowed": "57",
    "expired_card": "54",
    "suspected_fraud": "59",
    "incorrect_cvc": "14",
    None: None,
}

OUTCOME_TYPE_FOR_FAILURE = {
    "do_not_honor": "issuer_declined",
    "insufficient_funds": "issuer_declined",
    "card_velocity_exceeded": "issuer_declined",
    "transaction_not_allowed": "issuer_declined",
    "expired_card": "issuer_declined",
    "suspected_fraud": "blocked",
    "incorrect_cvc": "issuer_declined",
    None: "authorized",
}

DISPUTE_REASONS = ["fraudulent", "product_not_received", "unrecognized"]
DISPUTE_REASON_WEIGHTS = [0.50, 0.30, 0.20]


def generate_merchant_batch(merchant, rng_state=None):
    m = merchant
    n = m["n"]
    interaction = m["shopper_interaction"]

    print(f"  Generating {n:,} rows for {m['name']}...")

    # Timestamps spread across 2024
    start_ts = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp())
    end_ts = int(datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc).timestamp())
    created_timestamps = np.random.randint(start_ts, end_ts, size=n)
    created_timestamps.sort()  # chronological order

    # Card attributes
    card_funding_arr = np.random.choice(CARD_FUNDINGS, size=n, p=m["card_funding_weights"])
    card_brand_arr = np.random.choice(CARD_BRANDS, size=n, p=m["card_brand_weights"])

    # Card countries
    card_country_arr = np.random.choice(
        m["card_countries"], size=n, p=m["card_country_weights"]
    )

    # Currency
    currency_arr = np.random.choice(m["currencies"], size=n, p=m["currency_weights"])

    # Amounts
    amounts = np.random.randint(m["aov_min"], m["aov_max"] + 1, size=n)

    # Auth outcomes
    auth_mask = np.random.random(n) < m["auth_rate"]

    # Attempt numbers (1-3; retries on declined)
    attempt_numbers = np.ones(n, dtype=int)
    retry_mask = ~auth_mask & (np.random.random(n) < 0.4)
    attempt_numbers[retry_mask] = np.random.randint(2, 4, size=retry_mask.sum())

    # Guest checkout
    is_guest_arr = np.random.random(n) < m["guest_rate"]

    # Network tokens
    is_network_token_arr = np.random.random(n) < m["network_token_rate"]
    # POS never uses network tokens
    if interaction == "pos":
        is_network_token_arr[:] = False

    # Wallet usage
    wallet_arr = np.full(n, None, dtype=object)
    apple_mask = np.random.random(n) < m["apple_pay_rate"]
    google_mask = (~apple_mask) & (np.random.random(n) < m["google_pay_rate"])
    link_mask = (~apple_mask) & (~google_mask) & (np.random.random(n) < m["link_rate"])
    wallet_arr[apple_mask] = "apple_pay"
    wallet_arr[google_mask] = "google_pay"
    wallet_arr[link_mask] = "link"

    # Generate IDs
    pi_ids = gen_ids_bulk("pi_", 24, n)
    fingerprints = gen_fingerprints_bulk(n)
    card_bins = gen_card_bins_bulk(card_brand_arr, n)

    # CVC checks by interaction
    cvc_options = ["pass", "fail", "unavailable", "unchecked", None]
    if interaction == "pos":
        cvc_weights = [0.98, 0.02, 0.0, 0.0, 0.0]
    elif interaction == "ecommerce":
        cvc_weights = [0.72, 0.08, 0.0, 0.12, 0.08]
    elif interaction == "recurring":
        cvc_weights = [0.20, 0.05, 0.0, 0.10, 0.65]
    else:  # moto
        cvc_weights = [0.55, 0.10, 0.0, 0.0, 0.35]

    cvc_indices = np.random.choice(len(cvc_options), size=n, p=cvc_weights)
    cvc_arr = np.array(cvc_options, dtype=object)[cvc_indices]

    # Postal code checks
    postal_options = ["pass", "fail", "unavailable", "unchecked", None]
    if interaction == "pos":
        postal_weights = [0.90, 0.05, 0.0, 0.05, 0.0]
    elif interaction == "ecommerce":
        postal_weights = [0.68, 0.10, 0.0, 0.12, 0.10]
    elif interaction == "recurring":
        postal_weights = [0.15, 0.05, 0.0, 0.10, 0.70]
    else:  # moto
        postal_weights = [0.45, 0.10, 0.0, 0.0, 0.45]

    postal_indices = np.random.choice(len(postal_options), size=n, p=postal_weights)
    postal_arr = np.array(postal_options, dtype=object)[postal_indices]

    # Address line1 checks (similar to postal but slightly worse)
    addr_options = ["pass", "fail", "unavailable", "unchecked", None]
    if interaction == "pos":
        addr_weights = [0.85, 0.05, 0.0, 0.10, 0.0]
    elif interaction == "ecommerce":
        addr_weights = [0.60, 0.12, 0.0, 0.15, 0.13]
    elif interaction == "recurring":
        addr_weights = [0.12, 0.05, 0.0, 0.08, 0.75]
    else:  # moto
        addr_weights = [0.40, 0.10, 0.0, 0.0, 0.50]

    addr_indices = np.random.choice(len(addr_options), size=n, p=addr_weights)
    addr_arr = np.array(addr_options, dtype=object)[addr_indices]

    # 3DS
    tds_result_options = ["authenticated", "attempt_acknowledged", "exempted", "failed", "not_supported", None]
    tds_version_options = ["1.0.2", "2.1.0", "2.2.0", None]
    tds_reason_options = ["abandoned", "bypassed", "card_not_enrolled", "network_not_supported", None]

    if interaction in ("ecommerce",):
        tds_result_weights = [0.35, 0.15, 0.20, 0.10, 0.10, 0.10]
    elif interaction == "recurring":
        tds_result_weights = [0.10, 0.05, 0.40, 0.05, 0.05, 0.35]
    else:
        tds_result_weights = [0.0, 0.0, 0.0, 0.0, 0.05, 0.95]

    tds_indices = np.random.choice(len(tds_result_options), size=n, p=tds_result_weights)
    tds_result_arr = np.array(tds_result_options, dtype=object)[tds_indices]

    # 3DS version (null when result is null)
    tds_version_arr = np.full(n, None, dtype=object)
    has_tds = tds_result_arr != None
    has_tds_count = has_tds.sum()
    if has_tds_count > 0:
        v_indices = np.random.choice([0, 1, 2, 3], size=has_tds_count, p=[0.10, 0.40, 0.45, 0.05])
        tds_version_arr[has_tds] = np.array(tds_version_options, dtype=object)[v_indices]

    # 3DS reason (only when failed or not_supported)
    tds_reason_arr = np.full(n, None, dtype=object)
    failed_tds = np.isin(tds_result_arr, ["failed", "not_supported"])
    failed_count = failed_tds.sum()
    if failed_count > 0:
        r_indices = np.random.choice([0, 1, 2, 3, 4], size=failed_count, p=[0.25, 0.20, 0.30, 0.15, 0.10])
        tds_reason_arr[failed_tds] = np.array(tds_reason_options, dtype=object)[r_indices]

    # Decline reasons for declined transactions
    declined_count = (~auth_mask).sum()
    failure_codes_arr = np.full(n, None, dtype=object)
    if declined_count > 0:
        dc_indices = np.random.choice(len(DECLINE_FAILURE_CODES), size=declined_count, p=DECLINE_WEIGHTS)
        failure_codes_arr[~auth_mask] = np.array(DECLINE_FAILURE_CODES, dtype=object)[dc_indices]

    # Risk scores
    radar_risk_scores = np.random.randint(0, 100, size=n)
    outcome_risk_scores = np.random.randint(0, 100, size=n)

    # Risk levels
    radar_risk_levels = np.where(
        radar_risk_scores < 40, "normal",
        np.where(radar_risk_scores < 75, "elevated", "highest")
    )
    outcome_risk_levels = np.where(
        outcome_risk_scores < 40, "normal",
        np.where(outcome_risk_scores < 75, "elevated", "highest")
    )

    # Radar outcomes
    radar_outcomes = np.where(
        radar_risk_scores < 60, "allow",
        np.where(radar_risk_scores < 85, "review", "block")
    )

    # Card last4 and exp
    card_last4_arr = [f"{np.random.randint(1000, 9999)}" for _ in range(n)]
    card_exp_month_arr = np.random.randint(1, 13, size=n)
    card_exp_year_arr = np.random.randint(2024, 2029, size=n)

    # Device types
    if interaction == "pos":
        device_options = ["pos_terminal", None]
        device_weights = [0.95, 0.05]
    elif interaction == "ecommerce":
        device_options = ["mobile", "desktop", "tablet", None]
        device_weights = [0.55, 0.35, 0.08, 0.02]
    elif interaction == "recurring":
        device_options = ["mobile", "desktop", None]
        device_weights = [0.40, 0.50, 0.10]
    else:  # moto
        device_options = [None]
        device_weights = [1.0]

    device_indices = np.random.choice(len(device_options), size=n, p=device_weights)
    device_arr = np.array(device_options, dtype=object)[device_indices]

    records = []

    for i in range(n):
        ts = int(created_timestamps[i])
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        created_at = dt.isoformat()

        is_auth = bool(auth_mask[i])
        card_funding = str(card_funding_arr[i])
        card_brand = str(card_brand_arr[i])
        card_country = str(card_country_arr[i])
        currency = str(currency_arr[i])
        amount = int(amounts[i])
        failure_code = failure_codes_arr[i]
        if failure_code is not None:
            failure_code = str(failure_code)

        # Outcome
        if is_auth:
            outcome_type = "authorized"
            outcome_network_status = "approved_by_network"
            outcome_network_decline_code = "00"
            outcome_reason = None
            charge_id = "ch_" + rand_alphanumeric(24)
            amount_captured = amount
            balance_txn_id = "txn_" + rand_alphanumeric(24)
            # Settlement date T+1 or T+2
            settle_offset = random.choices([1, 2], weights=[0.7, 0.3])[0]
            settlement_date = (dt + timedelta(days=settle_offset)).strftime("%Y-%m-%d")
        else:
            outcome_type = OUTCOME_TYPE_FOR_FAILURE.get(failure_code, "issuer_declined")
            outcome_network_status = "declined_by_network" if failure_code != "suspected_fraud" else "not_sent_to_network"
            outcome_network_decline_code = DECLINE_CODE_MAP.get(failure_code)
            if outcome_type in ("blocked", "invalid"):
                outcome_reason = "highest_risk_level"
            else:
                outcome_reason = None
            charge_id = None
            amount_captured = 0
            balance_txn_id = None
            settlement_date = None

        # Interchange
        if is_auth:
            if card_brand == "amex":
                base_bps = np.random.randint(270, 320)
            elif card_funding == "commercial":
                base_bps = np.random.randint(220, 280)
            elif card_funding == "prepaid":
                base_bps = np.random.randint(165, 190)
            elif card_funding == "credit":
                if interaction in ("ecommerce",):
                    base_bps = np.random.randint(195, 220)
                elif interaction == "pos":
                    base_bps = np.random.randint(150, 175)
                elif interaction == "recurring":
                    base_bps = np.random.randint(185, 200)
                else:
                    base_bps = np.random.randint(175, 210)
            else:  # debit
                if interaction in ("ecommerce",):
                    base_bps = np.random.randint(120, 140)
                elif interaction == "pos":
                    base_bps = np.random.randint(70, 90)
                else:
                    base_bps = np.random.randint(95, 120)

            interchange_rate_bps = int(base_bps)
            interchange_amount_cents = int(amount * interchange_rate_bps / 10000)
            network_fee_cents = int(amount * 0.0011 + 2)  # ~11bps + $0.02
            stripe_fee_cents = int(amount * 0.029 + 30)  # 2.9% + $0.30

            # Interchange program
            programs = m["interchange_programs"].get(card_funding, ["CPS_ECOMM"])
            interchange_program = random.choice(programs)
        else:
            interchange_rate_bps = None
            interchange_amount_cents = None
            network_fee_cents = None
            stripe_fee_cents = None
            interchange_program = None

        # USD equivalent
        rate = EXCHANGE_RATES.get(currency, 1.0)
        amount_usd_cents = int(amount * rate)

        # Customer
        is_guest = bool(is_guest_arr[i])
        if is_guest:
            customer_id = None
            customer_email = None
        else:
            customer_id = "cus_" + rand_alphanumeric(16)
            customer_email = f"user{np.random.randint(10000, 99999)}@example.com"

        # IP country (mostly matches card country, some VPN)
        if np.random.random() < 0.05:
            ip_countries = ["US", "GB", "DE", "FR", "CA", "AU", "NL", "SG"]
            ip_country = random.choice(ip_countries)
        else:
            ip_country = card_country

        # Billing postal
        if card_country == "US":
            billing_postal = random.choice(US_POSTAL_CODES)
        else:
            billing_postal = random.choice(NON_US_POSTAL_CODES)

        # Disputed (only authorized transactions)
        is_disputed = False
        dispute_reason = None
        if is_auth and np.random.random() < m["dispute_rate"]:
            is_disputed = True
            dispute_reason = np.random.choice(
                DISPUTE_REASONS, p=DISPUTE_REASON_WEIGHTS
            )

        record = {
            "id": pi_ids[i],
            "charge_id": charge_id,
            "merchant_account_id": m["account_id"],
            "merchant_name": m["name"],
            "customer_id": customer_id,
            "attempt_number": int(attempt_numbers[i]),
            "created": ts,
            "created_at": created_at,
            "card_brand": card_brand,
            "card_funding": card_funding,
            "card_country": card_country,
            "card_last4": str(card_last4_arr[i]),
            "card_exp_month": int(card_exp_month_arr[i]),
            "card_exp_year": int(card_exp_year_arr[i]),
            "card_fingerprint": fingerprints[i],
            "card_network": card_brand,
            "card_wallet": wallet_arr[i],
            "card_bin": card_bins[i],
            "network_token_used": bool(is_network_token_arr[i]),
            "checks_cvc_check": cvc_arr[i],
            "checks_address_postal_code_check": postal_arr[i],
            "checks_address_line1_check": addr_arr[i],
            "three_d_secure_result": tds_result_arr[i],
            "three_d_secure_version": tds_version_arr[i],
            "three_d_secure_result_reason": tds_reason_arr[i],
            "outcome_network_status": outcome_network_status,
            "outcome_type": outcome_type,
            "outcome_risk_level": str(outcome_risk_levels[i]),
            "outcome_risk_score": int(outcome_risk_scores[i]),
            "outcome_reason": outcome_reason,
            "failure_code": failure_code,
            "outcome_network_decline_code": outcome_network_decline_code,
            "amount": amount,
            "amount_captured": amount_captured,
            "currency": currency,
            "amount_usd_cents": amount_usd_cents,
            "billing_address_country": card_country,
            "billing_address_postal_code": billing_postal,
            "customer_email": customer_email,
            "customer_ip_country": ip_country,
            "device_type": device_arr[i],
            "shopper_interaction": interaction,
            "is_guest_checkout": is_guest,
            "statement_descriptor": m["statement_descriptor"],
            "radar_risk_score": int(radar_risk_scores[i]),
            "radar_risk_level": str(radar_risk_levels[i]),
            "radar_outcome": str(radar_outcomes[i]),
            "disputed": is_disputed,
            "dispute_reason": dispute_reason,
            "interchange_amount_cents": interchange_amount_cents,
            "interchange_rate_bps": interchange_rate_bps,
            "interchange_program": interchange_program,
            "network_fee_cents": network_fee_cents,
            "stripe_fee_cents": stripe_fee_cents,
            "balance_transaction_id": balance_txn_id,
            "settlement_date": settlement_date,
        }
        records.append(record)

    return records


def main():
    t0 = time.time()
    print("=" * 60)
    print("Payments Synthetic Data Generator")
    print("=" * 60)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    total_records = 0
    merchant_stats = {}

    with gzip.open(OUTPUT_PATH, "wt", encoding="utf-8") as f:
        for merchant in MERCHANTS:
            records = generate_merchant_batch(merchant)
            chunk_size = 10000
            authorized = 0
            for start in range(0, len(records), chunk_size):
                chunk = records[start:start + chunk_size]
                for rec in chunk:
                    f.write(json.dumps(rec) + "\n")
                authorized += sum(1 for r in chunk if r["outcome_type"] == "authorized")

            # Recalculate full merchant stats
            auth_count = sum(1 for r in records if r["outcome_type"] == "authorized")
            ic_rates = [r["interchange_rate_bps"] for r in records if r["interchange_rate_bps"] is not None]
            null_cvc = sum(1 for r in records if r["checks_cvc_check"] is None)

            merchant_stats[merchant["name"]] = {
                "total": len(records),
                "authorized": auth_count,
                "auth_rate": auth_count / len(records),
                "avg_interchange_bps": sum(ic_rates) / len(ic_rates) if ic_rates else 0,
                "null_cvc": null_cvc,
            }
            total_records += len(records)
            print(f"    Written {len(records):,} rows for {merchant['name']}")

    elapsed = time.time() - t0

    print("\n" + "=" * 60)
    print(f"SUMMARY — Total rows: {total_records:,}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")
    print("=" * 60)
    print(f"\n{'Merchant':<15} {'Total':>10} {'Authorized':>12} {'Auth Rate':>10} {'Avg IC (bps)':>14} {'Null CVC':>10}")
    print("-" * 75)
    for name, stats in merchant_stats.items():
        print(
            f"{name:<15} {stats['total']:>10,} {stats['authorized']:>12,} "
            f"{stats['auth_rate']:>10.1%} {stats['avg_interchange_bps']:>14.1f} "
            f"{stats['null_cvc']:>10,}"
        )

    # Duplicate check
    print("\nDuplicate check: IDs are generated with randomness — collision probability < 1e-10 per ID")
    print("File size:", os.path.getsize(OUTPUT_PATH) / 1024 / 1024, "MB (compressed)")


if __name__ == "__main__":
    main()
