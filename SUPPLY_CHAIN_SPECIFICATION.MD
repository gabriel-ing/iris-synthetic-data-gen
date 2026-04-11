# Supply Chain Domain: Current Implemented Specification

This file describes the Supply Chain dataset as it is currently implemented in this repository. It replaces the earlier greenfield design brief.

## Package Mapping

- Python root: `src/SupplyChain/python/DataGen`
- ObjectScript package: `SupplyChain`
- Lazy-compile sentinel: `SupplyChain.DimCustomer`
- Direct IRIS loader: `src/SupplyChain/python/DataGen/main_iris.py`

## Current Generated Tables

- `dim_date.csv`
- `dim_product.csv`
- `dim_location.csv`
- `dim_supplier.csv`
- `dim_customer.csv`
- `product_supplier.csv`
- `sales_order_line.csv`
- `purchase_order_line.csv`
- `shipment_line.csv`
- `inventory_movement.csv`
- `inventory_snapshot_daily.csv`
- `stock_count_event.csv`

## Current Class and Model Layers

Dimensions:
- `DimDate`
- `DimProduct`
- `DimLocation`
- `DimSupplier`
- `DimCustomer`

Relationship bridge:
- `ProductSupplier`

Transaction and event tables:
- `SalesOrderLine`
- `PurchaseOrderLine`
- `ShipmentLine`
- `InventoryMovement`
- `StockCountEvent`

Snapshot:
- `InventorySnapshotDaily`

## Current Generation Order

1. `DimDate`
2. `DimProduct`
3. `DimLocation`
4. `DimSupplier`
5. `DimCustomer`
6. `ProductSupplier`
7. `SalesOrderLine`
8. `PurchaseOrderLine`
9. `ShipmentLine`
10. `StockCountEvent`
11. `InventoryMovement`
12. `InventorySnapshotDaily`

## Current Run Commands

CSV generation:

```bash
cd src/SupplyChain/python
python -m DataGen.main --config config/sample_config.yaml
python -m DataGen.main --config config/sample_config.yaml --scale-factor 2
```

Direct IRIS insert:

```bash
cd src/SupplyChain/python
python -m DataGen.main_iris --config config/sample_config.yaml --package SupplyChain --clear-existing
```

From an IRIS session through the shared loader:

```objectscript
do ##class(SyntheticDataGen.DataLoader).LoadData("SupplyChain")
do ##class(SyntheticDataGen.DataLoader).LoadData("SupplyChain",2)
do ##class(SyntheticDataGen.DataLoader).DeleteDataset("SupplyChain")
```

## Current IRIS Load Behavior

- The direct loader defaults to package `SupplyChain`.
- `--clear-existing` deletes existing rows in child-first order before insert.
- `--commit-every` controls commit batch size.
- `DataLoader.DeleteDataset("SupplyChain")` clears the dataset and removes the compiled classes by default.

## Current Implementation Notes

- Line tables rely on auto-generated `%ID`; the Supply Chain IRIS loader does not insert `%ID` explicitly.
- In this environment, the embedded Python IRIS loader is most reliable when nullable SQL values are bound as empty strings.
- `%Date` values are passed as IRIS logical-date integers in the Supply Chain IRIS loader.
- Sample generated CSVs under `src/SupplyChain/python/out_supply_chain/` are artifacts, not canonical schema definitions.

## Current Use Cases

- order, shipment, and delay analysis
- inventory availability and negative-available scenarios
- supplier and lane performance
- stock-count adjustment and shrink analysis
