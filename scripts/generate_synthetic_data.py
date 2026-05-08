"""
Generate synthetic Stripe-like payment transaction data.
Outputs to data/landing/raw_charges.ndjson.gz
"""
import argparse
import gzip
import orjson
import os
import string
import time
from datetime import date, datetime, timedelta, timezone

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(REPO_ROOT, "data", "landing", "raw_charges.ndjson.gz")

VERTICALS = [
    "retail", "qsr", "subscription", "healthcare", "travel",
    "marketplace", "grocery", "gaming", "education", "beauty",
    "automotive", "real_estate", "nonprofit", "b2b_saas", "logistics",
]

SIZE_TIERS = ["enterprise", "large", "mid", "small"]
SIZE_TIER_WEIGHTS = [0.05, 0.20, 0.45, 0.30]

DAILY_VOLUME = {
    "enterprise": (2000, 8000),
    "large":      (400,  2000),
    "mid":        (60,   400),
    "small":      (8,    60),
}

VERTICAL_CHANNEL = {
    "retail":       {"ecommerce": 0.75, "pos": 0.20, "moto": 0.05},
    "qsr":          {"pos": 0.90, "ecommerce": 0.08, "moto": 0.02},
    "subscription": {"recurring": 0.85, "ecommerce": 0.10, "moto": 0.05},
    "healthcare":   {"moto": 0.55, "ecommerce": 0.30, "pos": 0.15},
    "travel":       {"ecommerce": 0.75, "moto": 0.20, "recurring": 0.05},
    "marketplace":  {"ecommerce": 0.85, "recurring": 0.10, "moto": 0.05},
    "grocery":      {"pos": 0.70, "ecommerce": 0.25, "moto": 0.05},
    "gaming":       {"ecommerce": 0.55, "recurring": 0.40, "moto": 0.05},
    "education":    {"ecommerce": 0.50, "recurring": 0.35, "moto": 0.15},
    "beauty":       {"ecommerce": 0.80, "pos": 0.15, "moto": 0.05},
    "automotive":   {"ecommerce": 0.50, "pos": 0.30, "moto": 0.20},
    "real_estate":  {"moto": 0.60, "ecommerce": 0.30, "recurring": 0.10},
    "nonprofit":    {"ecommerce": 0.65, "moto": 0.25, "recurring": 0.10},
    "b2b_saas":     {"recurring": 0.80, "ecommerce": 0.15, "moto": 0.05},
    "logistics":    {"moto": 0.50, "ecommerce": 0.35, "pos": 0.15},
}

VERTICAL_AOV = {
    "retail":       (2500,  25000),
    "qsr":          (800,   3500),
    "subscription": (999,   4999),
    "healthcare":   (15000, 80000),
    "travel":       (20000, 150000),
    "marketplace":  (3000,  30000),
    "grocery":      (1500,  8000),
    "gaming":       (499,   5999),
    "education":    (2000,  50000),
    "beauty":       (1500,  12000),
    "automotive":   (5000,  100000),
    "real_estate":  (50000, 500000),
    "nonprofit":    (2000,  25000),
    "b2b_saas":     (5000,  50000),
    "logistics":    (3000,  30000),
}

TIER_AOV_MULT = {"enterprise": 2.0, "large": 1.4, "mid": 1.0, "small": 0.7}

CHANNEL_AUTH_RANGE = {
    "pos":       (0.88, 0.96),
    "ecommerce": (0.75, 0.88),
    "recurring": (0.71, 0.84),
    "moto":      (0.72, 0.82),
}

TIER_AUTH_DELTA = {"enterprise": 0.03, "large": 0.015, "mid": 0.0, "small": -0.02}

WEEKEND_MULT = {
    "retail": 1.30, "qsr": 1.25, "subscription": 0.85, "healthcare": 0.40,
    "travel": 1.35, "marketplace": 1.15, "grocery": 1.40, "gaming": 1.45,
    "education": 0.60, "beauty": 1.20, "automotive": 0.80, "real_estate": 0.50,
    "nonprofit": 0.90, "b2b_saas": 0.50, "logistics": 0.70,
}

