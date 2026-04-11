# Retail Dataset Guide

This guide describes the current Retail dataset in this repository: what each table represents, how the generated values behave, and the kinds of demos the dataset supports well.

## Overview

The Retail domain models a multi-store operation with stores, products, staff access, promotions, purchase orders, stock transfers, sales transactions, and inventory snapshots. It is designed for store-operations, merchandising, omnichannel, and promo-effectiveness demos rather than for full point-of-sale or ERP replication.

Current package and entrypoints:

- IRIS package: `Retail`
- Python package root: `src/Retail/python/DataGen`
- Lazy-compile sentinel: `Retail.Stores`
- Shared IRIS loader call: `do ##class(SyntheticDataGen.DataLoader).LoadData("Retail")`

Current generated outputs:

- `calendar.csv`
- `roles.csv`
- `users.csv`
- `user_store_access.csv`
- `stores.csv`
- `products.csv`
- `supplier_product.csv`
- `promotions.csv`
- `purchase_orders.csv`
- `stock_transfers.csv`
- `sales_transactions.csv`
- `inventory_snapshot.csv`

## What The Tables Represent

| Table | What it represents |
| --- | --- |
| `Calendar` | The retail calendar used to align events, seasons, and special retail periods such as payday and holiday peaks. |
| `Roles` | User-role definitions for access-control and persona-driven demos. |
| `Users` | Store and business users who interact with the retail estate. |
| `UserStoreAccess` | The access matrix showing which users can see which stores. |
| `Stores` | The retail network, including format, geography, active flag, and basic physical characteristics. |
| `Products` | The merchandise master with department, category, brand, price, private-label flag, and lifecycle timing. |
| `SupplierProduct` | The supplier-to-product bridge for sourcing and cost-oriented retail stories. |
| `Promotions` | Promotion campaigns with type, discount semantics, time window, and scope. |
| `PurchaseOrders` | Replenishment orders into the retail network. |
| `StockTransfers` | Store-to-store or network transfer events for inventory balancing. |
| `SalesTransactions` | The core sales fact table across stores and channels, including returns, discounts, gross/net amounts, and stockout flags. |
| `InventorySnapshot` | Synthetic inventory-state rows used for stock, availability, and sell-through demos. |

## Current Value Semantics

### Calendar And Retail Events

The retail calendar gives the dataset a repeatable operational rhythm.

Current calendar semantics include:

- ISO-style time rollups
- season labels such as `WINTER`, `SPRING`, `SUMMER`, and `AUTUMN`
- retail-event markers such as `HOLIDAY_PEAK`, `PAYDAY`, and `NONE`

Useful interpretation:

- `HOLIDAY_PEAK` is useful for demand-surge storytelling.
- `PAYDAY` is useful for short-cycle spend and promo timing demos.

### Roles, Users, And Access

The retail dataset includes a lightweight but useful access-control model.

Current role vocabulary includes:

- `StoreLead`
- `RegionalViewer`
- `MerchandisingManager`
- `InventoryOpsManager`

Useful interpretation:

- `StoreLead` and `RegionalViewer` are useful for persona-based dashboards.
- manager roles are useful for governance, access, and operational tooling demos.
- `UserStoreAccess` is a good supporting table when you want to show role-aware experiences or access audits.

### Stores

Stores are not interchangeable. Store format affects transaction volume and transaction shape.

Current store formats include:

- `FLAGSHIP`
- `SUBURBAN`
- `URBAN`
- `OUTLET`

Useful interpretation:

- `FLAGSHIP` is useful for premium/high-volume demo stories.
- `OUTLET` is useful for discount, clearance, and margin-pressure stories.
- geography fields support regional rollups and district comparisons.

### Products

Products are built for assortment, pricing, and merchandising analysis.

Current departments include:

- `GROCERY`
- `BEVERAGE`
- `HOUSEHOLD`
- `PERSONAL_CARE`
- `ELECTRONICS`
- `APPAREL`
- `TOYS`

Useful supporting semantics include:

- regular price
- cost
- brand
- private-label flag
- launch and discontinue timing
- seasonality markers

Useful interpretation:

- private-label share supports mix and margin storytelling.
- department and category splits support merchandising and sell-through analysis.

