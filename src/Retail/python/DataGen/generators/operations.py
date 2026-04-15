from __future__ import annotations

import numpy as np
import pandas as pd

from DataGen.rng import normalize_weights


def _promo_lookup(promotions: pd.DataFrame) -> dict[int, list[dict[str, object]]]:
    lookup: dict[int, list[dict[str, object]]] = {}
    for row in promotions.itertuples(index=False):
        lookup.setdefault(int(row.Product), []).append(
            {
                "PromotionId": int(row.PromotionId),
                "Store": None if pd.isna(row.Store) else int(row.Store),
                "StartDate": int(row.StartDate),
                "EndDate": int(row.EndDate),
                "DiscountPct": float(row.DiscountPct),
                "PromoPrice": float(row.PromoPrice),
            }
        )
    return lookup


def _basket_ids(count: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    basket_numbers = np.empty(count, dtype=int)
    line_numbers = np.empty(count, dtype=int)
    current_basket = 700000
    current_line = 1
    for index in range(count):
        if index == 0 or rng.random() < 0.64:
            current_basket += 1
            current_line = 1
        basket_numbers[index] = current_basket
        line_numbers[index] = current_line
        current_line += 1
    return basket_numbers, line_numbers


def generate_sales_transactions(
    config: dict,
    calendar: pd.DataFrame,
    stores: pd.DataFrame,
    products: pd.DataFrame,
    promotions: pd.DataFrame,
    customers: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    count = int(config["resolved_counts"]["sales_transactions"])
    store_ids = stores["StoreId"].to_numpy()
    product_ids = products["ProductId"].to_numpy()
    product_lookup = products.set_index("ProductId")
    store_lookup = stores.set_index("StoreId")
    customer_lookup = customers.set_index("CustomerId")
    promo_lookup = _promo_lookup(promotions)

    format_multiplier = {"FLAGSHIP": 1.45, "SUBURBAN": 1.05, "URBAN": 1.18, "OUTLET": 0.82}
    store_weights = normalize_weights([format_multiplier[str(value)] * (1.0 if bool(active) else 0.6) for value, active in zip(stores["StoreFormat"], stores["ActiveFlag"])])

    product_popularity = rng.pareto(2.1, size=len(product_ids)) + 1.0
    product_popularity *= np.where(products["Department"].isin(["GROCERY", "BEVERAGE"]), 1.25, 1.0)
    product_weights = normalize_weights(product_popularity)

    date_weight = np.where(calendar["IsWeekend"], 1.22, 1.0).astype(float)
    date_weight *= np.where(calendar["RetailEvent"] == "HOLIDAY_PEAK", 1.35, 1.0)
    date_ids = calendar["CalendarId"].to_numpy()
    date_weights = normalize_weights(date_weight)

    sales_cfg = config["behavior"]["sales"]
    channel_weights = sales_cfg["channel_weights"]
    channels = list(channel_weights.keys())
    channel_prob = normalize_weights([channel_weights[name] for name in channels])
    return_rate = float(sales_cfg["return_rate"])
    stockout_rate = float(sales_cfg["stockout_rate"])
    promo_attach_rate = float(sales_cfg["promo_attach_rate"])
    customer_ids = customers["CustomerId"].to_numpy()
    customer_weight = np.where(customers["ActiveFlag"], 1.0, 0.3).astype(float)
    customer_weight *= customers["Segment"].map({"BUDGET": 1.10, "MAINSTREAM": 1.00, "PREMIUM": 0.92, "OCCASIONAL": 0.58}).to_numpy(dtype=float)
    customer_weight = normalize_weights(customer_weight)
    basket_numbers, basket_line_numbers = _basket_ids(count, rng)

    dept_unit_mean = {
        "GROCERY": 2.6,
        "BEVERAGE": 2.4,
        "HOUSEHOLD": 1.5,
        "PERSONAL_CARE": 1.4,
        "ELECTRONICS": 1.05,
        "APPAREL": 1.2,
        "TOYS": 1.15,
    }

    payment_method_weights = {
        "INSTORE": (["CARD", "CASH", "MOBILE_WALLET", "GIFT_CARD"], [0.48, 0.24, 0.18, 0.10]),
        "CLICK_COLLECT": (["CARD", "MOBILE_WALLET", "GIFT_CARD"], [0.58, 0.28, 0.14]),
        "DELIVERY": (["CARD", "DIGITAL_WALLET", "BNPL"], [0.62, 0.20, 0.18]),
        "SHIP_FROM_STORE": (["CARD", "DIGITAL_WALLET", "BNPL"], [0.60, 0.18, 0.22]),
    }

    rows: list[dict[str, object]] = []
    basket_customer = 0
    basket_store = 0
    basket_date = 0
    basket_channel = ""
    basket_payment = ""
    for sales_transaction_id in range(1, count + 1):
        if basket_line_numbers[sales_transaction_id - 1] == 1:
            basket_customer = int(rng.choice(customer_ids, p=customer_weight))
            customer = customer_lookup.loc[basket_customer]
            basket_store = int(customer["HomeStore"]) if rng.random() < 0.68 else int(rng.choice(store_ids, p=store_weights))
            preferred_channel = str(customer["PreferredChannel"])
            blended = channel_prob.copy()
            blended[channels.index(preferred_channel)] *= 1.55
            basket_channel = str(rng.choice(channels, p=normalize_weights(blended)))
            basket_date = int(rng.choice(date_ids, p=date_weights))
            payment_options, payment_weights = payment_method_weights[basket_channel]
            loyalty = str(customer["LoyaltyTier"])
            adjusted_weights = np.array(payment_weights, dtype=float)
            if loyalty in {"PLUS", "VIP"} and "DIGITAL_WALLET" in payment_options:
                adjusted_weights[payment_options.index("DIGITAL_WALLET")] *= 1.35
            basket_payment = str(rng.choice(payment_options, p=normalize_weights(adjusted_weights)))

        store_id = basket_store
        product_id = int(rng.choice(product_ids, p=product_weights))
        transaction_date = basket_date
        product = product_lookup.loc[product_id]
        store = store_lookup.loc[store_id]
        department = str(product["Department"])
        channel = basket_channel
        fulfillment = {
            "INSTORE": "TAKEAWAY",
            "CLICK_COLLECT": "PICKUP",
            "DELIVERY": "HOME_DELIVERY",
            "SHIP_FROM_STORE": "SHIP_FROM_STORE",
        }[channel]

        active_promotions = []
        for promotion in promo_lookup.get(product_id, []):
            store_match = promotion["Store"] is None or int(promotion["Store"]) == store_id
            date_match = int(promotion["StartDate"]) <= transaction_date <= int(promotion["EndDate"])
            if store_match and date_match:
                active_promotions.append(promotion)

        applied_promotion = None
        if active_promotions and rng.random() < promo_attach_rate:
            applied_promotion = active_promotions[int(rng.integers(0, len(active_promotions)))]

        unit_mean = dept_unit_mean[department] * (1.15 if str(store["StoreFormat"]) == "FLAGSHIP" else 1.0)
        units = max(1, int(rng.poisson(unit_mean)))
        is_return = bool(rng.random() < return_rate)
        stockout_flag = bool((not is_return) and rng.random() < stockout_rate)

        gross_amount = float(np.round(float(product["BaseRegularPrice"]) * units, 2))
        discount_amount = 0.0
        promotion_id = pd.NA
        if applied_promotion is not None and not is_return:
            promotion_id = int(applied_promotion["PromotionId"])
            discount_amount = float(np.round(gross_amount * float(applied_promotion["DiscountPct"]), 2))

        net_amount = gross_amount - discount_amount
        cogs_amount = float(np.round(float(product["BaseUnitCost"]) * units, 2))
        signed_units = -units if is_return else units
        signed_gross = -gross_amount if is_return else gross_amount
        signed_discount = 0.0 if is_return else discount_amount
        signed_net = -net_amount if is_return else net_amount
        signed_cogs = -cogs_amount if is_return else cogs_amount

        rows.append(
            {
                "SalesTransactionId": sales_transaction_id,
                "TransactionNumber": f"TXN{sales_transaction_id:09d}",
                "BasketNumber": f"BSK{basket_numbers[sales_transaction_id - 1]:09d}",
                "TransactionDate": transaction_date,
                "Store": store_id,
                "Customer": basket_customer,
                "Product": product_id,
                "Channel": channel,
                "PaymentMethod": basket_payment,
                "Units": signed_units,
                "GrossSalesAmount": signed_gross,
                "DiscountAmount": signed_discount,
                "NetSalesAmount": signed_net,
                "CogsAmount": signed_cogs,
                "Promotion": promotion_id,
                "FulfillmentType": fulfillment,
                "ReturnFlag": is_return,
                "StockoutFlag": stockout_flag,
            }
        )

    return pd.DataFrame(rows)


def generate_inventory_snapshot(
    config: dict,
    calendar: pd.DataFrame,
    stores: pd.DataFrame,
    products: pd.DataFrame,
    supplier_products: pd.DataFrame,
    promotions: pd.DataFrame,
    purchase_orders: pd.DataFrame,
    stock_transfers: pd.DataFrame,
    sales_transactions: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    count = int(config["resolved_counts"]["inventory_snapshots"])
    product_lookup = products.set_index("ProductId")
    store_lookup = stores.set_index("StoreId")
    promo_lookup = _promo_lookup(promotions)

    positive_sales = sales_transactions.loc[~sales_transactions["ReturnFlag"]].copy()
    sales_demand = positive_sales.groupby(["Store", "Product"], observed=True)["Units"].sum().to_dict()
    pair_weights: dict[tuple[int, int], float] = {key: float(value) + 1.0 for key, value in sales_demand.items()}

    store_ids = stores["StoreId"].to_numpy()
    product_ids = products["ProductId"].to_numpy()
    while len(pair_weights) < max(120, count // 2):
        pair = (int(rng.choice(store_ids)), int(rng.choice(product_ids)))
        pair_weights.setdefault(pair, 1.0)

    pair_list = list(pair_weights.keys())
    pair_prob = normalize_weights([pair_weights[pair] for pair in pair_list])

    supplier_summary = supplier_products.groupby("Product", observed=True).agg(
        LeadTimeDays=("LeadTimeDays", "min"),
        MinOrderQty=("MinOrderQty", "min"),
        UnitCost=("UnitCost", "mean"),
    )
    po_product = purchase_orders.merge(
        supplier_products[["SupplierProductId", "Product"]],
        left_on="SupplierProduct",
        right_on="SupplierProductId",
        how="left",
    )
    po_product["RemainingQty"] = (po_product["OrderedQty"] - po_product["ReceivedQty"]).clip(lower=0)
    po_remaining = po_product.groupby(["Store", "Product"], observed=True)["RemainingQty"].sum().to_dict()
    transfer_in = stock_transfers.loc[stock_transfers["Status"].isin(["IN_TRANSIT", "DELAYED", "RECEIVED"])].groupby(
        ["ToStore", "Product"], observed=True
    )["Quantity"].sum().to_dict()
    transfer_out = stock_transfers.loc[stock_transfers["Status"].isin(["IN_TRANSIT", "DELAYED", "RECEIVED"])].groupby(
        ["FromStore", "Product"], observed=True
    )["Quantity"].sum().to_dict()

    date_ids = calendar["CalendarId"].to_numpy()
    recency = np.linspace(0.8, 1.35, num=len(date_ids))
    date_prob = normalize_weights(recency)
    low_stock_share = float(config["behavior"]["inventory"]["low_stock_share"])
    markdown_share = float(config["behavior"]["inventory"]["markdown_share"])

    used_keys: set[tuple[int, int, int]] = set()
    rows: list[dict[str, object]] = []
    snapshot_id = 1
    while len(rows) < count:
        store_id, product_id = pair_list[int(rng.choice(np.arange(len(pair_list)), p=pair_prob))]
        snapshot_date = int(rng.choice(date_ids, p=date_prob))
        unique_key = (snapshot_date, store_id, product_id)
        if unique_key in used_keys:
            continue
        used_keys.add(unique_key)

        product = product_lookup.loc[product_id]
        store = store_lookup.loc[store_id]
        supplier_row = supplier_summary.loc[product_id] if product_id in supplier_summary.index else None
        daily_units = float(sales_demand.get((store_id, product_id), 0.0)) / max(1, len(date_ids))
        lead_time = int(supplier_row["LeadTimeDays"]) if supplier_row is not None else int(rng.integers(4, 20))
        min_order_qty = int(supplier_row["MinOrderQty"]) if supplier_row is not None else int(rng.integers(12, 48))
        unit_cost = float(np.round(supplier_row["UnitCost"], 2)) if supplier_row is not None else float(product["BaseUnitCost"])

        safety_stock = max(4, int(np.round(daily_units * 10 + rng.integers(3, 18))))
        reorder_point = max(safety_stock + 2, int(np.round(daily_units * lead_time + safety_stock)))
        reorder_target = reorder_point + max(min_order_qty // 2, int(rng.integers(8, 32)))

        inbound_qty = int(po_remaining.get((store_id, product_id), 0))
        in_transit_qty = int(transfer_in.get((store_id, product_id), 0) * 0.35)
        outbound_pressure = int(transfer_out.get((store_id, product_id), 0) * 0.12)
        base_stock = reorder_target + int(rng.integers(-12, 26)) + int(daily_units * rng.integers(2, 8))
        on_hand_qty = max(0, base_stock + inbound_qty // 6 + in_transit_qty - outbound_pressure)
        if rng.random() < low_stock_share:
            on_hand_qty = max(0, int(rng.integers(0, max(reorder_point, 2))))

        reserved_qty = min(on_hand_qty, int(np.round(on_hand_qty * rng.uniform(0.02, 0.18))))
        available_qty = max(0, on_hand_qty - reserved_qty)
        on_order_qty = max(0, inbound_qty)
        regular_price = float(product["BaseRegularPrice"])

        markdown_price = pd.NA
        active_promo = [promo for promo in promo_lookup.get(product_id, []) if promo["StartDate"] <= snapshot_date <= promo["EndDate"] and (promo["Store"] is None or promo["Store"] == store_id)]
        if active_promo:
            markdown_price = float(active_promo[0]["PromoPrice"])
        elif rng.random() < markdown_share or str(store["StoreFormat"]) == "OUTLET":
            markdown_price = float(np.round(regular_price * rng.uniform(0.75, 0.92), 2))

        days_of_supply = float(np.round(available_qty / max(0.3, daily_units), 2))

        rows.append(
            {
                "InventorySnapshotId": snapshot_id,
                "SnapshotDate": snapshot_date,
                "Store": store_id,
                "Product": product_id,
                "OnHandQty": on_hand_qty,
                "ReservedQty": reserved_qty,
                "AvailableQty": available_qty,
                "InTransitQty": in_transit_qty,
                "OnOrderQty": on_order_qty,
                "SafetyStockQty": safety_stock,
                "ReorderPointQty": reorder_point,
                "ReorderTargetQty": reorder_target,
                "UnitCost": unit_cost,
                "RegularPrice": regular_price,
                "MarkdownPrice": markdown_price,
                "DaysOfSupply": days_of_supply,
            }
        )
        snapshot_id += 1

    return pd.DataFrame(rows)
