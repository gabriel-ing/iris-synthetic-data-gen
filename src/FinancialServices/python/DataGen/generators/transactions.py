from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from DataGen.rng import normalize_weights


CATEGORY_AMOUNT = {
    "GROCERY": (2.8, 0.55),
    "FUEL": (3.0, 0.45),
    "DINING": (3.2, 0.60),
    "TRAVEL": (4.0, 0.95),
    "RETAIL": (3.3, 0.75),
    "DIGITAL": (2.9, 0.80),
}


def _safe_probability(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, 0.0001, None)
    return normalize_weights(values)


def _daily_target_counts(total: int, days: int) -> np.ndarray:
    base = total // days
    rem = total % days
    out = np.full(days, base, dtype=int)
    out[:rem] += 1
    return out


def generate_transactions(config: dict, customers: pd.DataFrame, cards: pd.DataFrame, merchants: pd.DataFrame, rng) -> list[pd.DataFrame]:
    total_txn = config["resolved_counts"]["transactions"]
    start = pd.Timestamp(config["time"]["start_date"], tz="UTC")
    days = int(config["time"]["days"])
    tx_cfg = config["behavior"]["transactions"]
    base_ecom = float(tx_cfg["base_ecom_share"])
    base_decline = float(tx_cfg["base_decline_rate"])
    base_refund = float(tx_cfg["base_refund_rate"])
    weekly = bool(tx_cfg.get("weekly_seasonality", True))

    cards_join = cards.merge(
        customers[
            [
                "CustomerId",
                "Segment",
                "RiskScore",
                "SegmentTxnMultiplier",
                "SegmentAmountMultiplier",
                "SegmentEcomMultiplier",
                "SegmentDeclineMultiplier",
            ]
        ],
        left_on="Customer",
        right_on="CustomerId",
        how="left",
    )
    card_weights = _safe_probability(cards_join["SegmentTxnMultiplier"].to_numpy(dtype=float))
    merchant_weights = _safe_probability(merchants["PopularityWeight"].to_numpy(dtype=float))

    merchant_category = merchants.set_index("MerchantId")["Category"].to_dict()
    merchant_risk = merchants.set_index("MerchantId")["RiskTier"].to_dict()
    card_opened = pd.to_datetime(cards_join["OpenedAt"], utc=True)
    card_closed = pd.to_datetime(cards_join["ClosedAt"], utc=True, errors="coerce")

    card_ids = cards_join["CardId"].to_numpy()
    merchant_ids = merchants["MerchantId"].to_numpy()

    day_counts = _daily_target_counts(total_txn, days)
    if weekly:
        day_idx = np.arange(days)
        dow = (start.dayofweek + day_idx) % 7
        multiplier = np.where(dow >= 5, 1.12, 0.96)
        adjusted = np.floor(day_counts * multiplier).astype(int)
        adjusted[0] += total_txn - adjusted.sum()
        day_counts = adjusted

    frames: list[pd.DataFrame] = []
    txn_id = 1
    decline_reasons = ["INSUFFICIENT_FUNDS", "SUSPECTED_FRAUD", "LIMIT_EXCEEDED", "INVALID_CVV"]
    decline_reason_p = [0.48, 0.22, 0.20, 0.10]

    for day_offset, n_today in enumerate(day_counts):
        day_start = start + timedelta(days=int(day_offset))
        day_end = day_start + timedelta(days=1)
        eligible = (card_opened <= day_end) & (card_closed.isna() | (card_closed >= day_start))
        eligible_idx = np.flatnonzero(eligible.to_numpy())
        if len(eligible_idx) == 0:
            eligible_idx = np.arange(len(card_ids))
        eligible_weights = card_weights[eligible_idx]
        eligible_weights = eligible_weights / eligible_weights.sum()
        chosen_card_idx = rng.choice(eligible_idx, size=n_today, p=eligible_weights)
        day_card_ids = card_ids[chosen_card_idx]
        day_merchant_ids = rng.choice(merchant_ids, size=n_today, p=merchant_weights)

        seg_ecom = cards_join.iloc[chosen_card_idx]["SegmentEcomMultiplier"].to_numpy(dtype=float)
        seg_amt = cards_join.iloc[chosen_card_idx]["SegmentAmountMultiplier"].to_numpy(dtype=float)
        seg_decl = cards_join.iloc[chosen_card_idx]["SegmentDeclineMultiplier"].to_numpy(dtype=float)
        risk_score = cards_join.iloc[chosen_card_idx]["RiskScore"].to_numpy(dtype=float)

        ecom_prob = np.clip(base_ecom * seg_ecom, 0.01, 0.95)
        is_ecom = rng.random(n_today) < ecom_prob
        channel = np.where(is_ecom, "ECOM", "POS")
        card_present = ~is_ecom
        entry_mode = np.where(is_ecom, "MANUAL", rng.choice(["CHIP", "TAP"], size=n_today, p=[0.45, 0.55]))

        merchant_category_arr = np.array([merchant_category[m] for m in day_merchant_ids])
        merchant_risk_arr = np.array([merchant_risk[m] for m in day_merchant_ids])
        amount = np.empty(n_today, dtype=float)
        for cat in CATEGORY_AMOUNT:
            mask = merchant_category_arr == cat
            if mask.any():
                mean, sigma = CATEGORY_AMOUNT[cat]
                amount[mask] = rng.lognormal(mean=mean, sigma=sigma, size=int(mask.sum()))

        amount = amount * seg_amt
        amount = np.clip(amount, 0.5, 9999.0)
        amount = np.round(amount, 2)

        risk_mult = 1.0 + (risk_score / 100.0) * 0.7
        ecom_mult = np.where(is_ecom, 1.35, 1.0)
        high_amt_mult = np.where(amount > np.percentile(amount, 92), 1.5, 1.0)
        decline_prob = np.clip(base_decline * seg_decl * risk_mult * ecom_mult * high_amt_mult, 0.01, 0.9)
        is_declined = rng.random(n_today) < decline_prob

        status = np.where(is_declined, "DECLINED", "APPROVED")
        decline_reason = np.where(
            is_declined,
            rng.choice(decline_reasons, size=n_today, p=decline_reason_p),
            None,
        )

        refund_prob = np.clip(base_refund * np.where(is_ecom, 1.4, 0.9) * np.where(merchant_category_arr == "TRAVEL", 1.8, 1.0), 0.0, 0.25)
        refund_hit = (~is_declined) & (rng.random(n_today) < refund_prob)
        reverse_hit = (~is_declined) & (~refund_hit) & (rng.random(n_today) < (base_refund * 0.35))
        status = np.where(refund_hit, "REFUNDED", status)
        status = np.where(reverse_hit, "REVERSED", status)

        secs = rng.integers(0, 24 * 3600, size=n_today)
        auth_at = pd.Series(pd.to_datetime(day_start) + pd.to_timedelta(secs, unit="s"))
        opened_vals = card_opened.iloc[chosen_card_idx].to_numpy()
        closed_vals = card_closed.iloc[chosen_card_idx].to_numpy()
        auth_np = auth_at.to_numpy()
        auth_np = np.maximum(auth_np, opened_vals)
        max_bound = np.where(pd.isna(closed_vals), auth_np, closed_vals)
        auth_np = np.minimum(auth_np, max_bound)
        auth_at = pd.Series(pd.to_datetime(auth_np, utc=True))
        post_delay = rng.integers(0, 180, size=n_today)
        posted_at = auth_at + pd.to_timedelta(post_delay, unit="m")

        posted_at = posted_at.where(posted_at >= auth_at, auth_at)

        is_fraud = (merchant_risk_arr == "HIGH") & is_ecom & (rng.random(n_today) < 0.08)
        is_fraud = is_fraud | ((risk_score > 85) & is_ecom & (rng.random(n_today) < 0.03))

        frame = pd.DataFrame(
            {
                "TransactionId": np.arange(txn_id, txn_id + n_today),
                "Card": day_card_ids,
                "Merchant": day_merchant_ids,
                "AuthAt": pd.to_datetime(auth_at, utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "PostedAt": pd.to_datetime(posted_at, utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "Amount": amount,
                "Currency": config["currency"],
                "Channel": channel,
                "EntryMode": entry_mode,
                "CardPresent": card_present,
                "Status": status,
                "DeclineReason": decline_reason,
                "IsFraud": is_fraud,
            }
        )
        frames.append(frame)
        txn_id += n_today

    return frames
