# SyntheticDataGen Workspace Guide

This repository contains four implemented synthetic data domains for InterSystems IRIS and one shared ZPM/ObjectScript loader.

## Current Domains

- `FinancialServices`
  - IRIS package: `Finance`
  - Python package root: `src/FinancialServices/python/DataGen`
  - ObjectScript classes: `src/FinancialServices/ObjectScript`
  - Core tables: `Customers`, `Cards`, `Merchants`, `Transactions`, `Disputes`

- `SupplyChain`
  - IRIS package: `SupplyChain`
  - Python package root: `src/SupplyChain/python/DataGen`
  - ObjectScript classes: `src/SupplyChain/ObjectScript`
  - Core tables: `DimDate`, `DimProduct`, `DimLocation`, `DimSupplier`, `DimCustomer`, `ProductSupplier`, `SalesOrderLine`, `PurchaseOrderLine`, `ShipmentLine`, `InventoryMovement`, `InventorySnapshotDaily`, `StockCountEvent`

- `Retail`
  - IRIS package: `Retail`
  - Python package root: `src/Retail/python/DataGen`
  - ObjectScript classes: `src/Retail/ObjectScript`
  - Core tables: `Calendar`, `Roles`, `Users`, `UserStoreAccess`, `Stores`, `Products`, `SupplierProduct`, `Promotions`, `PurchaseOrders`, `StockTransfers`, `SalesTransactions`, `InventorySnapshot`

- `ThemePark`
  - IRIS package: `ThemePark`
  - Python package root: `src/ThemePark/python/DataGen`
  - ObjectScript classes: `src/ThemePark/ObjectScript`
  - Core tables: `Parks`, `Zones`, `Rides`, `RideMaintenance`, `Employees`, `Shifts`, `Guests`, `Tickets`, `Incidents`, `Feedback`

## Shared Integration Layer

- The ZPM module is defined in `module.xml`.
- Installation copies `requirements.txt` and all domain assets into `${libdir}SyntheticDataGen/`.
- The only ObjectScript class compiled during install is `SyntheticDataGen.DataLoader`.
- `^SyntheticDataGen("InstallRoot")` stores the installed asset root.
- Dataset ObjectScript classes are compiled lazily per domain by `SyntheticDataGen.DataLoader.EnsureDatasetClasses()`.

## DataLoader Contract

Current class: `src/SyntheticDataGen/DataLoader.cls`

Current methods:
- `PersistInstallRoot()`
- `DefaultInstallRoot()`
- `SetInstallRoot(path)`
- `GetInstallRoot()`
- `EnsureDatasetClasses(dataset)`
- `DeleteDataset(dataset, deleteClasses=1)`
- `LoadData(dataset, scaleFactor="", configPath="", clearExisting=0)`

Valid dataset names:
- `FinancialServices`
- `SupplyChain`
- `Retail`
- `ThemePark`

Important positional order for `LoadData()`:
1. dataset
2. scale factor
3. config path
4. clear-existing flag

## Repository Layout

- `src/SyntheticDataGen/DataLoader.cls`: shared IRIS entrypoint used by ZPM installs
- `src/<Domain>/python/DataGen`: domain generator, validation, writer, and direct IRIS loader
- `src/<Domain>/ObjectScript`: domain persistent classes
- `src/<Domain>/tests`: domain-specific unit tests
- `docs/`: repo-level architecture, troubleshooting, and integration notes
- `tests/test_zpm_packaging.py`: end-to-end ZPM install and lazy-compile coverage

## Maintenance Rules

- Keep `README.md`, `AGENTS.md`, `docs/`, `module.xml`, and `tests/test_zpm_packaging.py` aligned when loader signatures or install behavior change.
- Keep the child-first delete order aligned between `DataLoader.DeleteDataset()` and each domain's `main_iris.py` `clear_existing` behavior.
- Keep these sentinel classes stable unless you also update `DataLoader` and the packaging test:
  - `Finance.Customers`
  - `SupplyChain.DimCustomer`
  - `Retail.Stores`
  - `ThemePark.Parks`
- Do not move copied asset paths without updating install-root logic and documentation.
- `load_csv_to_iris.py` currently exists only for `FinancialServices`. `SupplyChain`, `Retail`, and `ThemePark` use `main_iris.py` for direct inserts.
- When writing docs or examples, prefer the current commands and signatures over the earlier single-domain Financial Services design notes.

## Common Commands

Local CSV generation:
- `cd src/FinancialServices/python && python -m DataGen.main --config config/sample_config.yaml`
- `cd src/SupplyChain/python && python -m DataGen.main --config config/sample_config.yaml`
- `cd src/Retail/python && python -m DataGen.main --config config/sample_config.yaml`
- `cd src/ThemePark/python && python -m DataGen.main --config config/sample_config.yaml`

Direct IRIS insert:
- `cd src/FinancialServices/python && python -m DataGen.main_iris --config config/sample_config.yaml --package Finance --clear-existing`
- `cd src/SupplyChain/python && python -m DataGen.main_iris --config config/sample_config.yaml --package SupplyChain --clear-existing`
- `cd src/Retail/python && python -m DataGen.main_iris --config config/sample_config.yaml --package Retail --clear-existing`
- `cd src/ThemePark/python && python -m DataGen.main_iris --config config/sample_config.yaml --package ThemePark --clear-existing`

From an IRIS session:
- `do ##class(SyntheticDataGen.DataLoader).LoadData("FinancialServices")`
- `do ##class(SyntheticDataGen.DataLoader).DeleteDataset("FinancialServices")`
- `do ##class(SyntheticDataGen.DataLoader).LoadData("ThemePark")`
- `do ##class(SyntheticDataGen.DataLoader).DeleteDataset("ThemePark")`
