# Synthetic Data Generators for InterSystems IRIS

This repository contains four implemented synthetic demo datasets for InterSystems IRIS:

- Financial Services
- Supply Chain
- Retail
- Theme Park Management

Each domain includes:
- Python generation and validation code
- sample YAML configuration
- ObjectScript persistent classes
- direct embedded-Python IRIS loading via `main_iris.py`
- domain-specific tests
- Linked relational tables which can be joined using `->` notation  

The root ZPM package installs a shared ObjectScript entrypoint, `SyntheticDataGen.DataLoader`, and copies all domain assets into the IRIS install tree for lazy compilation and load.

Information on each individual dataset can be found in [./docs/datasets](./docs/Datasets/)

*Disclaimer - AI was extensively used for this project. Datasets were designed with advice from an LLM, and much of the code is AI generated. Whilst there has been human oversight, the code has not been carefully reviewed, and the datasets may not be realistic or perfect. These datasets are scaleable and designed for demos where having linked data tables which look realistic, is more important than quality or realism of the data.*

**Feedback or contributions are welcome**

## Quickstart

### Install 

Install with InterSystems Package Manager with: 

```objectscript
zpm "install iris-synthetic-data-gen"
```

Or clone the repo to build a local container: 

```
git clone https://github.com/gabriel-ing/iris-synthetic-data-gen.git
cd iris-synthetic-data-gen
docker-compose up --build 
```

### Generating data

The Synthetic data can be generated directly into IRIS tables, from a single command: 

```objectscript
do ##class(SyntheticDataGen.DataLoader).Load("FinancialServices")
do ##class(SyntheticDataGen.DataLoader).Load("SupplyChain")
do ##class(SyntheticDataGen.DataLoader).Load("ThemePark")
do ##class(SyntheticDataGen.DataLoader).Load("Retail")
```

There are additional parameters for: 
    - Scale of dataset multiplier. 1 is default.
    - Path to Config file. The datasets are configurable, with the default config being available in `./<dataset>/python/config/sample_config.yaml`. 
    - Replace existing (boolean). 0 is default.

e.g. to overwrite an existing dataset with a new dataset which is 5 times bigger, you can run: 

```objectscript
do ##class(SyntheticDataGen.DataLoader).Load("Retail", 5, "", 1)
```

### Remove datasets 

If you want to remove the datasets, this is automated with the same classs: 

```objectscript
do ##class(SyntheticDataGen.DataLoader).DeleteDataset("Retail")
```

## Repository Layout

- `module.xml`: ZPM package definition
- `src/SyntheticDataGen/DataLoader.cls`: shared IRIS loader and cleanup entrypoint
- `src/FinancialServices/`: financial-services generator, classes, tests, and CSV loader script
- `src/SupplyChain/`: supply-chain generator, classes, and tests
- `src/Retail/`: retail generator, classes, and tests
- `src/ThemePark/`: theme-park generator, classes, and tests
- `docs/`: repo-level architecture, troubleshooting, and integration notes
- `tests/test_zpm_packaging.py`: end-to-end ZPM install and lazy-compile coverage

## Implemented Domains

### Financial Services

IRIS package: `Finance`

Generated outputs:
- `accounts.csv`
- `customers.csv`
- `cards.csv`
- `merchants.csv`
- `transactions.csv`
- `disputes.csv`

### Supply Chain

IRIS package: `SupplyChain`

Generated outputs:
- `sales_orders.csv`
- `purchase_orders.csv`
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

### Retail

IRIS package: `Retail`

Generated outputs:
- `customers.csv`
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

### Theme Park Management

IRIS package: `ThemePark`

Generated outputs:
- `queue_snapshot.csv`
- `parks.csv`
- `zones.csv`
- `rides.csv`
- `ride_maintenance.csv`
- `employees.csv`
- `shifts.csv`
- `guests.csv`
- `tickets.csv`
- `incidents.csv`
- `feedback.csv`

## Install Dependencies

Create a Python 3.10+ environment and install the shared requirements:

```bash
pip install -r requirements.txt
```

Root dependencies currently are:
- `numpy`
- `pandas`
- `pyyaml`
- `pytest`
- `faker`

## Local CSV Generation

Each domain exposes `python -m DataGen.main --config ...` and supports an optional `--scale-factor`.

Financial Services:

```bash
cd src/FinancialServices/python
python -m DataGen.main --config config/sample_config.yaml
python -m DataGen.main --config config/sample_config.yaml --scale-factor 2
```

Supply Chain:

```bash
cd src/SupplyChain/python
python -m DataGen.main --config config/sample_config.yaml
python -m DataGen.main --config config/sample_config.yaml --scale-factor 2
```

Retail:

```bash
cd src/Retail/python
python -m DataGen.main --config config/sample_config.yaml
python -m DataGen.main --config config/sample_config.yaml --scale-factor 2
```

Theme Park:

```bash
cd src/ThemePark/python
python -m DataGen.main --config config/sample_config.yaml
python -m DataGen.main --config config/sample_config.yaml --scale-factor 2
```

The output location is controlled by each domain config file.

## Direct Insert Into IRIS

Each domain also exposes `main_iris.py` for direct insert without writing CSVs first.

Financial Services:

