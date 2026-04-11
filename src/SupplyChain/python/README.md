# Supply Chain Synthetic Data Generator

This package generates the Supply Chain demo dataset used by the root SyntheticDataGen module.

## Outputs

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

## CSV Generation

From `src/SupplyChain/python`:

```bash
python -m DataGen.main --config config/sample_config.yaml
python -m DataGen.main --config config/sample_config.yaml --scale-factor 2
```

The output directory is controlled by the YAML config.

## Direct IRIS Insert

From `src/SupplyChain/python`:

```bash
python -m DataGen.main_iris --config config/sample_config.yaml --package SupplyChain --clear-existing
```

Current `main_iris.py` options:

- `--config`
- `--package` with default `SupplyChain`
- `--clear-existing`
- `--commit-every`
- `--scale-factor`

## Tests

From `src/SupplyChain/python`:

```bash
python -m pytest
```

## Through ZPM

After installing the root module in IRIS:

```objectscript
do ##class(SyntheticDataGen.DataLoader).LoadData("SupplyChain")
do ##class(SyntheticDataGen.DataLoader).LoadData("SupplyChain",2)
do ##class(SyntheticDataGen.DataLoader).DeleteDataset("SupplyChain")
```

`SupplyChain.DimCustomer` is the lazy-compile sentinel class for this domain.