# Holiday volume multiplier by vertical; unlisted verticals default to 1.2
HOLIDAY_MULT = {
    "retail": 1.8, "grocery": 1.8, "beauty": 1.8, "gaming": 1.8,
    "qsr": 0.6, "healthcare": 0.3, "b2b_saas": 0.3, "real_estate": 0.3,
    "education": 0.4, "logistics": 0.7,
}

US_HOLIDAYS_2024 = frozenset([
    (1,1),(1,15),(2,14),(2,19),(3,31),(5,12),(5,27),(6,19),(7,4),(9,2),
    (10,14),(10,31),(11,11),(11,28),(11,29),(12,24),(12,25),(12,26),(12,31),
])

EXCHANGE_RATES = {
    "usd": 1.0, "eur": 1.09, "gbp": 1.27, "cad": 0.74,
    "mxn": 0.059, "aud": 0.65, "sgd": 0.74, "brl": 0.20,
}

CARD_BRANDS  = ["visa", "mastercard", "amex", "discover"]
CARD_FUNDINGS = ["credit", "debit", "prepaid", "commercial"]

DECLINE_CODES = [
    "do_not_honor", "insufficient_funds", "card_velocity_exceeded",
    "transaction_not_allowed", "expired_card", "suspected_fraud", "incorrect_cvc",
]
DECLINE_WEIGHTS = [0.35, 0.20, 0.12, 0.10, 0.08, 0.10, 0.05]

NETWORK_DECLINE_CODE = {
    "do_not_honor": "05", "insufficient_funds": "51",
    "card_velocity_exceeded": "61", "transaction_not_allowed": "57",
    "expired_card": "54", "suspected_fraud": "59", "incorrect_cvc": "14",
}
OUTCOME_FOR_FAILURE = {
    "do_not_honor": "issuer_declined", "insufficient_funds": "issuer_declined",
    "card_velocity_exceeded": "issuer_declined", "transaction_not_allowed": "issuer_declined",
    "expired_card": "issuer_declined", "suspected_fraud": "blocked",
    "incorrect_cvc": "issuer_declined",
}

DISPUTE_REASONS  = ["fraudulent", "product_not_received", "unrecognized"]
DISPUTE_WEIGHTS  = [0.50, 0.30, 0.20]

US_POSTALS = [
    "10001", "90210", "60601", "77001", "85001", "30301", "02101", "98101",
    "33101", "75201", "19101", "55401", "80201", "94102", "78201", "37201",
    "53201", "46201", "73101", "83701",
]
NON_US_POSTALS = ["SW1A 1AA", "75001", "10115", "M5V 2T6", "06600", "EC1A 1BB", "1010"]

ALNUM = np.array(list(string.ascii_letters + string.digits))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm(weights):
    w = np.array(weights, dtype=float)
    return (w / w.sum()).tolist()


def gen_ids(prefix, length, n, rng):
    idx = rng.integers(0, len(ALNUM), size=(n, length))
    return [prefix + "".join(ALNUM[row].tolist()) for row in idx]


def gen_fingerprints(n, rng):
    idx = rng.integers(0, len(ALNUM), size=(n, 16))
    return ["".join(ALNUM[row].tolist()) for row in idx]


def gen_bins(brands, rng):
    out = []
    for b in brands:
        if b == "visa":
            prefix = "4"
        elif b == "mastercard":
            prefix = str(int(rng.choice([51, 52, 53, 54, 55])))
        elif b == "amex":
            prefix = str(int(rng.choice([34, 37])))
        else:
            prefix = "6011"
        suffix = "".join(str(int(rng.integers(0, 10))) for _ in range(8 - len(prefix)))
        out.append(prefix + suffix)
    return out


# ---------------------------------------------------------------------------
# Merchant profile generation
# ---------------------------------------------------------------------------