### Promotions

Promotions are explicit first-class objects, which is a strong fit for demo work.

Current promotion types include:

- `PCT_OFF`
- `MULTIBUY`
- `CLEARANCE`
- `DIGITAL_COUPON`

Useful interpretation:

- `CLEARANCE` is useful for markdown and aging-stock stories.
- `DIGITAL_COUPON` is useful for channel and loyalty-style discussions.
- chain-wide vs store-specific scope lets you compare broad and local activation.

### Sales Transactions

This is the main fact table for most retail demos.

Current channel vocabulary includes:

- `INSTORE`
- `CLICK_COLLECT`
- `DELIVERY`
- `SHIP_FROM_STORE`

Current fulfillment semantics include:

- `TAKEAWAY`
- `PICKUP`
- `HOME_DELIVERY`
- `SHIP_FROM_STORE`

Useful interpretation:

- the channel split is strong enough for omnichannel demos.
- return and stockout flags are already built in, so the dataset supports exception-style analysis well.
- gross, net, discount, and COGS measures make margin storytelling straightforward.

### Inventory And Supply Operations

The retail dataset includes replenishment and balancing tables to support operational stories beyond sales alone.

Current stock-transfer statuses include:

- `PENDING`
- `IN_TRANSIT`
- `DELAYED`
- `RECEIVED`

Useful interpretation:

- `PurchaseOrders` supports replenishment and inbound risk views.
- `StockTransfers` supports balancing and fulfillment-support stories.
- `InventorySnapshot` is the easiest starting point for store-stock dashboards.

## Time And Scale Behavior

Useful current behavior:

- Default sample horizon is 90 days.
- Weekend and retail-event effects are built into the generated demand pattern.
- Runtime scale-factor overrides are supported through the CLI and through `DataLoader.LoadData(...)`.
- Promotion attach behavior, return behavior, and stockout behavior are all explicit generator concepts.

## Suggested Demo Projects

### 1. Store Performance Dashboard

Compare stores on:

- sales
- transactions
- average basket
- channel mix
- return rate
- stockout rate

Why it works:

- store-format and regional differences are built into the generated data, so the comparisons are visually useful.

### 2. Promotional Effectiveness Demo

Measure the impact of promotions by:

- promotion type
- department
- store format
- chain-wide vs local scope

Why it works:

- promotions are modeled explicitly and linked to transactional behavior.

### 3. Omnichannel Retail Story

Show how channel mix changes across:

- `INSTORE`
- `CLICK_COLLECT`
- `DELIVERY`
- `SHIP_FROM_STORE`

Why it works:

- channel and fulfillment semantics are already present in the base fact table.

### 4. Inventory Allocation And Rebalancing Demo

Focus on:

- stockouts by store and department
- low-availability items
- transfer delays
- inventory levels vs sales pressure

Why it works:

- the dataset includes inventory state, transfers, and demand in one coherent domain.

### 5. Returns And Margin Analysis

Use sales transactions to show:

- signed sales impact of returns
- discount pressure
- net sales vs gross sales
- category-level margin behavior

Why it works:

- the transaction table already includes return and signed-value semantics.

### 6. Role-Aware Retail Operations Demo

Build a persona-based experience where:

- store leads see only their stores
- regional viewers see cross-store rollups
- managers see supplier and cost detail

Why it works:

- the role and user-store access model is already present, which is rare in synthetic demo datasets.

## Good Starter Metrics For A Demo

If you want a quick first dashboard, these metrics usually tell the story fastest:

- gross sales and net sales
- average units per transaction
- channel mix
- promotion attach rate
- markdown or discount rate
- return rate
- stockout rate
- inventory availability by store and department

## Useful Caveats And Suggestions

- `InventorySnapshot` is synthetic state data, so it should be treated as dashboard-friendly inventory state rather than a guaranteed exact reconstruction from transactional events.
- Return rows are intentionally useful for analytics because signed financial values flip direction when the return flag is present.
- Promotions can be chain-wide or store-specific, which makes scope an important filter in demos.
- Store format materially changes demand shape, so format is usually worth including in first-pass dashboards.
- If you want a short live demo, start with one of these three stories: promo effectiveness, omnichannel mix, or stockout and inventory allocation.