```bash
cd src/FinancialServices/python
python -m DataGen.main_iris --config config/sample_config.yaml --package Finance --clear-existing
```

Supply Chain:

```bash
cd src/SupplyChain/python
python -m DataGen.main_iris --config config/sample_config.yaml --package SupplyChain --clear-existing
```

Retail:

```bash
cd src/Retail/python
python -m DataGen.main_iris --config config/sample_config.yaml --package Retail --clear-existing
```

Theme Park:

```bash
cd src/ThemePark/python
python -m DataGen.main_iris --config config/sample_config.yaml --package ThemePark --clear-existing
```

Current `main_iris.py` entrypoints support:
- `--config`
- `--package`
- `--clear-existing`
- `--commit-every`
- `--scale-factor`

Financial Services also includes a CSV-to-IRIS utility at `src/FinancialServices/python/scripts/load_csv_to_iris.py` for DDL printing and CSV-based loads.

## ZPM Install and DataLoader

The root module currently behaves as follows:

- installs module `SyntheticDataGen` from `module.xml`
- copies `requirements.txt` and all domain asset trees into `${libdir}SyntheticDataGen/`
- compiles only `SyntheticDataGen.DataLoader` during install
- persists the installed asset root in `^SyntheticDataGen("InstallRoot")`
- compiles dataset classes lazily when a domain is first ensured or loaded

Current DataLoader methods:
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

Important `LoadData()` positional order:
1. dataset
2. scale factor
3. config path
4. clear-existing flag

From an IRIS session:

```objectscript
zpm "install SyntheticDataGen"

do ##class(SyntheticDataGen.DataLoader).LoadData("FinancialServices")
do ##class(SyntheticDataGen.DataLoader).LoadData("SupplyChain",2)
do ##class(SyntheticDataGen.DataLoader).LoadData("Retail",2,"",1)
do ##class(SyntheticDataGen.DataLoader).LoadData("ThemePark",2)
do ##class(SyntheticDataGen.DataLoader).LoadData("FinancialServices","","/usr/irissys/lib/SyntheticDataGen/FinancialServices/python/config/sample_config.yaml",1)

do ##class(SyntheticDataGen.DataLoader).DeleteDataset("Retail")
do ##class(SyntheticDataGen.DataLoader).DeleteDataset("SupplyChain",0)
do ##class(SyntheticDataGen.DataLoader).DeleteDataset("ThemePark")
```

`DeleteDataset(dataset)` clears rows in child-to-parent order and, by default, removes the compiled dataset package. Pass `0` as the second argument if you want to keep the classes compiled.

Useful checks from an IRIS session:

```objectscript
write $get(^SyntheticDataGen("InstallRoot"))
write $classmethod("%Dictionary.ClassDefinition","%ExistsId","Finance.Customers")
write $classmethod("%Dictionary.ClassDefinition","%ExistsId","SupplyChain.DimCustomer")
write $classmethod("%Dictionary.ClassDefinition","%ExistsId","Retail.Stores")
write $classmethod("%Dictionary.ClassDefinition","%ExistsId","ThemePark.Parks")
```

On a fresh install, the domain classes should not exist until the corresponding domain is loaded or explicitly ensured.

## Testing

Run all Python tests from the repo root:

```bash
pytest
```

Run the ZPM packaging and lazy-compile test:

```bash
pytest tests/test_zpm_packaging.py -q
```

By default that test rebuilds the Docker Compose IRIS container for a clean install check. Set `SYNTHETICDATAGEN_REBUILD_DOCKER=0` to reuse the existing container for faster reruns.

Domain-specific tests can also be run from each domain directory with `python -m pytest`.

## Current Docs

- `docs/Datasets/FINANCIAL_SERVICES_DATASET_GUIDE.md`: detailed financial-services dataset semantics, values, and demo ideas
- `docs/Datasets/SUPPLY_CHAIN_DATASET_GUIDE.md`: detailed supply-chain dataset semantics, values, and demo ideas
- `docs/Datasets/RETAIL_DATASET_GUIDE.md`: detailed retail dataset semantics, values, and demo ideas
- `docs/Datasets/THEME_PARK_DATASET_GUIDE.md`: detailed theme-park dataset semantics, values, and demo ideas
- `docs/SYNTHETIC_DATA_GEN_ARCHITECTURE.md`: current repo architecture and load flows
- `docs/IRIS_PYTHON_SQLERROR_246_TROUBLESHOOTING.md`: embedded Python and IRIS SQL troubleshooting
- `docs/09.-Python-ObjectScript-Integration.md`: current shared Python/ObjectScript install pattern
- `SUPPLY_CHAIN_SPECIFICATION.MD`: current implemented supply-chain domain summary
- `src/SupplyChain/python/README.md`: supply-chain domain quick start
- `src/Retail/python/README.md`: retail domain quick start
- `src/ThemePark/python/README.md`: theme-park domain quick start

## Notes

- Output is deterministic for a given seed and config.
- All four domains support scale-factor overrides at runtime.
- The shared top-level Python package name is `DataGen` in each domain, so `DataLoader` clears cached `DataGen` modules before importing a different domain in embedded Python.
- `EnsureDatasetClasses()` currently uses `$system.OBJ.LoadDir(...)`, which works but reports a deprecation warning during validation.
