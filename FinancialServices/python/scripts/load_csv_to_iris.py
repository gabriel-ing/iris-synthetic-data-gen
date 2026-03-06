from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Callable


# ============================================================
# DDL SECTION (easy to copy into other contexts)
# ============================================================


def build_ddl(package: str) -> dict[str, str]:
    return {
        "Customers": f"""
CREATE TABLE {package}.Customers (
    CustomerId INTEGER NOT NULL,
    CreatedAt VARCHAR(35),
    Status VARCHAR(20),
    Segment VARCHAR(20),
    RiskScore INTEGER,
    State VARCHAR(20),
    SegmentTxnMultiplier DOUBLE,
    SegmentAmountMultiplier DOUBLE,
    SegmentEcomMultiplier DOUBLE,
    SegmentDeclineMultiplier DOUBLE,
    SegmentDisputeMultiplier DOUBLE,
    PRIMARY KEY (CustomerId)
)
""".strip(),
        "Cards": f"""
CREATE TABLE {package}.Cards (
    CardId INTEGER NOT NULL,
    Customer INTEGER,
    CardType VARCHAR(20),
    Status VARCHAR(20),
    OpenedAt VARCHAR(35),
    ClosedAt VARCHAR(35),
    CardToken VARCHAR(80),
    CreditLimit INTEGER,
    PRIMARY KEY (CardId)
)
""".strip(),
        "Merchants": f"""
CREATE TABLE {package}.Merchants (
    MerchantId INTEGER NOT NULL,
    MerchantName VARCHAR(200),
    Category VARCHAR(40),
    RiskTier VARCHAR(20),
    PopularityWeight DOUBLE,
    Country VARCHAR(10),
    PRIMARY KEY (MerchantId)
)
""".strip(),
        "Transactions": f"""
CREATE TABLE {package}.Transactions (
    TransactionId BIGINT NOT NULL,
    Card INTEGER,
    Merchant INTEGER,
    AuthAt VARCHAR(35),
    PostedAt VARCHAR(35),
    Amount NUMERIC(18,2),
    Currency VARCHAR(10),
    Channel VARCHAR(20),
    EntryMode VARCHAR(20),
    CardPresent INTEGER,
    Status VARCHAR(20),
    DeclineReason VARCHAR(50),
    IsFraud INTEGER,
    PRIMARY KEY (TransactionId)
)
""".strip(),
        "Disputes": f"""
CREATE TABLE {package}.Disputes (
    DisputeId BIGINT NOT NULL,
    Transactions BIGINT,
    OpenedAt VARCHAR(35),
    ResolvedAt VARCHAR(35),
    ReasonCode VARCHAR(50),
    State VARCHAR(30),
    Outcome VARCHAR(40),
    DisputedAmount NUMERIC(18,2),
    PRIMARY KEY (DisputeId)
)
""".strip(),
    }


def build_drop_statements(package: str) -> dict[str, str]:
    return {
        "Disputes": f"DROP TABLE {package}.Disputes",
        "Transactions": f"DROP TABLE {package}.Transactions",
        "Cards": f"DROP TABLE {package}.Cards",
        "Merchants": f"DROP TABLE {package}.Merchants",
        "Customers": f"DROP TABLE {package}.Customers",
    }


# ============================================================
# Insert mappings and converters
# ============================================================


def _to_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    if value in {"True", "true"}:
        return 1
    if value in {"False", "false"}:
        return 0
    return int(value)