def gen_merchant(idx, rng):
    size_tier = str(rng.choice(SIZE_TIERS, p=SIZE_TIER_WEIGHTS))
    vertical  = str(rng.choice(VERTICALS))

    ch_map = VERTICAL_CHANNEL[vertical]
    channels, ch_w = zip(*ch_map.items())
    primary_channel = str(rng.choice(channels, p=_norm(ch_w)))

    mult    = TIER_AOV_MULT[size_tier]
    aov_lo  = max(1, int(VERTICAL_AOV[vertical][0] * mult))
    aov_hi  = max(aov_lo + 1, int(VERTICAL_AOV[vertical][1] * mult))

    ar_lo, ar_hi = CHANNEL_AUTH_RANGE[primary_channel]
    auth_rate = float(np.clip(rng.uniform(ar_lo, ar_hi) + TIER_AUTH_DELTA[size_tier], 0.70, 0.97))

    dv_lo, dv_hi = DAILY_VOLUME[size_tier]
    base_daily     = float(rng.uniform(dv_lo, dv_hi))
    monthly_growth = float(rng.uniform(0.0, 0.03))

    # Card funding weights
    if primary_channel == "pos":
        fw = [0.30, 0.58, 0.08, 0.04]
    elif primary_channel == "recurring":
        fw = [0.55, 0.30, 0.08, 0.07]
    elif primary_channel == "moto":
        fw = [0.42, 0.22, 0.28, 0.08]
    else:
        fw = [0.65, 0.20, 0.07, 0.08]
    if vertical == "healthcare":
        fw = [0.38, 0.22, 0.32, 0.08]

    # Card brand weights
    if vertical in ("b2b_saas", "travel", "automotive"):
        bw = [0.42, 0.32, 0.18, 0.08]
    elif vertical == "grocery":
        bw = [0.52, 0.33, 0.05, 0.10]
    else:
        bw = [0.47, 0.32, 0.13, 0.08]

    # Geography & currency
    if vertical in ("travel", "marketplace", "gaming", "b2b_saas"):
        countries = ["US", "CA", "GB", "DE", "FR", "AU", "NL", "SG"]
        ctry_w    = _norm([0.45, 0.12, 0.12, 0.10, 0.08, 0.07, 0.04, 0.02])
        currencies = ["usd", "eur", "gbp", "cad"]
        curr_w     = _norm([0.50, 0.22, 0.18, 0.10])
    elif vertical in ("retail", "qsr", "grocery", "beauty", "healthcare"):
        countries  = ["US", "CA", "GB"]
        ctry_w     = _norm([0.88, 0.07, 0.05])
        currencies = ["usd"]
        curr_w     = [1.0]
    else:
        countries  = ["US", "CA", "GB", "AU"]
        ctry_w     = _norm([0.80, 0.08, 0.07, 0.05])
        currencies = ["usd", "eur", "gbp"]
        curr_w     = _norm([0.70, 0.18, 0.12])

    # Guest rate
    if primary_channel == "pos":
        guest_rate = 1.0
    elif primary_channel == "recurring":
        guest_rate = float(rng.uniform(0.0, 0.05))
    elif primary_channel == "moto":
        guest_rate = float(rng.uniform(0.05, 0.25))
    else:
        guest_rate = float(rng.uniform(0.15, 0.45))

    # Network token rate
    nt = 0.0 if primary_channel == "pos" else float(rng.uniform(0.05, 0.35))
    if size_tier == "enterprise":
        nt = min(0.65, nt * 1.6)
    elif size_tier == "small":
        nt *= 0.4
    network_token_rate = nt

    # Wallet rates
    if primary_channel == "pos":
        apple_rate  = float(rng.uniform(0.15, 0.35))
        google_rate = float(rng.uniform(0.08, 0.18))
        link_rate   = 0.0
    elif primary_channel == "ecommerce":
        apple_rate  = float(rng.uniform(0.08, 0.22))
        google_rate = float(rng.uniform(0.04, 0.12))
        link_rate   = float(rng.uniform(0.01, 0.06))
    elif primary_channel == "recurring":
        apple_rate  = float(rng.uniform(0.02, 0.08))
        google_rate = float(rng.uniform(0.01, 0.05))
        link_rate   = float(rng.uniform(0.02, 0.08))
    else:
        apple_rate = google_rate = link_rate = 0.0

    # Dispute rate
    if vertical in ("travel", "gaming", "marketplace"):
        dispute_rate = float(rng.uniform(0.010, 0.018))
    elif vertical in ("healthcare", "real_estate", "b2b_saas"):
        dispute_rate = float(rng.uniform(0.012, 0.020))
    elif vertical in ("qsr", "grocery"):
        dispute_rate = float(rng.uniform(0.003, 0.007))
    else:
        dispute_rate = float(rng.uniform(0.005, 0.012))

    # Interchange programs
    if primary_channel == "pos":
        ic_programs = {
            "credit":     ["CPS_RETAIL", "MC_MERIT_III", "MC_MERIT_I"],
            "debit":      ["REGULATED_DEBIT", "SUPERMARKET"],
            "prepaid":    ["CPS_RETAIL"],
            "commercial": ["CPS_RETAIL"],
        }
    elif primary_channel == "recurring":
        ic_programs = {
            "credit":     ["CPS_ECOMM", "EIRF"],
            "debit":      ["REGULATED_DEBIT"],
            "prepaid":    ["EIRF"],
            "commercial": ["STD_IRF"],
        }
    elif primary_channel == "moto":
        ic_programs = {
            "credit":     ["EIRF", "STD_IRF"],
            "debit":      ["REGULATED_DEBIT"],
            "prepaid":    ["EIRF", "STD_IRF"],
            "commercial": ["STD_IRF"],
        }
    else:
        ic_programs = {
            "credit":     ["CPS_ECOMM", "EIRF", "STD_IRF"],
            "debit":      ["REGULATED_DEBIT", "CPS_ECOMM"],
            "prepaid":    ["EIRF"],
            "commercial": ["STD_IRF"],
        }

    return {
        "id":           f"MERCH_{idx+1:04d}",
        "account_id":   f"acct_{vertical[:4]}{idx+1:06d}",
        "name":         f"Merchant_{idx+1:04d}_{vertical.replace('_','').title()}",
        "statement_descriptor": f"{vertical[:8].upper()}{idx+1}",
        "vertical":        vertical,
        "size_tier":       size_tier,
        "primary_channel": primary_channel,
        "aov_min":         aov_lo,
        "aov_max":         aov_hi,
        "base_daily":      base_daily,
        "monthly_growth":  monthly_growth,
        "auth_rate":       auth_rate,
        "card_funding_weights": _norm(fw),
        "card_brand_weights":   _norm(bw),
        "card_countries":       countries,
        "card_country_weights": ctry_w,
        "currencies":      currencies,
        "currency_weights": curr_w,
        "guest_rate":       guest_rate,
        "network_token_rate": network_token_rate,
        "apple_rate":       apple_rate,
        "google_rate":      google_rate,
        "link_rate":        link_rate,
        "dispute_rate":     dispute_rate,
        "ic_programs":      ic_programs,
    }


