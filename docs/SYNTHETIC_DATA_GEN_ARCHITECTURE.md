# SyntheticDataGen Architecture

## Current Purpose

This repository currently implements four synthetic data domains for InterSystems IRIS:

- Financial Services
- Supply Chain
- Retail
- Theme Park Management

The repo combines:
- Python generators for CSV output and direct IRIS insert
- ObjectScript persistent classes for each domain
- one shared ZPM/ObjectScript loader, `SyntheticDataGen.DataLoader`

## Workspace Architecture

- `module.xml`
  - defines the root ZPM package
  - copies domain Python and ObjectScript assets into `${libdir}SyntheticDataGen/`
  - compiles only `SyntheticDataGen.DataLoader`

- `src/SyntheticDataGen/DataLoader.cls`
  - persists the install root
  - lazily compiles dataset classes by domain
  - dispatches embedded Python loads into the installed domain package
  - clears rows and optionally deletes compiled packages via `DeleteDataset()`

- `src/FinancialServices/`
  - Python generator and direct IRIS loader
  - ObjectScript classes in package `Finance`
  - CSV-to-IRIS helper script under `python/scripts/load_csv_to_iris.py`

- `src/SupplyChain/`
  - Python generator and direct IRIS loader
  - ObjectScript classes in package `SupplyChain`

- `src/Retail/`
  - Python generator and direct IRIS loader
  - ObjectScript classes in package `Retail`

- `src/ThemePark/`
  - Python generator and direct IRIS loader
  - ObjectScript classes in package `ThemePark`

## Domain Map

### Financial Services

- Package: `Finance`
- Python root: `src/FinancialServices/python/DataGen`
- Outputs: `customers`, `cards`, `merchants`, `transactions`, `disputes`
- Extra modules: `edge_cases.py`, `scripts/load_csv_to_iris.py`
- Lazy-compile sentinel: `Finance.Customers`

### Supply Chain

- Package: `SupplyChain`
- Python root: `src/SupplyChain/python/DataGen`
- Outputs: `dim_date`, `dim_product`, `dim_location`, `dim_supplier`, `dim_customer`, `product_supplier`, `sales_order_line`, `purchase_order_line`, `shipment_line`, `inventory_movement`, `inventory_snapshot_daily`, `stock_count_event`
- Lazy-compile sentinel: `SupplyChain.DimCustomer`

### Retail

- Package: `Retail`
- Python root: `src/Retail/python/DataGen`
- Outputs: `calendar`, `roles`, `users`, `user_store_access`, `stores`, `products`, `supplier_product`, `promotions`, `purchase_orders`, `stock_transfers`, `sales_transactions`, `inventory_snapshot`
- Lazy-compile sentinel: `Retail.Stores`

### Theme Park Management

- Package: `ThemePark`
- Python root: `src/ThemePark/python/DataGen`
- Outputs: `parks`, `zones`, `rides`, `ride_maintenance`, `employees`, `shifts`, `guests`, `tickets`, `incidents`, `feedback`
- Lazy-compile sentinel: `ThemePark.Parks`

## Shared Domain Pattern

Each domain currently follows the same basic structure:

- `DataGen/config.py`
- `DataGen/rng.py`
- `DataGen/writer.py`
- `DataGen/validate.py`
- `DataGen/main.py`
- `DataGen/main_iris.py`
- `DataGen/generators/`
- `tests/`

This keeps the repo consistent even though each domain has different tables and generation logic.

## Current Load Flows

### Flow 1: Local CSV Generation

1. Run `python -m DataGen.main --config ...`
2. Load YAML config and optional scale-factor override
3. Generate domain tables in domain-specific order
4. Run validation
5. Write CSVs to the configured output path
6. Print a run summary

### Flow 2: Direct IRIS Insert

1. Run `python -m DataGen.main_iris --config ... --package <Package>`
2. Optionally clear existing rows in child-first order
3. Generate data in memory
4. Insert rows into IRIS using embedded Python
5. Commit in batches using `--commit-every`

### Flow 3: ZPM Install Plus DataLoader

1. `zpm "install SyntheticDataGen"`
2. `PersistInstallRoot()` stores the installed asset root
3. `EnsureDatasetClasses(dataset)` loads the installed ObjectScript source tree only when the sentinel class is missing
4. `LoadData(dataset, ...)` inserts the installed domain Python path into `sys.path`, deletes cached `DataGen` modules, imports `DataGen.main_iris`, and calls the domain loader
5. `DeleteDataset(dataset, deleteClasses=1)` clears rows and optionally deletes the compiled domain package

## DataLoader Responsibilities

Current responsibilities in `src/SyntheticDataGen/DataLoader.cls`:

- resolve and persist the installed asset root
- validate dataset names and sentinel classes
- lazy-load ObjectScript classes from installed asset directories
- clear Python module cache before switching domains that share the `DataGen` top-level package name
- pass runtime scale-factor and config overrides into the embedded Python loader
- provide dataset cleanup through `DeleteDataset()`

## Current Testing Layout

- `src/<Domain>/tests/`: domain-specific unit and CLI coverage
- `tests/test_zpm_packaging.py`: root packaging test covering install-root persistence and lazy compilation

The packaging test validates that a fresh install starts without domain classes compiled, then confirms that `LoadData()` compiles only the requested domain.

## Current Constraints

- Only Financial Services currently includes a CSV-to-IRIS utility script.
- The shared top-level Python package name is `DataGen` in all domains, so module-cache invalidation is required between loads.
- `LoadData()` uses positional order `dataset, scaleFactor, configPath, clearExisting`.
- `EnsureDatasetClasses()` currently uses `$system.OBJ.LoadDir(...)`, which works but produces a deprecation warning during validation.
