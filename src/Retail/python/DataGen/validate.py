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
        raise AssertionError(message)
    checks.append(message)


def validate_all(
    config: dict,
    calendar: pd.DataFrame,
    roles: pd.DataFrame,
    customers: pd.DataFrame,
    users: pd.DataFrame,
    user_store_access: pd.DataFrame,
    stores: pd.DataFrame,
    products: pd.DataFrame,
    supplier_products: pd.DataFrame,
    promotions: pd.DataFrame,
    purchase_orders: pd.DataFrame,
    stock_transfers: pd.DataFrame,
    sales_transactions: pd.DataFrame,
    inventory_snapshot: pd.DataFrame,
) -> ValidationResult:
    checks: list[str] = []
    warnings: list[str] = []
    counts = config["resolved_counts"]

    _assert(len(calendar) == counts["days"], "calendar row count matches configured days", checks)
    _assert(len(roles) == counts["roles"], "role row count matches fixed role set", checks)
    _assert(len(customers) == counts["customers"], "customer row count matches configuration", checks)
    _assert(len(users) == counts["users"], "user row count matches configuration", checks)
    _assert(len(stores) == counts["stores"], "store row count matches configuration", checks)
    _assert(len(products) == counts["products"], "product row count matches configuration", checks)
    _assert(len(supplier_products) == counts["supplier_products"], "supplier_product row count matches configuration", checks)
    _assert(len(promotions) == counts["promotions"], "promotion row count matches configuration", checks)
    _assert(len(purchase_orders) == counts["purchase_orders"], "purchase_order row count matches configuration", checks)
    _assert(len(stock_transfers) == counts["stock_transfers"], "stock_transfer row count matches configuration", checks)
    _assert(len(sales_transactions) == counts["sales_transactions"], "sales_transaction row count matches configuration", checks)
    _assert(len(inventory_snapshot) == counts["inventory_snapshots"], "inventory_snapshot row count matches configuration", checks)

    calendar_ids = set(calendar["CalendarId"].tolist())
    role_ids = set(roles["RoleId"].tolist())
    customer_ids = set(customers["CustomerId"].tolist())
    user_ids = set(users["UserId"].tolist())
    store_ids = set(stores["StoreId"].tolist())
    product_ids = set(products["ProductId"].tolist())
    supplier_product_ids = set(supplier_products["SupplierProductId"].tolist())
    promotion_ids = set(promotions["PromotionId"].tolist())

    _assert(set(customers["HomeStore"]).issubset(store_ids), "customers reference valid home stores", checks)
    _assert(set(users["RoleRef"]).issubset(role_ids), "users reference valid roles", checks)
    _assert(set(users["PrimaryStore"]).issubset(store_ids), "users reference valid primary stores", checks)
    _assert(set(user_store_access["UserRef"]).issubset(user_ids), "user_store_access references valid users", checks)
    _assert(set(user_store_access["Store"]).issubset(store_ids), "user_store_access references valid stores", checks)
    _assert(set(supplier_products["Product"]).issubset(product_ids), "supplier_product references valid products", checks)

    _assert(promotions["Product"].isin(products["ProductId"]).all(), "promotions reference valid products", checks)
    promo_store = promotions["Store"]
    _assert(promo_store[promo_store.notna()].isin(stores["StoreId"]).all(), "promotions reference valid stores when store scoped", checks)
    _assert((promotions["StartDate"] <= promotions["EndDate"]).all(), "promotions have non-decreasing date windows", checks)
    _assert(promotions["StartDate"].isin(calendar["CalendarId"]).all(), "promotion start dates reference calendar rows", checks)
    _assert(promotions["EndDate"].isin(calendar["CalendarId"]).all(), "promotion end dates reference calendar rows", checks)

    _assert(purchase_orders["Store"].isin(stores["StoreId"]).all(), "purchase orders reference valid stores", checks)
    _assert(purchase_orders["SupplierProduct"].isin(supplier_products["SupplierProductId"]).all(), "purchase orders reference valid supplier_product rows", checks)
    _assert(purchase_orders["OrderDate"].isin(calendar["CalendarId"]).all(), "purchase order dates reference calendar rows", checks)
    _assert(purchase_orders["ExpectedReceiptDate"].isin(calendar["CalendarId"]).all(), "expected receipt dates reference calendar rows", checks)
    _assert((purchase_orders["ExpectedReceiptDate"] >= purchase_orders["OrderDate"]).all(), "purchase orders do not expect receipt before order date", checks)
    actual_receipt = purchase_orders["ActualReceiptDate"]
    _assert(actual_receipt[actual_receipt.notna()].isin(calendar["CalendarId"]).all(), "actual receipt dates reference calendar rows when present", checks)
    _assert((actual_receipt.fillna(purchase_orders["OrderDate"]) >= purchase_orders["OrderDate"]).all(), "actual receipt dates are not before order dates", checks)

    _assert(stock_transfers["Product"].isin(products["ProductId"]).all(), "stock transfers reference valid products", checks)
    _assert(stock_transfers["FromStore"].isin(stores["StoreId"]).all(), "stock transfers reference valid source stores", checks)
    _assert(stock_transfers["ToStore"].isin(stores["StoreId"]).all(), "stock transfers reference valid destination stores", checks)
    _assert((stock_transfers["FromStore"] != stock_transfers["ToStore"]).all(), "stock transfers keep source and destination distinct", checks)
    _assert((stock_transfers["ShipDate"] >= stock_transfers["RequestDate"]).all(), "stock transfers do not ship before request", checks)
    receipt_date = stock_transfers["ReceiptDate"]
    _assert((receipt_date.fillna(stock_transfers["ShipDate"]) >= stock_transfers["ShipDate"]).all(), "stock transfer receipts are not before ship dates", checks)

    _assert(sales_transactions["TransactionDate"].isin(calendar["CalendarId"]).all(), "sales transactions reference calendar rows", checks)
    _assert(sales_transactions["Store"].isin(stores["StoreId"]).all(), "sales transactions reference valid stores", checks)
    _assert(sales_transactions["Customer"].isin(customers["CustomerId"]).all(), "sales transactions reference valid customers", checks)
    _assert(sales_transactions["Product"].isin(products["ProductId"]).all(), "sales transactions reference valid products", checks)
    _assert(sales_transactions["BasketNumber"].notna().all(), "sales transactions include basket numbers", checks)
    _assert(sales_transactions["PaymentMethod"].notna().all(), "sales transactions include payment methods", checks)
    sales_promo = sales_transactions.loc[sales_transactions["Promotion"].notna()].copy()
    _assert(sales_promo["Promotion"].isin(promotions["PromotionId"]).all(), "sales transactions reference valid promotions when present", checks)
    if len(sales_promo):
        promo_join = sales_promo.merge(
            promotions[["PromotionId", "Product", "Store", "StartDate", "EndDate"]],
            left_on="Promotion",
            right_on="PromotionId",
            how="left",
            suffixes=("_Sale", "_Promo"),
        )
        sale_store = promo_join["Store_Sale"].astype("Int64").fillna(-1)
        promo_store = promo_join["Store_Promo"].astype("Int64").fillna(-1)
        store_match = promo_join["Store_Promo"].isna() | (sale_store == promo_store)
        product_match = promo_join["Product_Sale"] == promo_join["Product_Promo"]
        date_match = (promo_join["TransactionDate"] >= promo_join["StartDate"]) & (promo_join["TransactionDate"] <= promo_join["EndDate"])
        _assert((store_match & product_match & date_match).all(), "sales promotions align with product, store, and date scope", checks)

    _assert(inventory_snapshot["SnapshotDate"].isin(calendar["CalendarId"]).all(), "inventory snapshots reference calendar rows", checks)
    _assert(inventory_snapshot["Store"].isin(stores["StoreId"]).all(), "inventory snapshots reference valid stores", checks)
    _assert(inventory_snapshot["Product"].isin(products["ProductId"]).all(), "inventory snapshots reference valid products", checks)
    _assert((inventory_snapshot["ReorderTargetQty"] > inventory_snapshot["ReorderPointQty"]).all(), "inventory reorder target exceeds reorder point", checks)
    _assert((inventory_snapshot["AvailableQty"] <= inventory_snapshot["OnHandQty"]).all(), "inventory available quantity does not exceed on-hand", checks)
    _assert((inventory_snapshot["RegularPrice"] > inventory_snapshot["UnitCost"]).all(), "inventory regular price exceeds unit cost", checks)

    access_count = user_store_access.groupby("UserRef", observed=True).size()
    partial_users = users.loc[users["AccessScope"] == "PARTIAL"]
    full_users = users.loc[users["AccessScope"] == "FULL"]
    _assert((partial_users["CategoryScope"] != "ALL").all(), "partial users are category scoped", checks)
    _assert((full_users["CategoryScope"] == "ALL").all(), "full users have all-category scope", checks)
    if len(partial_users):
        _assert((access_count.loc[partial_users["UserId"]] < len(stores)).all(), "partial users are not granted every store", checks)
    if len(full_users):
        _assert((access_count.loc[full_users["UserId"]] == len(stores)).all(), "full users are granted every store", checks)

    if promotions["Store"].isna().mean() < 0.20:
        warnings.append("Chainwide promotions are sparse; advanced promo demos may look too store-specific.")
    if float((sales_transactions["Promotion"].notna()).mean()) < 0.05:
        warnings.append("Promotion attachment in sales is low; promo analysis may feel thin.")
    if float((inventory_snapshot["OnHandQty"] < inventory_snapshot["ReorderPointQty"]).mean()) < 0.05:
        warnings.append("Low-stock inventory states are rare; replenishment demos may have limited edge cases.")
    if sales_transactions["BasketNumber"].nunique() >= len(sales_transactions):
        warnings.append("Most baskets are single-line only; basket-level retail analysis may still feel flat.")

    return ValidationResult(ok=True, checks=checks, warnings=warnings)