def _to_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _to_text(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    return value


TABLE_CONFIG = {
    "customers": {
        "table": "Customers",
        "columns": [
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
        ],
        "converters": [_to_int, _to_text, _to_text, _to_text, _to_int, _to_text, _to_float, _to_float, _to_float, _to_float, _to_float],
    },
    "cards": {
        "table": "Cards",
        "columns": ["CardId", "Customer", "CardType", "Status", "OpenedAt", "ClosedAt", "CardToken", "CreditLimit"],
        "converters": [_to_int, _to_int, _to_text, _to_text, _to_text, _to_text, _to_text, _to_int],
    },
    "merchants": {
        "table": "Merchants",
        "columns": ["MerchantId", "MerchantName", "Category", "RiskTier", "PopularityWeight", "Country"],
        "converters": [_to_int, _to_text, _to_text, _to_text, _to_float, _to_text],
    },
    "transactions": {
        "table": "Transactions",
        "columns": [
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
        ],
        "converters": [_to_int, _to_int, _to_int, _to_text, _to_text, _to_float, _to_text, _to_text, _to_text, _to_int, _to_text, _to_text, _to_int],
    },
    "disputes": {
        "table": "Disputes",
        "columns": ["DisputeId", "Transactions", "OpenedAt", "ResolvedAt", "ReasonCode", "State", "Outcome", "DisputedAmount"],
        "converters": [_to_int, _to_int, _to_text, _to_text, _to_text, _to_text, _to_text, _to_float],
    },
}


def _safe_identifier(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", value):
        raise ValueError("package must match [A-Za-z][A-Za-z0-9_]*")
    return value


def _transaction_csv_paths(data_dir: Path) -> list[Path]:
    single = data_dir / "transactions.csv"
    if single.exists():
        return [single]

    part_dir = data_dir / "transactions"
    if part_dir.exists():
        return sorted(part_dir.glob("transactions_*.csv"))

    return []


def _load_rows(
    cursor,
    full_table_name: str,
    csv_paths: list[Path],
    columns: list[str],
    converters: list[Callable[[str | None], object]],
    chunk_size: int,
) -> int:
    placeholders = ",".join(["?"] * len(columns))
    col_sql = ", ".join(columns)
    insert_sql = f"INSERT INTO {full_table_name} ({col_sql}) VALUES ({placeholders})"

    inserted = 0
    buffer: list[list[object]] = []
    for csv_path in csv_paths:
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                converted = [conv(row.get(col)) for col, conv in zip(columns, converters)]
                buffer.append(converted)
                if len(buffer) >= chunk_size:
                    cursor.executemany(insert_sql, buffer)
                    inserted += len(buffer)
                    buffer.clear()

    if buffer:
        cursor.executemany(insert_sql, buffer)
        inserted += len(buffer)
    return inserted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load generated CSV data into InterSystems IRIS via DB-API")
    parser.add_argument("--data-dir", default="out", help="Directory containing generated CSV files")
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--port", type=int, default=1972)
    parser.add_argument("--namespace", default="USER")
    parser.add_argument("--username", default="_system")
    parser.add_argument("--password", default="SYS")
    parser.add_argument("--package", default="finance", help="SQL package/schema prefix, e.g. finance")
    parser.add_argument("--chunk-size", type=int, default=5000)
    parser.add_argument("--drop-existing", action="store_true", help="Drop existing tables first")
    parser.add_argument("--create-only", action="store_true", help="Create tables only, skip data load")
    parser.add_argument("--load-only", action="store_true", help="Load data only, skip table creation")
    parser.add_argument("--print-ddl", action="store_true", help="Print DDL and exit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    package = _safe_identifier(args.package)
    ddl = build_ddl(package)
    drop_sql = build_drop_statements(package)

    if args.print_ddl:
        for name, sql in ddl.items():
            print(f"\n-- {name}\n{sql};")
        return

    if args.create_only and args.load_only:
        raise ValueError("--create-only and --load-only cannot be used together")

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    try:
        import iris
    except ImportError as exc:
        raise ImportError(
            "Missing dependency 'intersystems-irispython'. Install with: pip install intersystems-irispython"
        ) from exc
    print(f"Connecting to IRIS at {args.server}:{args.port}, namespace={args.namespace}, user={args.username}")
    connection = iris.connect(args.server, int(args.port), args.namespace, args.username, args.password)
    print(connection)
    cursor = connection.cursor()
    try:
        if args.drop_existing and not args.load_only:
            for table_name in ["Disputes", "Transactions", "Cards", "Merchants", "Customers"]:
                sql = drop_sql[table_name]
                try:
                    cursor.execute(sql)
                    print(f"Dropped {package}.{table_name}")
                except Exception:
                    pass

        if not args.load_only:
            for table_name in ["Customers", "Cards", "Merchants", "Transactions", "Disputes"]:
                sql = ddl[table_name]
                try:
                    cursor.execute(sql)
                    print(f"Created {package}.{table_name}")
                except Exception as exc:
                    if "already exists" in str(exc).lower():
                        print(f"Exists {package}.{table_name}, continuing")
                    else:
                        raise

        if not args.create_only:
            table_load_order = ["customers", "cards", "merchants", "transactions", "disputes"]
            for key in table_load_order:
                conf = TABLE_CONFIG[key]
                table = conf["table"]
                if key == "transactions":
                    paths = _transaction_csv_paths(data_dir)
                    if not paths:
                        raise FileNotFoundError(
                            f"Could not find transactions.csv or partitioned transactions files under {data_dir}"
                        )
                else:
                    path = data_dir / f"{key}.csv"
                    if not path.exists():
                        raise FileNotFoundError(f"Missing CSV: {path}")
                    paths = [path]

                count = _load_rows(
                    cursor=cursor,
                    full_table_name=f"{package}.{table}",
                    csv_paths=paths,
                    columns=conf["columns"],
                    converters=conf["converters"],
                    chunk_size=args.chunk_size,
                )
                print(f"Loaded {count:,} rows into {package}.{table}")

        connection.commit()
        print("Load completed successfully")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
