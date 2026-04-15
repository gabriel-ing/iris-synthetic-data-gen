# Supply Chain Dataset Guide

This guide describes the current Supply Chain dataset in this repository: what the tables mean, how the generated values behave, and the kinds of demos the dataset supports well.

## Overview

The Supply Chain domain models the flow of products through suppliers, facilities, orders, shipments, inventory movements, and daily stock snapshots. It is designed for operations, planning, fulfillment, and inventory-control demos rather than for full ERP replication.

Current package and entrypoints:

- IRIS package: `SupplyChain`
- Python package root: `src/SupplyChain/python/DataGen`
- Lazy-compile sentinel: `SupplyChain.DimCustomer`
- Shared IRIS loader call: `do ##class(SyntheticDataGen.DataLoader).LoadData("SupplyChain")`

Current generated outputs:

- `dim_date.csv`
- `dim_product.csv`
- `dim_location.csv`
- `dim_supplier.csv`
- `dim_customer.csv`
- `product_supplier.csv`
- `sales_orders.csv`
- `sales_order_line.csv`
- `purchase_orders.csv`
- `purchase_order_line.csv`
- `shipment_line.csv`
- `inventory_movement.csv`
- `inventory_snapshot_daily.csv`
- `stock_count_event.csv`

## What The Tables Represent

| Table | What it represents |
| --- | --- |
| `DimDate` | The reporting calendar. It supports trend analysis, weekday/weekend effects, and time-based rollups. |
| `DimProduct` | The product master with category, brand, cost, list price, unit, shelf-life, and handling attributes. |
| `DimLocation` | The location network, including distribution centers, stores, customer sites, and supplier sites. |
| `DimSupplier` | The supplier master with commercial and logistics attributes such as payment terms, incoterms, and preferred ship modes. |
| `DimCustomer` | The buying population for outbound sales, including customer type, region, and commercial segment. |
| `ProductSupplier` | The bridge between products and suppliers, including sourcing constraints such as MOQ and order multiples. |
| `SalesOrders` | The customer-order header layer derived from line activity. It consolidates status, dates, quantities, and order value at document level. |
| `SalesOrderLine` | Customer-demand lines with ordered, allocated, shipped, backordered, and delivered quantities. |
| `PurchaseOrders` | The supplier-order header layer derived from line activity. It summarizes order status, order value, receipt timing, and late-receipt behavior. |
| `PurchaseOrderLine` | Supplier-facing replenishment lines with open, partial-receipt, and received behavior. |
| `ShipmentLine` | Physical fulfillment events moving product between origin and destination with carrier and service-level detail. |
| `InventoryMovement` | The event ledger for receipts, shipments, transfers, and adjustments. |
| `InventorySnapshotDaily` | A daily state table for on-hand, allocated, available, in-transit, on-order, and value measures. |
| `StockCountEvent` | Physical stock counts and variance events used for shrink, damage, and reconciliation demos. |

## Current Value Semantics

### Locations

The location model is intentionally mixed so you can tell both network-design and fulfillment stories.

Current location types include:

- `DC`
- `Store`
- `CustomerSite`
- `SupplierSite`

Useful interpretation:

- `DC` and `Store` support internal network and replenishment demos.
- `CustomerSite` is useful for outbound fulfillment stories.
- `SupplierSite` helps explain procurement and inbound lanes.

### Products

Products are designed to work for assortment, replenishment, and inventory-health stories.

Current product categories include:

- `GROCERY`
- `BEVERAGE`
- `HOUSEHOLD`
- `PERSONAL_CARE`
- `ELECTRONICS`
- `APPAREL`
- `SEASONAL`

Current supporting product semantics include:

- temperature zone
- perishable flag
- shelf-life days
- units per case
- weight and volume
- launch and discontinue timing

Useful interpretation:

- perishable and chilled items are good for freshness and waste stories.
- discontinued products are useful for slow-moving inventory and end-of-life analytics.

### Suppliers And Product-Supplier Relationships

The supplier side supports sourcing and vendor-performance demos.

Current supplier semantics include:

- tiered suppliers
- payment terms in days
- incoterms such as `EXW`, `FCA`, `DAP`, and `DDP`
- ship modes such as `Road`, `Air`, and `Ocean`

The `ProductSupplier` bridge adds sourcing realism through:

- minimum order quantity
- order multiple
- planned lead time

Useful interpretation:

- this makes it possible to demo supplier rationalization, MOQ pressure, and replenishment constraints.

### Customers And Sales Demand

Outbound demand is modeled at the order-line level.

Current customer types include:

- `Consumer`
- `B2B`

Current customer segments include:

- `Value`
- `Standard`
- `Premium`

Current sales channels include:

- `Store`
- `Ecomm`
- `B2B`

Current sales order statuses include:

- `Open`
- `PartShipped`
- `Shipped`
- `Delivered`
- `Cancelled`

Useful interpretation:

