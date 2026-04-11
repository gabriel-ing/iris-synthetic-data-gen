# Retail Synthetic Data Generator

This package generates the Retail demo dataset used by the root SyntheticDataGen module.

## Outputs

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

## CSV Generation

From `src/Retail/python`:

```bash
python -m DataGen.main --config config/sample_config.yaml
python -m DataGen.main --config config/sample_config.yaml --scale-factor 2
```

The output directory is controlled by the YAML config.

## Direct IRIS Insert

From `src/Retail/python`:

```bash
python -m DataGen.main_iris --config config/sample_config.yaml --package Retail --clear-existing
```

Current `main_iris.py` options:

- `--config`
- `--package` with default `Retail`
- `--clear-existing`
- `--commit-every`
- `--scale-factor`

## Tests

From `src/Retail/python`:

```bash
python -m pytest
```

## Through ZPM

After installing the root module in IRIS:

```objectscript
do ##class(SyntheticDataGen.DataLoader).LoadData("Retail")
do ##class(SyntheticDataGen.DataLoader).LoadData("Retail",2)
do ##class(SyntheticDataGen.DataLoader).DeleteDataset("Retail")
```

`Retail.Stores` is the lazy-compile sentinel class for this domain.