from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ValidationResult:
    ok: bool
    checks: list[str]
    warnings: list[str]


def _assert(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise ValueError(message)
    checks.append(message)


def validate_all(config: dict, customers: pd.DataFrame, cards: pd.DataFrame, merchants: pd.DataFrame, transactions: pd.DataFrame, disputes: pd.DataFrame) -> ValidationResult:
    checks: list[str] = []
    warnings: list[str] = []

    # FK checks
    _assert(cards["Customer"].isin(customers["CustomerId"]).all(), "FK cards.customer valid", checks)
    _assert(transactions["Card"].isin(cards["CardId"]).all(), "FK transactions.card valid", checks)
    _assert(transactions["Merchant"].isin(merchants["MerchantId"]).all(), "FK transactions.merchant valid", checks)
    _assert(disputes["Transactions"].isin(transactions["TransactionId"]).all(), "FK disputes.transactions valid", checks)
    _assert(disputes["Transactions"].is_unique, "One dispute per transaction", checks)

    # Temporal checks
    card_times = cards[["CardId", "OpenedAt", "ClosedAt"]].copy()
    card_times["OpenedAt"] = pd.to_datetime(card_times["OpenedAt"], utc=True)
    card_times["ClosedAt"] = pd.to_datetime(card_times["ClosedAt"], utc=True, errors="coerce")

    tx = transactions.merge(card_times, left_on="Card", right_on="CardId", how="left")
    tx["AuthAt"] = pd.to_datetime(tx["AuthAt"], utc=True)
    tx["PostedAt"] = pd.to_datetime(tx["PostedAt"], utc=True)
    _assert((tx["AuthAt"] >= tx["OpenedAt"]).all(), "Transactions auth >= card opened", checks)
    closed_mask = tx["ClosedAt"].notna()
    _assert((tx.loc[closed_mask, "AuthAt"] <= tx.loc[closed_mask, "ClosedAt"]).all(), "Transactions auth <= card closed (if closed)", checks)
    _assert((tx["PostedAt"] >= tx["AuthAt"]).all(), "PostedAt >= AuthAt", checks)

    disp = disputes.merge(transactions[["TransactionId", "PostedAt"]], left_on="Transactions", right_on="TransactionId", how="left")
    disp["OpenedAt"] = pd.to_datetime(disp["OpenedAt"], utc=True)
    disp["ResolvedAt"] = pd.to_datetime(disp["ResolvedAt"], utc=True, errors="coerce")
    disp["PostedAt"] = pd.to_datetime(disp["PostedAt"], utc=True)
    _assert((disp["OpenedAt"] > disp["PostedAt"]).all(), "Dispute opened after posted", checks)
    resolved_mask = disp["ResolvedAt"].notna()
    _assert((disp.loc[resolved_mask, "ResolvedAt"] >= disp.loc[resolved_mask, "OpenedAt"]).all(), "Dispute resolved >= opened", checks)

    # Count checks
    resolved = config["resolved_counts"]
    _assert(len(customers) == int(resolved["customers"]), "Customer count matches config", checks)
    _assert(len(cards) == int(resolved["cards"]), "Card count matches config", checks)
    _assert(len(merchants) == int(resolved["merchants"]), "Merchant count matches config", checks)
    _assert(len(disputes) == int(resolved["disputes"]), "Dispute count matches config", checks)
    base_tx_count = int(resolved["transactions"])
    if len(transactions) < base_tx_count:
        raise ValueError("Transaction count lower than configured")
    checks.append("Transaction count is at least configured count")

    # Realism checks (soft)
    merchant_tx_counts = transactions.groupby("Merchant").size()
    if merchant_tx_counts.quantile(0.95) <= merchant_tx_counts.median():
        warnings.append("Merchant skew weaker than expected")

    tx_for_rate = transactions.merge(cards[["CardId", "Customer"]], left_on="Card", right_on="CardId", how="left").merge(customers[["CustomerId", "Segment"]], left_on="Customer", right_on="CustomerId", how="left")
    highrisk_decline = (tx_for_rate.loc[tx_for_rate["Segment"] == "HIGHRISK", "Status"] == "DECLINED").mean()
    mass_decline = (tx_for_rate.loc[tx_for_rate["Segment"] == "MASS", "Status"] == "DECLINED").mean()
    if pd.notna(highrisk_decline) and pd.notna(mass_decline) and highrisk_decline <= mass_decline:
        warnings.append("HIGHRISK decline rate not above MASS")

    ecom_dispute_rate = (disputes["Transactions"].isin(transactions.loc[transactions["Channel"] == "ECOM", "TransactionId"])).mean()
    if ecom_dispute_rate < 0.5:
        warnings.append("ECOM dispute share lower than expected")

    return ValidationResult(ok=True, checks=checks, warnings=warnings)