- `Open` and `PartShipped` are useful for backlog views.
- `Delivered` lets you measure service performance.
- `B2B` order lines are useful for comparing consumer-style and account-style demand patterns.
- The new `SalesOrders` header table is useful when you want one row per customer order instead of reconstructing documents from line-level data.

### Purchase Orders

Purchase orders now have both a header layer and a line layer, which makes the dataset easier to use for receipt, supplier, and inbound-control-tower demos.

Current purchase-order header statuses include:

- `Open`
- `PartReceived`
- `Received`
- `Cancelled`

Current purchase-order line statuses include:

- `Open`
- `PartReceived`
- `Closed`
- `Cancelled`

Useful interpretation:

- partial receipts are useful for inbound planning demos.
- late receipts are useful for supplier-performance and ETA-reliability views.
- The header table adds `LateReceiptFlag`, total quantities, and order value so common KPIs do not require rebuilding documents from lines first.

### Shipments

Shipments are the physical movement layer for outbound fulfillment.

Current shipment status vocabulary includes:

- `Pending`
- `InTransit`
- `Delayed`
- `Delivered`

Current service levels include values such as:

- `Ground`
- `Express`
- `Economy`

Current delay reasons visible in generated samples include:

- `Weather`
- `HubCongestion`
- `Customs`
- `Capacity`

Useful interpretation:

- split shipments and delay reasons are especially good for fulfillment and SLA demos.

### Inventory

The inventory layer is split into movement events, state snapshots, and physical counts.

Current inventory movement types include:

- `Receipt`
- `Shipment`
- `Transfer`
- `Adjustment`

Current stock-count variance reasons include:

- `Shrink`
- `Damage`
- `AdminError`
- `MisPick`

Useful interpretation:

- `InventoryMovement` is the operational event history.
- `InventorySnapshotDaily` is the easiest starting point for KPI dashboards.
- `StockCountEvent` is the best place to show reconciliation and root-cause analysis.

## Time And Scale Behavior

Useful current behavior:

- Default sample horizon is 180 days.
- The calendar dimension is built for time-series and fulfillment-lag analysis.
- Order activity is not perfectly flat; weekend and seasonal weighting is built into generation.
- Runtime scale-factor overrides are supported through the CLI and through `DataLoader.LoadData(...)`.
- Initial inventory is seeded before subsequent movement and snapshot behavior.

## Suggested Demo Projects

### 1. Supply Chain Control Tower

Build a control-tower dashboard that tracks:

- open customer backlog
- purchase orders at risk
- delayed shipments
- low-stock and out-of-stock positions
- freight cost by lane or service level

Why it works:

- the dataset has a complete enough event chain to tell an end-to-end operational story.

### 2. Supplier Performance Scorecard

Measure suppliers on:

- on-time receipt rate
- partial-receipt frequency
- average lead-time variance
- product-category exposure

Why it works:

- the supplier and purchase-order model already includes commercial and logistics semantics.

### 3. Fulfillment SLA And Delay Analysis

Compare requested, promised, and actual delivery performance by:

- channel
- customer segment
- origin location
- carrier
- service level

Why it works:

- shipments and sales lines both include the timing fields needed to tell an SLA story.

### 4. Inventory Health And Reconciliation Demo

Focus on:

- daily on-hand vs available stock
- safety-stock breaches
- stock-count variances
- shrink and damage hot spots

Why it works:

- the dataset includes both daily inventory state and exception-style count events.

### 5. Demand And Replenishment Planning Demo

Show how demand signals translate into procurement and inventory pressure using:

- sales order volume
- purchase order timing
- supplier lead time
- snapshot coverage

Why it works:

- the dataset is explicitly built around that upstream-to-downstream chain.

### 6. Network And Lane Optimization Story

Use locations, shipments, and freight costs to show:

- costly lanes
- service-level tradeoffs
- split-shipment frequency
- candidate network simplifications

## Good Starter Metrics For A Demo

If you want a quick first dashboard, these metrics usually tell the story fastest:

- fill rate
- on-time delivery rate
- partial-shipment rate
- late-receipt rate
- freight cost per shipped unit
- inventory value by location and product category
- stock-count variance rate
- available vs allocated stock

## Useful Caveats And Suggestions

- `InventorySnapshotDaily` is the easiest place to start for dashboarding, but it is still synthetic state data and should not be treated as a perfect ledger reconstruction.
- `InventoryMovement` is better when you want event-history storytelling or reconciliation logic.
- `SalesOrders` and `PurchaseOrders` are derived header tables, so the line tables remain the source of truth for exact operational sequencing.
- Delay reasons are intentionally readable for demos, which is useful for presentations and issue triage views.
- Sample CSV artifacts under `src/SupplyChain/python/out_supply_chain/` are useful examples, but the ObjectScript classes and generators remain the source of truth.
- If you want a short demo, anchor it around one business question: service performance, supplier performance, or inventory health.
