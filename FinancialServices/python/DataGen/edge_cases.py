from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd


def apply_edge_cases(config: dict, customers: pd.DataFrame, cards: pd.DataFrame, transactions: pd.DataFrame, rng) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    edge = config.get("edge_cases", {})
    if not edge.get("enable", True):
        return customers, cards, transactions

    customers = customers.copy()
    cards = cards.copy()
    transactions = transactions.copy()

    # Customers with no cards
    n_no_cards = min(int(edge.get("customers_with_no_cards", 0)), len(customers))
    if n_no_cards > 0 and len(cards) > 0:
        no_card_customers = rng.choice(customers["CustomerId"].to_numpy(), size=n_no_cards, replace=False)
        reassign_mask = cards["Customer"].isin(no_card_customers)
        if reassign_mask.any():
            allowed = customers.loc[~customers["CustomerId"].isin(no_card_customers), "CustomerId"].to_numpy()
            if len(allowed) > 0:
                cards.loc[reassign_mask, "Customer"] = rng.choice(allowed, size=int(reassign_mask.sum()), replace=True)

    # Cards with only declines
    n_only_declines = min(int(edge.get("cards_with_only_declines", 0)), cards["CardId"].nunique())
    if n_only_declines > 0 and len(transactions) > 0:
        chosen_cards = rng.choice(cards["CardId"].to_numpy(), size=n_only_declines, replace=False)
        mask = transactions["Card"].isin(chosen_cards)
        transactions.loc[mask, "Status"] = "DECLINED"
        decline_reasons = ["INSUFFICIENT_FUNDS", "SUSPECTED_FRAUD", "LIMIT_EXCEEDED", "INVALID_CVV"]
        transactions.loc[mask, "DeclineReason"] = rng.choice(decline_reasons, size=int(mask.sum()), replace=True)

    # Blocked cards mid-window
    n_blocked = min(int(edge.get("blocked_cards_mid_window", 0)), len(cards))
    if n_blocked > 0:
        blocked_cards = rng.choice(cards["CardId"].to_numpy(), size=n_blocked, replace=False)
        cards.loc[cards["CardId"].isin(blocked_cards), "Status"] = "BLOCKED"

    # Fraud bursts
    burst_cfg = edge.get("fraud_bursts", {})
    n_burst_cards = min(int(burst_cfg.get("count_cards", 0)), cards["CardId"].nunique())
    txns_per_card = int(burst_cfg.get("txns_per_card", 0))
    burst_hours = int(burst_cfg.get("burst_hours", 2))
    amount_lo, amount_hi = burst_cfg.get("amount_range", [1.0, 25.0])

    if n_burst_cards > 0 and txns_per_card > 0 and len(transactions) > 0:
        candidate_cards = rng.choice(cards["CardId"].to_numpy(), size=n_burst_cards, replace=False)
        start = pd.Timestamp(config["time"]["start_date"], tz="UTC")
        days = int(config["time"]["days"])
        end = start + timedelta(days=days)
        card_time = cards.set_index("CardId")[["OpenedAt", "ClosedAt"]].copy()
        card_time["OpenedAt"] = pd.to_datetime(card_time["OpenedAt"], utc=True)
        card_time["ClosedAt"] = pd.to_datetime(card_time["ClosedAt"], utc=True, errors="coerce")

        for card_id in candidate_cards:
            card_idx = transactions.index[transactions["Card"] == card_id].to_numpy()
            if len(card_idx) == 0:
                continue
            opened_at = card_time.at[card_id, "OpenedAt"]
            closed_at = card_time.at[card_id, "ClosedAt"]
            valid_start = max(start, opened_at)
            valid_end = min(end, closed_at) if pd.notna(closed_at) else end
            if valid_end <= valid_start:
                continue
            take = min(txns_per_card, len(card_idx))
            chosen = rng.choice(card_idx, size=take, replace=False)
            span_days = max(1, int((valid_end - valid_start).days) + 1)
            burst_start = valid_start + timedelta(days=int(rng.integers(0, span_days)))
            for idx in chosen:
                auth = burst_start + timedelta(minutes=int(rng.integers(0, max(1, burst_hours * 60))))
                if auth >= valid_end:
                    auth = valid_end - timedelta(minutes=1)
                if auth < valid_start:
                    auth = valid_start
                posted = auth + timedelta(minutes=int(rng.integers(0, 15)))
                transactions.at[idx, "AuthAt"] = auth.strftime("%Y-%m-%dT%H:%M:%SZ")
                transactions.at[idx, "PostedAt"] = posted.strftime("%Y-%m-%dT%H:%M:%SZ")
                transactions.at[idx, "Amount"] = round(float(rng.uniform(amount_lo, amount_hi)), 2)
                transactions.at[idx, "Channel"] = "ECOM"
                transactions.at[idx, "EntryMode"] = "MANUAL"
                transactions.at[idx, "CardPresent"] = False
                transactions.at[idx, "Status"] = "APPROVED"
                transactions.at[idx, "DeclineReason"] = None
                transactions.at[idx, "IsFraud"] = True

    return customers, cards, transactions
