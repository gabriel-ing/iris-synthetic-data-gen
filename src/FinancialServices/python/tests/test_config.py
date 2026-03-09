from __future__ import annotations

from synthetic_data_gen.config import load_config


def test_explicit_counts_are_resolved(tmp_path):
    path = tmp_path / "cfg.yaml"
    path.write_text(
        """
seed: 7
scale:
  mode: explicit
  counts:
    customers: 11
    merchants: 12
    cards: 13
    transactions: 14
    disputes: 15
""",
        encoding="utf-8",
    )
    cfg = load_config(path)
    assert cfg["resolved_counts"] == {
        "customers": 11,
        "merchants": 12,
        "cards": 13,
        "transactions": 14,
        "disputes": 15,
    }


def test_factor_mode_derives_counts(tmp_path):
    path = tmp_path / "cfg_factor.yaml"
    path.write_text(
        """
scale:
  mode: factor
  factor: 3
  base_counts:
    customers: 10
    merchants: 20
    cards: 30
    transactions: 40
    disputes: 50
""",
        encoding="utf-8",
    )
    cfg = load_config(path)
    assert cfg["resolved_counts"] == {
        "customers": 30,
        "merchants": 60,
        "cards": 90,
        "transactions": 120,
        "disputes": 150,
    }
