from __future__ import annotations

import numpy as np
import pandas as pd

from DataGen.generators.helpers import random_codes, weighted_choice
from DataGen.rng import normalize_weights


def generate_supplier_product(config: dict, products: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    target = int(config["resolved_counts"]["supplier_products"])
    product_ids = products["ProductId"].to_numpy()
    supplier_pool_size = max(16, min(72, target // 8))

    supplier_country = rng.choice(["US", "MX", "CA", "VN", "CN"], size=supplier_pool_size, p=[0.55, 0.14, 0.12, 0.10, 0.09])
    supplier_tier = rng.choice([1, 2, 3], size=supplier_pool_size, p=[0.32, 0.48, 0.20])
    supplier_risk = np.clip(rng.normal(38, 17, size=supplier_pool_size), 3, 97).astype(int)
    supplier_codes = random_codes("SUP", supplier_pool_size)
    supplier_names = [f"Supplier {idx:04d}" for idx in range(1, supplier_pool_size + 1)]

    pairs: set[tuple[int, int]] = set()
    for product_id in product_ids:
        pairs.add((int(product_id), int(rng.integers(1, supplier_pool_size + 1))))

    while len(pairs) < target:
        pairs.add((int(rng.choice(product_ids)), int(rng.integers(1, supplier_pool_size + 1))))

    product_lookup = products.set_index("ProductId")
    rows: list[dict[str, object]] = []
    preferred_share = float(config["behavior"]["supply"]["preferred_supplier_share"])
    currency = str(config["currency"])

    for supplier_product_id, (product_id, supplier_idx) in enumerate(sorted(pairs), start=1):
        product = product_lookup.loc[product_id]
        base_cost = float(product["BaseUnitCost"])
        lead_time = int(rng.integers(4, 28))
        multiple = int(rng.choice([1, 2, 4, 6, 12], p=normalize_weights([0.18, 0.26, 0.24, 0.16, 0.16])))
        min_order = int(multiple * rng.choice([6, 12, 18, 24], p=normalize_weights([0.28, 0.34, 0.22, 0.16])))
        cost = max(0.5, float(np.round(base_cost * rng.uniform(0.88, 1.08), 2)))
        rows.append(
            {
                "SupplierProductId": supplier_product_id,
                "Product": product_id,
                "SupplierCode": supplier_codes[supplier_idx - 1],
                "SupplierName": supplier_names[supplier_idx - 1],
                "SupplierCountry": supplier_country[supplier_idx - 1],
                "SupplierTier": int(supplier_tier[supplier_idx - 1]),
                "PreferredSupplierFlag": bool(rng.random() < preferred_share),
                "LeadTimeDays": lead_time,
                "MinOrderQty": min_order,
                "OrderMultipleQty": multiple,
                "UnitCost": cost,
                "Currency": currency,
                "RiskScore": int(supplier_risk[supplier_idx - 1]),
                "ShipMode": str(rng.choice(["TRUCK", "AIR", "PARCEL"], p=[0.66, 0.09, 0.25])),
            }
        )

    out = pd.DataFrame(rows).sort_values("SupplierProductId", ignore_index=True)
    first_idx = out.groupby("Product").head(1).index
    out["PreferredSupplierFlag"] = False
    out.loc[first_idx, "PreferredSupplierFlag"] = True
    return out


def generate_promotions(
    config: dict,
    calendar: pd.DataFrame,
    stores: pd.DataFrame,
    products: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    count = int(config["resolved_counts"]["promotions"])
    store_ids = stores["StoreId"].to_numpy()
    product_ids = products["ProductId"].to_numpy()
    price_lookup = products.set_index("ProductId")["BaseRegularPrice"]
    type_weights = config["behavior"]["promotions"]["type_weights"]
    promo_types = list(type_weights.keys())
    chosen_types = weighted_choice(rng, promo_types, type_weights, count)
    chainwide_share = float(config["behavior"]["promotions"]["chainwide_share"])
    max_day = int(calendar["CalendarId"].max())

    rows: list[dict[str, object]] = []
    for promotion_id in range(1, count + 1):
        product_id = int(rng.choice(product_ids))
        start_date = int(rng.integers(1, max(2, max_day - 10)))
        duration = int(rng.integers(5, 19))
        end_date = min(max_day, start_date + duration)
        promo_type = str(chosen_types[promotion_id - 1])
        discount_pct = {
            "PCT_OFF": float(np.round(rng.uniform(0.08, 0.22), 4)),
            "MULTIBUY": float(np.round(rng.uniform(0.10, 0.18), 4)),
            "CLEARANCE": float(np.round(rng.uniform(0.22, 0.42), 4)),
            "DIGITAL_COUPON": float(np.round(rng.uniform(0.05, 0.16), 4)),
        }[promo_type]
        base_price = float(price_lookup.loc[product_id])
        promo_price = max(0.49, float(np.round(base_price * (1.0 - discount_pct), 2)))
        rows.append(
            {
                "PromotionId": promotion_id,
                "PromotionCode": f"PROMO{promotion_id:05d}",
                "Product": product_id,
                "Store": pd.NA if rng.random() < chainwide_share else int(rng.choice(store_ids)),
                "StartDate": start_date,
                "EndDate": end_date,
                "PromoType": promo_type,
                "DiscountPct": discount_pct,
                "PromoPrice": promo_price,
                "ExpectedLiftPct": float(np.round(rng.uniform(0.05, 0.45), 4)),
                "FundingSource": str(rng.choice(["VENDOR", "RETAILER", "SHARED"], p=[0.25, 0.50, 0.25])),
            }
        )

    return pd.DataFrame(rows)


def generate_purchase_orders(
    config: dict,
    calendar: pd.DataFrame,
    stores: pd.DataFrame,
    supplier_products: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    count = int(config["resolved_counts"]["purchase_orders"])
    store_ids = stores.loc[stores["ActiveFlag"], "StoreId"].to_numpy()
    if len(store_ids) == 0:
        store_ids = stores["StoreId"].to_numpy()

    supplier_product_ids = supplier_products["SupplierProductId"].to_numpy()
    preferred_weight = np.where(supplier_products["PreferredSupplierFlag"], 2.4, 1.0)
    preferred_weight = preferred_weight / preferred_weight.sum()
    supplier_lookup = supplier_products.set_index("SupplierProductId")
    max_day = int(calendar["CalendarId"].max())
    late_rate = float(config["behavior"]["supply"]["late_po_rate"])

    rows: list[dict[str, object]] = []
    for purchase_order_id in range(1, count + 1):
        supplier_product_id = int(rng.choice(supplier_product_ids, p=preferred_weight))
        supplier_row = supplier_lookup.loc[supplier_product_id]
        order_date = int(rng.integers(1, max_day + 1))
        lead_time = int(supplier_row["LeadTimeDays"])
        expected_receipt = min(max_day, order_date + lead_time)
        ordered_qty = int(supplier_row["OrderMultipleQty"] * rng.integers(4, 18))
        ordered_qty = max(int(supplier_row["MinOrderQty"]), ordered_qty)
        draw = float(rng.random())
        if draw < 0.52:
            status = "RECEIVED"
            actual_receipt = max(order_date, min(max_day, expected_receipt + int(rng.integers(-1, 3))))
            received_qty = ordered_qty
        elif draw < 0.70:
            status = "PARTIAL"
            actual_receipt = max(order_date, min(max_day, expected_receipt + int(rng.integers(0, 4))))
            received_qty = int(np.round(ordered_qty * rng.uniform(0.45, 0.82)))
        elif draw < 0.70 + late_rate:
            status = "LATE"
            late_receipt = expected_receipt + int(rng.integers(2, 12))
            actual_receipt = max(order_date, late_receipt) if late_receipt <= max_day else np.nan
            received_qty = ordered_qty if not pd.isna(actual_receipt) else 0
        elif draw < 0.94:
            status = "OPEN"
            actual_receipt = np.nan
            received_qty = 0
        else:
            status = "CANCELLED"
            actual_receipt = np.nan
            received_qty = 0

        rows.append(
            {
                "PurchaseOrderId": purchase_order_id,
                "PoNumber": f"PO{purchase_order_id:07d}",
                "Store": int(rng.choice(store_ids)),
                "SupplierProduct": supplier_product_id,
                "OrderDate": order_date,
                "ExpectedReceiptDate": expected_receipt,
                "ActualReceiptDate": actual_receipt,
                "OrderedQty": ordered_qty,
                "ReceivedQty": received_qty,
                "UnitCost": float(supplier_row["UnitCost"]),
                "Status": status,
                "UrgentFlag": bool(rng.random() < 0.11),
            }
        )

    return pd.DataFrame(rows)


def generate_stock_transfers(
    config: dict,
    calendar: pd.DataFrame,
    stores: pd.DataFrame,
    products: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    count = int(config["resolved_counts"]["stock_transfers"])
    store_rows = stores.set_index("StoreId")
    store_ids = stores["StoreId"].to_numpy()
    product_ids = products["ProductId"].to_numpy()
    max_day = int(calendar["CalendarId"].max())
    delay_rate = float(config["behavior"]["supply"]["transfer_delay_rate"])

    rows: list[dict[str, object]] = []
    for transfer_id in range(1, count + 1):
        from_store = int(rng.choice(store_ids))
        from_region = str(store_rows.loc[from_store, "Region"])
        same_region = stores.loc[stores["Region"] == from_region, "StoreId"].to_numpy()
        candidate_to = same_region if len(same_region) > 1 and rng.random() < 0.72 else store_ids
        candidate_to = candidate_to[candidate_to != from_store]
        to_store = int(rng.choice(candidate_to)) if len(candidate_to) else int(rng.choice(store_ids[store_ids != from_store]))
        request_date = int(rng.integers(1, max_day + 1))
        ship_date = min(max_day, request_date + int(rng.integers(0, 4)))
        quantity = int(rng.integers(6, 90))
        draw = float(rng.random())
        if draw < 0.66:
            status = "RECEIVED"
            receipt_date = min(max_day, ship_date + int(rng.integers(1, 5)))
        elif draw < 0.66 + delay_rate:
            status = "DELAYED"
            delayed_date = ship_date + int(rng.integers(5, 12))
            receipt_date = delayed_date if delayed_date <= max_day else np.nan
        elif draw < 0.94:
            status = "IN_TRANSIT"
            receipt_date = np.nan
        else:
            status = "CANCELLED"
            receipt_date = np.nan

        rows.append(
            {
                "StockTransferId": transfer_id,
                "TransferNumber": f"TR{transfer_id:07d}",
                "Product": int(rng.choice(product_ids)),
                "FromStore": from_store,
                "ToStore": to_store,
                "RequestDate": request_date,
                "ShipDate": ship_date,
                "ReceiptDate": receipt_date,
                "Quantity": quantity,
                "Status": status,
                "ReasonCode": str(rng.choice(["REBALANCE", "PROMO_SUPPORT", "STOCKOUT_ASSIST"], p=[0.54, 0.22, 0.24])),
            }
        )

    return pd.DataFrame(rows)
