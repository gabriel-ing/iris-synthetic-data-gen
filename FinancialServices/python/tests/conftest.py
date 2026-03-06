from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from synthetic_data_gen.config import load_config
from synthetic_data_gen.edge_cases import apply_edge_cases
from synthetic_data_gen.generators.cards import generate_cards
from synthetic_data_gen.generators.customers import generate_customers
from synthetic_data_gen.generators.disputes import generate_disputes
from synthetic_data_gen.generators.merchants import generate_merchants
from synthetic_data_gen.generators.transactions import generate_transactions
from synthetic_data_gen.rng import make_rng


def build_dataset(config: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    seed = int(config["seed"])
    merchants = generate_merchants(config, make_rng(seed, "merchants"))
    customers = generate_customers(config, make_rng(seed, "customers"))
    cards = generate_cards(config, customers, make_rng(seed, "cards"))
    tx_frames = generate_transactions(config, customers, cards, merchants, make_rng(seed, "transactions"))
    transactions = pd.concat(tx_frames, ignore_index=True)
    customers, cards, transactions = apply_edge_cases(config, customers, cards, transactions, make_rng(seed, "edge_cases"))
    disputes = generate_disputes(config, customers, cards, merchants, transactions, make_rng(seed, "disputes"))
    return customers, cards, merchants, transactions, disputes


def write_config(tmp_path: Path, data: dict) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return config_path


def small_config_dict(tmp_path: Path, seed: int = 42, partition: str = "none") -> dict:
    return {
        "seed": seed,
        "currency": "USD",
        "time": {
            "start_date": "2026-01-01",
            "days": 30,
            "timezone": "UTC",
        },
        "scale": {
            "mode": "explicit",
            "counts": {
                "customers": 80,
                "merchants": 40,
                "cards": 110,
                "transactions": 1200,
                "disputes": 35,
            },
        },
        "output": {
            "format": "csv",
            "path": str(tmp_path / "out"),
            "partition_transactions_by": partition,
            "overwrite": True,
        },
        "edge_cases": {
            "enable": True,
            "customers_with_no_cards": 4,
            "cards_with_only_declines": 4,
            "blocked_cards_mid_window": 4,
            "fraud_bursts": {
                "count_cards": 3,
                "txns_per_card": 8,
                "burst_hours": 2,
                "amount_range": [1.0, 25.0],
            },
        },
    }


def load_small_config(tmp_path: Path, seed: int = 42, partition: str = "none") -> dict:
    cfg = small_config_dict(tmp_path, seed=seed, partition=partition)
    path = write_config(tmp_path, cfg)
    return load_config(path)
