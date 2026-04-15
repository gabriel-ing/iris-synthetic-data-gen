from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from DataGen.config import load_config
from DataGen.edge_cases import apply_edge_cases
from DataGen.generators.accounts import generate_accounts
from DataGen.generators.cards import generate_cards
from DataGen.generators.customers import generate_customers
from DataGen.generators.disputes import generate_disputes
from DataGen.generators.merchants import generate_merchants
from DataGen.generators.transactions import generate_transactions
from DataGen.rng import make_rng
from DataGen.validate import validate_all
from DataGen.writer import prepare_output_dir, write_csv, write_transactions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic financial dataset generator")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--scale-factor", type=int, help="Multiply the configured base dataset size by this factor")
    return parser.parse_args()


def _summary(accounts: pd.DataFrame, customers: pd.DataFrame, cards: pd.DataFrame, merchants: pd.DataFrame, transactions: pd.DataFrame, disputes: pd.DataFrame) -> dict:
    decline_rate = float((transactions["Status"] == "DECLINED").mean())
    refund_rate = float((transactions["Status"].isin(["REFUNDED", "REVERSED"])).mean())
    dispute_rate = float(len(disputes) / max(1, len(transactions)))
    top_merchants = (
        transactions.groupby("Merchant")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .rename("TxnCount")
        .reset_index()
        .to_dict(orient="records")
    )
    auth = pd.to_datetime(transactions["AuthAt"], utc=True)
    return {
        "counts": {
            "accounts": len(accounts),
            "customers": len(customers),
            "cards": len(cards),
            "merchants": len(merchants),
            "transactions": len(transactions),
            "disputes": len(disputes),
        },
        "rates": {
            "decline_rate": round(decline_rate, 4),
            "refund_or_reversed_rate": round(refund_rate, 4),
            "dispute_rate": round(dispute_rate, 4),
        },
        "top_10_merchants": top_merchants,
        "transaction_time_range": {
            "min_auth_at": auth.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "max_auth_at": auth.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }


def main() -> None:
    args = parse_args()
    config = load_config(args.config, scale_factor_override=args.scale_factor)
    seed = int(config["seed"])

    out_dir = prepare_output_dir(config["output"]["path"], config["output"].get("overwrite", True))

    merchants = generate_merchants(config, make_rng(seed, "merchants"))
    customers = generate_customers(config, make_rng(seed, "customers"))
    accounts = generate_accounts(config, customers, make_rng(seed, "accounts"))
    cards = generate_cards(config, customers, accounts, make_rng(seed, "cards"))
    tx_frames = generate_transactions(config, customers, cards, merchants, make_rng(seed, "transactions"))
    transactions = pd.concat(tx_frames, ignore_index=True)

    customers, cards, transactions = apply_edge_cases(config, customers, cards, transactions, make_rng(seed, "edge_cases"))
    disputes = generate_disputes(config, customers, cards, merchants, transactions, make_rng(seed, "disputes"))

    write_csv(accounts, out_dir, "accounts")
    write_csv(customers, out_dir, "customers")
    write_csv(cards, out_dir, "cards")
    write_csv(merchants, out_dir, "merchants")

    partition_mode = config["output"].get("partition_transactions_by", "none")
    if partition_mode == "day":
        tx_by_day = [frame for _, frame in transactions.groupby(transactions["AuthAt"].str[:10], sort=True)]
        write_transactions(tx_by_day, out_dir, partition_mode)
    else:
        write_transactions([transactions], out_dir, "none")

    write_csv(disputes, out_dir, "disputes")

    validation = validate_all(config, accounts, customers, cards, merchants, transactions, disputes)
    summary = _summary(accounts, customers, cards, merchants, transactions, disputes)
    print("Validation checks passed:", len(validation.checks))
    if validation.warnings:
        print("Validation warnings:")
        for warning in validation.warnings:
            print(" -", warning)
    print("Run summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
