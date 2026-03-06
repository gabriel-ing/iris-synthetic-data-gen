from __future__ import annotations

import argparse
import math
from typing import Iterable

import pandas as pd

from DataGen.config import load_config
from DataGen.edge_cases import apply_edge_cases
from DataGen.generators.cards import generate_cards
from DataGen.generators.customers import generate_customers
from DataGen.generators.disputes import generate_disputes
from DataGen.generators.merchants import generate_merchants
from DataGen.generators.transactions import generate_transactions
from DataGen.rng import make_rng
from DataGen.validate import validate_all


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic data and insert directly into IRIS (no CSV files)."
    )
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--package", default="finance", help="IRIS SQL package/schema prefix")
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Delete existing rows before insert (child tables first)",
    )
    parser.add_argument(
        "--commit-every",
        type=int,
        default=20000,
        help="Issue SQL COMMIT every N inserted rows per table",
    )
    return parser.parse_args()


def _summary(
    customers: pd.DataFrame,
    cards: pd.DataFrame,
    merchants: pd.DataFrame,
    transactions: pd.DataFrame,
    disputes: pd.DataFrame,
) -> dict:
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


def _normalize_value(value):
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if value is pd.NA:
        return None
    # Convert numpy scalar types to native Python values.
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    return value


def _iter_rows(df: pd.DataFrame, columns: list[str]) -> Iterable[tuple]:
    for row in df[columns].itertuples(index=False, name=None):
        yield tuple(_normalize_value(v) for v in row)


def _exec_sql(iris, sql: str) -> None:
    stmt = iris.sql.prepare(sql)
    stmt.execute()


def _insert_df(iris, table_name: str, columns: list[str], df: pd.DataFrame, commit_every: int) -> int:
    placeholders = ", ".join(["?"] * len(columns))
    col_sql = ", ".join(columns)
    sql = f"INSERT INTO {table_name} ({col_sql}) VALUES ({placeholders})"
    stmt = iris.sql.prepare(sql)

    inserted = 0
    for row in _iter_rows(df, columns):
        stmt.execute(*row)
        inserted += 1
        if commit_every > 0 and inserted % commit_every == 0:
            _exec_sql(iris, "COMMIT")

    _exec_sql(iris, "COMMIT")
    return inserted


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    seed = int(config["seed"])

    merchants = generate_merchants(config, make_rng(seed, "merchants"))
    customers = generate_customers(config, make_rng(seed, "customers"))
    cards = generate_cards(config, customers, make_rng(seed, "cards"))
    tx_frames = generate_transactions(
        config,
        customers,
        cards,
        merchants,
        make_rng(seed, "transactions"),
    )
    transactions = pd.concat(tx_frames, ignore_index=True)

    customers, cards, transactions = apply_edge_cases(
        config,
        customers,
        cards,
        transactions,
        make_rng(seed, "edge_cases"),
    )
    disputes = generate_disputes(
        config,
        customers,
        cards,
        merchants,
        transactions,
        make_rng(seed, "disputes"),
    )

    validation = validate_all(config, customers, cards, merchants, transactions, disputes)
    print("Validation checks passed:", len(validation.checks))
    if validation.warnings:
        print("Validation warnings:")
        for warning in validation.warnings:
            print(" -", warning)

    try:
        import iris
    except ImportError as exc:
        raise ImportError(
            "iris module not found. Run this in IRIS Embedded Python or install intersystems-irispython."
        ) from exc

    pkg = args.package
    table_customers = f"{pkg}.Customers"
    table_merchants = f"{pkg}.Merchants"
    table_cards = f"{pkg}.Cards"
    table_transactions = f"{pkg}.Transactions"
    table_disputes = f"{pkg}.Disputes"

    if args.clear_existing:
        for table in [table_disputes, table_transactions, table_cards, table_merchants, table_customers]:
            _exec_sql(iris, f"DELETE FROM {table}")
            print(f"Cleared {table}")
        _exec_sql(iris, "COMMIT")

    customers_cols = [
        "CustomerId",
        "CreatedAt",
        "Status",
        "Segment",
        "RiskScore",
        "State",
        "SegmentTxnMultiplier",
        "SegmentAmountMultiplier",
        "SegmentEcomMultiplier",
        "SegmentDeclineMultiplier",
        "SegmentDisputeMultiplier",
    ]
    merchants_cols = [
        "MerchantId",
        "MerchantName",
        "Category",
        "RiskTier",
        "PopularityWeight",
        "Country",
    ]
    cards_cols = [
        "CardId",
        "Customer",
        "CardType",
        "Status",
        "OpenedAt",
        "ClosedAt",
        "CardToken",
        "CreditLimit",
    ]
    transactions_cols = [
        "TransactionId",
        "Card",
        "Merchant",
        "AuthAt",
        "PostedAt",
        "Amount",
        "Currency",
        "Channel",
        "EntryMode",
        "CardPresent",
        "Status",
        "DeclineReason",
        "IsFraud",
    ]
    disputes_cols = [
        "DisputeId",
        "Transactions",
        "OpenedAt",
        "ResolvedAt",
        "ReasonCode",
        "State",
        "Outcome",
        "DisputedAmount",
    ]

    inserted_customers = _insert_df(iris, table_customers, customers_cols, customers, args.commit_every)
    print(f"Inserted {inserted_customers:,} rows into {table_customers}")
    inserted_merchants = _insert_df(iris, table_merchants, merchants_cols, merchants, args.commit_every)
    print(f"Inserted {inserted_merchants:,} rows into {table_merchants}")
    inserted_cards = _insert_df(iris, table_cards, cards_cols, cards, args.commit_every)
    print(f"Inserted {inserted_cards:,} rows into {table_cards}")
    inserted_transactions = _insert_df(
        iris,
        table_transactions,
        transactions_cols,
        transactions,
        args.commit_every,
    )
    print(f"Inserted {inserted_transactions:,} rows into {table_transactions}")
    inserted_disputes = _insert_df(iris, table_disputes, disputes_cols, disputes, args.commit_every)
    print(f"Inserted {inserted_disputes:,} rows into {table_disputes}")

    summary = _summary(customers, cards, merchants, transactions, disputes)
    print("Run summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
