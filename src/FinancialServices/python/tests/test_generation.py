from __future__ import annotations

import pandas as pd
from pandas.testing import assert_frame_equal

from synthetic_data_gen.validate import validate_all
from conftest import build_dataset, load_small_config


def test_generation_is_deterministic_for_same_seed(tmp_path):
    cfg_a = load_small_config(tmp_path / "a", seed=123)
    a_customers, a_cards, a_merchants, a_tx, a_disputes = build_dataset(cfg_a)

    cfg_b = load_small_config(tmp_path / "b", seed=123)
    b_customers, b_cards, b_merchants, b_tx, b_disputes = build_dataset(cfg_b)

    assert_frame_equal(a_customers, b_customers, check_like=False)
    assert_frame_equal(a_cards, b_cards, check_like=False)
    assert_frame_equal(a_merchants, b_merchants, check_like=False)
    assert_frame_equal(a_tx, b_tx, check_like=False)
    assert_frame_equal(a_disputes, b_disputes, check_like=False)


def test_generation_passes_core_validation(tmp_path):
    cfg = load_small_config(tmp_path)
    customers, cards, merchants, transactions, disputes = build_dataset(cfg)

    result = validate_all(cfg, customers, cards, merchants, transactions, disputes)
    assert result.ok is True
    assert len(result.checks) >= 10

    assert len(customers) == cfg["resolved_counts"]["customers"]
    assert len(cards) == cfg["resolved_counts"]["cards"]
    assert len(merchants) == cfg["resolved_counts"]["merchants"]
    assert len(transactions) == cfg["resolved_counts"]["transactions"]
    assert len(disputes) == cfg["resolved_counts"]["disputes"]

    tx_auth = pd.to_datetime(transactions["AuthAt"], utc=True)
    start = pd.Timestamp(cfg["time"]["start_date"], tz="UTC")
    end = start + pd.Timedelta(days=int(cfg["time"]["days"]))
    assert tx_auth.min() >= start
    assert tx_auth.max() <= end