# ---------------------------------------------------------------------------
# Daily volume simulation
# ---------------------------------------------------------------------------

def day_volume(merchant, d, rng):
    month_idx = d.month - 1
    growth    = (1 + merchant["monthly_growth"]) ** month_idx
    base      = merchant["base_daily"] * growth

    if d.month in (10, 11, 12):
        base *= 1.25
    if d.weekday() >= 5:
        base *= WEEKEND_MULT.get(merchant["vertical"], 1.0)
    if (d.month, d.day) in US_HOLIDAYS_2024:
        base *= HOLIDAY_MULT.get(merchant["vertical"], 1.2)

    return max(0, int(rng.poisson(max(1.0, base))))


# ---------------------------------------------------------------------------
# Transaction generation
# ---------------------------------------------------------------------------

def generate_merchant(merchant, rng, f):
    m  = merchant
    ch = m["primary_channel"]

    # Per-channel static distributions
    cvc_opts    = ["pass", "fail", "unavailable", "unchecked", None]
    postal_opts = ["pass", "fail", "unavailable", "unchecked", None]
    addr_opts   = ["pass", "fail", "unavailable", "unchecked", None]
    tds_opts    = ["authenticated", "attempt_acknowledged", "exempted", "failed", "not_supported", None]
    tds_ver_opts    = ["1.0.2", "2.1.0", "2.2.0", None]
    tds_reason_opts = ["abandoned", "bypassed", "card_not_enrolled", "network_not_supported", None]

    if ch == "pos":
        cvc_w    = [0.97, 0.02, 0.0,  0.01, 0.0]
        postal_w = [0.88, 0.05, 0.0,  0.07, 0.0]
        addr_w   = [0.83, 0.05, 0.0,  0.12, 0.0]
        tds_w    = [0.0,  0.0,  0.0,  0.0,  0.05, 0.95]
        dev_opts = ["pos_terminal", None]; dev_w = [0.95, 0.05]
    elif ch == "ecommerce":
        cvc_w    = [0.68, 0.08, 0.0,  0.14, 0.10]
        postal_w = [0.65, 0.10, 0.0,  0.13, 0.12]
        addr_w   = [0.58, 0.12, 0.0,  0.16, 0.14]
        tds_w    = [0.35, 0.15, 0.20, 0.10, 0.10, 0.10]
        dev_opts = ["mobile", "desktop", "tablet", None]; dev_w = [0.55, 0.35, 0.08, 0.02]
    elif ch == "recurring":
        cvc_w    = [0.18, 0.04, 0.0,  0.10, 0.68]
        postal_w = [0.14, 0.04, 0.0,  0.10, 0.72]
        addr_w   = [0.11, 0.04, 0.0,  0.08, 0.77]
        tds_w    = [0.10, 0.05, 0.40, 0.05, 0.05, 0.35]
        dev_opts = ["mobile", "desktop", None]; dev_w = [0.40, 0.50, 0.10]
    else:  # moto
        cvc_w    = [0.52, 0.10, 0.0,  0.0,  0.38]
        postal_w = [0.42, 0.10, 0.0,  0.0,  0.48]
        addr_w   = [0.38, 0.10, 0.0,  0.0,  0.52]
        tds_w    = [0.0,  0.0,  0.0,  0.0,  0.05, 0.95]
        dev_opts = [None]; dev_w = [1.0]

    # Simulate 365 daily volumes and build total N
    start_date   = date(2024, 1, 1)
    daily_counts = [day_volume(m, start_date + timedelta(days=d), rng) for d in range(365)]
    total_n      = sum(daily_counts)
    if total_n == 0:
        return 0

    # Build timestamp array from daily volumes
    ts_arr  = np.empty(total_n, dtype=np.int64)
    pos_idx = 0
    for day_off, cnt in enumerate(daily_counts):
        if cnt == 0:
            continue
        d         = start_date + timedelta(days=day_off)
        day_start = int(datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=timezone.utc).timestamp())
        ts_arr[pos_idx:pos_idx + cnt] = rng.integers(day_start, day_start + 86399, size=cnt)
        pos_idx += cnt
    ts_arr.sort()

    n = total_n

    # Bulk attribute generation
    fundings = rng.choice(CARD_FUNDINGS, size=n, p=m["card_funding_weights"])
    brands   = rng.choice(CARD_BRANDS,   size=n, p=m["card_brand_weights"])
    ctries   = rng.choice(m["card_countries"], size=n, p=m["card_country_weights"])
    currs    = rng.choice(m["currencies"],      size=n, p=m["currency_weights"])
    amounts  = rng.integers(m["aov_min"], m["aov_max"] + 1, size=n)

    auth_mask    = rng.random(n) < m["auth_rate"]
    retry_mask   = ~auth_mask & (rng.random(n) < 0.4)
    attempt_nums = np.ones(n, dtype=np.int32)
    attempt_nums[retry_mask] = rng.integers(2, 4, size=int(retry_mask.sum()))

    is_guest = rng.random(n) < m["guest_rate"]
    is_nt    = rng.random(n) < m["network_token_rate"]
    if ch == "pos":
        is_nt[:] = False

    wallet = np.full(n, None, dtype=object)
    ap = rng.random(n) < m["apple_rate"]
    gp = ~ap & (rng.random(n) < m["google_rate"])
    lk = ~ap & ~gp & (rng.random(n) < m["link_rate"])
    wallet[ap] = "apple_pay"
    wallet[gp] = "google_pay"
    wallet[lk] = "link"

    pi_ids       = gen_ids("pi_",  24, n, rng)
    fingerprints = gen_fingerprints(n, rng)
    card_bins    = gen_bins(brands, rng)
    ch_ids       = gen_ids("ch_",  24, n, rng)
    txn_ids      = gen_ids("txn_", 24, n, rng)
    cus_ids      = gen_ids("cus_", 16, n, rng)
    cust_nums    = rng.integers(10000, 99999, size=n)

    cvc_arr    = rng.choice(cvc_opts,    size=n, p=cvc_w)
    postal_arr = rng.choice(postal_opts, size=n, p=postal_w)
    addr_arr   = rng.choice(addr_opts,   size=n, p=addr_w)
    tds_arr    = rng.choice(tds_opts,    size=n, p=tds_w)

    tds_ver = np.full(n, None, dtype=object)
    has_tds = tds_arr != None  # noqa: E711
    if has_tds.sum():
        vi = rng.choice([0, 1, 2, 3], size=int(has_tds.sum()), p=[0.10, 0.40, 0.45, 0.05])
        tds_ver[has_tds] = np.array(tds_ver_opts, dtype=object)[vi]

    tds_reason = np.full(n, None, dtype=object)
    bad_tds    = np.isin(tds_arr, ["failed", "not_supported"])
    if bad_tds.sum():
        ri = rng.choice(len(tds_reason_opts), size=int(bad_tds.sum()),
                        p=[0.25, 0.20, 0.30, 0.15, 0.10])
        tds_reason[bad_tds] = np.array(tds_reason_opts, dtype=object)[ri]

    fail_codes = np.full(n, None, dtype=object)
    nd = int((~auth_mask).sum())
    if nd:
        di = rng.choice(len(DECLINE_CODES), size=nd, p=DECLINE_WEIGHTS)
        fail_codes[~auth_mask] = np.array(DECLINE_CODES, dtype=object)[di]

    radar_scores   = rng.integers(0, 100, size=n)
    outcome_scores = rng.integers(0, 100, size=n)
    radar_levels   = np.where(radar_scores < 40, "normal",
                              np.where(radar_scores < 75, "elevated", "highest"))
    outcome_levels = np.where(outcome_scores < 40, "normal",
                              np.where(outcome_scores < 75, "elevated", "highest"))
    radar_outcomes = np.where(radar_scores < 60, "allow",
                              np.where(radar_scores < 85, "review", "block"))

    last4s     = rng.integers(1000, 9999, size=n)
    exp_months = rng.integers(1, 13, size=n)
    exp_years  = rng.integers(2024, 2029, size=n)
    devices    = rng.choice(dev_opts, size=n, p=dev_w)

    settle_offsets   = rng.choice([1, 2], size=n, p=[0.7, 0.3])
    us_postal_idx    = rng.integers(0, len(US_POSTALS),     size=n)
    nonus_postal_idx = rng.integers(0, len(NON_US_POSTALS), size=n)
    ip_rand          = rng.random(n)
    ip_fallback      = rng.choice(["US", "GB", "DE", "FR", "CA", "AU", "NL", "SG"], size=n)
    dispute_rand     = rng.random(n)
    dispute_rsn_arr  = rng.choice(DISPUTE_REASONS, size=n, p=DISPUTE_WEIGHTS)

    # Vectorised interchange BPS -----------------------------------------------
    bps_arr = np.zeros(n, dtype=np.int32)

    amex_m       = auth_mask & (brands == "amex")
    commercial_m = auth_mask & ~amex_m & (fundings == "commercial")
    prepaid_m    = auth_mask & ~amex_m & (fundings == "prepaid")
    credit_m     = auth_mask & ~amex_m & (fundings == "credit")
    debit_m      = auth_mask & ~amex_m & (fundings == "debit")

    if amex_m.sum():
        bps_arr[amex_m] = rng.integers(270, 320, size=int(amex_m.sum()))
    if commercial_m.sum():
        bps_arr[commercial_m] = rng.integers(220, 280, size=int(commercial_m.sum()))
    if prepaid_m.sum():
        bps_arr[prepaid_m] = rng.integers(165, 190, size=int(prepaid_m.sum()))
    if credit_m.sum():
        lo, hi = (195, 220) if ch == "ecommerce" else (150, 175) if ch == "pos" else \
                 (185, 200) if ch == "recurring" else (175, 210)
        bps_arr[credit_m] = rng.integers(lo, hi, size=int(credit_m.sum()))
    if debit_m.sum():
        lo, hi = (120, 140) if ch == "ecommerce" else (70, 90) if ch == "pos" else (95, 120)
        bps_arr[debit_m] = rng.integers(lo, hi, size=int(debit_m.sum()))

    ic_amount_arr  = np.where(auth_mask, (amounts * bps_arr / 10000).astype(np.int32), 0)
    net_fee_arr    = np.where(auth_mask, (amounts * 0.0011 + 2).astype(np.int32),     0)
    stripe_fee_arr = np.where(auth_mask, (amounts * 0.029  + 30).astype(np.int32),    0)

    ic_prog_arr = np.full(n, None, dtype=object)
    for funding_type in CARD_FUNDINGS:
        fmask = auth_mask & (fundings == funding_type)
        if not fmask.sum():
            continue
        progs = m["ic_programs"].get(funding_type, ["CPS_ECOMM"])
        ic_prog_arr[fmask] = rng.choice(progs, size=int(fmask.sum()))
    # --------------------------------------------------------------------------

    batch = []
    for i in range(n):
        ts   = int(ts_arr[i])
        dt   = datetime.fromtimestamp(ts, tz=timezone.utc)
        auth = bool(auth_mask[i])

        funding  = str(fundings[i])
        brand    = str(brands[i])
        country  = str(ctries[i])
        currency = str(currs[i])
        amount   = int(amounts[i])
        fc       = fail_codes[i]
        if fc is not None:
            fc = str(fc)

        if auth:
            out_type       = "authorized"
            out_net_status = "approved_by_network"
            out_net_code   = "00"
            out_reason     = None
            charge_id      = ch_ids[i]
            captured       = amount
            bal_txn        = txn_ids[i]
            settle_dt      = (dt + timedelta(days=int(settle_offsets[i]))).strftime("%Y-%m-%d")
        else:
            out_type       = OUTCOME_FOR_FAILURE.get(fc, "issuer_declined")
            out_net_status = "not_sent_to_network" if fc == "suspected_fraud" else "declined_by_network"
            out_net_code   = NETWORK_DECLINE_CODE.get(fc)
            out_reason     = "highest_risk_level" if out_type in ("blocked", "invalid") else None
            charge_id      = None
            captured       = 0
            bal_txn        = None
            settle_dt      = None

        bps       = int(bps_arr[i])       if auth else None
        ic_amount = int(ic_amount_arr[i]) if auth else None
        net_fee   = int(net_fee_arr[i])   if auth else None
        sf        = int(stripe_fee_arr[i]) if auth else None
        ic_prog   = str(ic_prog_arr[i])   if auth else None

        rate       = EXCHANGE_RATES.get(currency, 1.0)
        amount_usd = int(amount * rate)

        if is_guest[i]:
            cust_id    = None
            cust_email = None
        else:
            cust_id    = cus_ids[i]
            cust_email = f"user{int(cust_nums[i])}@example.com"

        ip_country = str(ip_fallback[i]) if ip_rand[i] < 0.05 else country

        billing_postal = (US_POSTALS[int(us_postal_idx[i])] if country == "US"
                          else NON_US_POSTALS[int(nonus_postal_idx[i])])

        disputed   = auth and bool(dispute_rand[i] < m["dispute_rate"])
        disp_reason = str(dispute_rsn_arr[i]) if disputed else None

        record = {
            "id":                              pi_ids[i],
            "charge_id":                       charge_id,
            "merchant_account_id":             m["account_id"],
            "merchant_name":                   m["name"],
            "customer_id":                     cust_id,
            "attempt_number":                  int(attempt_nums[i]),
            "created":                         ts,
            "created_at":                      dt.isoformat(),
            "card_brand":                      brand,
            "card_funding":                    funding,
            "card_country":                    country,
            "card_last4":                      str(int(last4s[i])),
            "card_exp_month":                  int(exp_months[i]),
            "card_exp_year":                   int(exp_years[i]),
            "card_fingerprint":                fingerprints[i],
            "card_network":                    brand,
            "card_wallet":                     wallet[i],
            "card_bin":                        card_bins[i],
            "network_token_used":              bool(is_nt[i]),
            "checks_cvc_check":                cvc_arr[i],
            "checks_address_postal_code_check": postal_arr[i],
            "checks_address_line1_check":      addr_arr[i],
            "three_d_secure_result":           tds_arr[i],
            "three_d_secure_version":          tds_ver[i],
            "three_d_secure_result_reason":    tds_reason[i],
            "outcome_network_status":          out_net_status,
            "outcome_type":                    out_type,
            "outcome_risk_level":              str(outcome_levels[i]),
            "outcome_risk_score":              int(outcome_scores[i]),
            "outcome_reason":                  out_reason,
            "failure_code":                    fc,
            "outcome_network_decline_code":    out_net_code,
            "amount":                          amount,
            "amount_captured":                 captured,
            "currency":                        currency,
            "amount_usd_cents":                amount_usd,
            "billing_address_country":         country,
            "billing_address_postal_code":     billing_postal,
            "customer_email":                  cust_email,
            "customer_ip_country":             ip_country,
            "device_type":                     devices[i],
            "shopper_interaction":             ch,
            "is_guest_checkout":               bool(is_guest[i]),
            "statement_descriptor":            m["statement_descriptor"],
            "radar_risk_score":                int(radar_scores[i]),
            "radar_risk_level":                str(radar_levels[i]),
            "radar_outcome":                   str(radar_outcomes[i]),
            "disputed":                        disputed,
            "dispute_reason":                  disp_reason,
            "interchange_amount_cents":        ic_amount,
            "interchange_rate_bps":            bps,
            "interchange_program":             ic_prog,
            "network_fee_cents":               net_fee,
            "stripe_fee_cents":                sf,
            "balance_transaction_id":          bal_txn,
            "settlement_date":                 settle_dt,
        }
        batch.append(record)
        if len(batch) >= 50_000:
            f.write(b"\n".join(orjson.dumps(r) for r in batch) + b"\n")
            batch.clear()

    if batch:
        f.write(b"\n".join(orjson.dumps(r) for r in batch) + b"\n")

    return n


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic payment data.")
    parser.add_argument("--num-merchants", type=int, default=50)
    parser.add_argument("--seed",          type=int, default=42)
    args = parser.parse_args()

    t0  = time.time()
    rng = np.random.default_rng(args.seed)

    merchants = [gen_merchant(i, rng) for i in range(args.num_merchants)]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    total_rows = 0
    with gzip.open(OUTPUT_PATH, "wb") as f:
        for m in merchants:
            total_rows += generate_merchant(m, rng, f)

    elapsed     = time.time() - t0
    file_size_mb = os.path.getsize(OUTPUT_PATH) / 1024 / 1024

    print(f"Merchants generated: {args.num_merchants}")
    print(f"Total rows: {total_rows:,}")
    print(f"Time elapsed: {elapsed:.1f}s")
    print(f"File size: {file_size_mb:.1f} MB (compressed)")


if __name__ == "__main__":
    main()
