from __future__ import annotations

from datetime import timedelta

import pandas as pd

from DataGen.generators.helpers import segment_lookup


def generate_customers(config: dict, rng) -> pd.DataFrame:
    count = config["resolved_counts"]["customers"]
    segments_cfg = config["behavior"]["segments"]
    segment_names = [x["name"] for x in segments_cfg]
    segment_weights = [x["weight"] for x in segments_cfg]
    lookup = segment_lookup(segments_cfg)

    start_date = pd.Timestamp(config["time"]["start_date"], tz="UTC")
    created_days_before = rng.integers(1, 365 * 3, size=count)
    created_seconds = rng.integers(0, 24 * 3600, size=count)
    created_at = [
        (start_date - timedelta(days=int(d), seconds=int(s))).isoformat()
        for d, s in zip(created_days_before, created_seconds)
    ]

    segments = rng.choice(segment_names, size=count, p=segment_weights)
    status = rng.choice(["ACTIVE", "CLOSED"], size=count, p=[0.96, 0.04])

    risk_scores: list[int] = []
    for segment in segments:
        if segment == "HIGHRISK":
            score = int(rng.normal(75, 12))
        elif segment == "AFFLUENT":
            score = int(rng.normal(35, 10))
        elif segment == "DORMANT":
            score = int(rng.normal(45, 12))
        else:
            score = int(rng.normal(50, 15))
        risk_scores.append(max(0, min(100, score)))

    us_states = [
        "CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI",
        "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI",
    ]
    states = rng.choice(us_states, size=count)
    df = pd.DataFrame(
        {
            "CustomerId": range(1, count + 1),
            "CreatedAt": created_at,
            "Status": status,
            "Segment": segments,
            "RiskScore": risk_scores,
            "State": states,
            "SegmentTxnMultiplier": [lookup[s]["txn_rate_multiplier"] for s in segments],
            "SegmentAmountMultiplier": [lookup[s]["avg_amount_multiplier"] for s in segments],
            "SegmentEcomMultiplier": [lookup[s]["ecom_multiplier"] for s in segments],
            "SegmentDeclineMultiplier": [lookup[s]["decline_multiplier"] for s in segments],
            "SegmentDisputeMultiplier": [lookup[s]["dispute_multiplier"] for s in segments],
        }
    )
    return df
