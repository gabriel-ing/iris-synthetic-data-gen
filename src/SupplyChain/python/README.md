# Supply Chain Synthetic Data Generator

This package is the Supply Chain companion domain to the Financial Services generator.

## What it generates

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

## Run

From `SupplyChain/python`:

```bash
c:/Users/ging/external_hackathon/synthetic_data_gen/.venv/Scripts/python.exe -m DataGen.main --config config/sample_config.yaml
```

## Test

From `SupplyChain/python`:

```bash
c:/Users/ging/external_hackathon/synthetic_data_gen/.venv/Scripts/python.exe -m pytest
```

## Reuse Design

- Shared deterministic RNG namespace pattern (`DataGen/rng.py`).
- Shared config merge + explicit/factor scale strategy (`DataGen/config.py`).
- Domain-specific generators isolated in `DataGen/generators/`.
- Validation and writer modules separated from generator logic.

This separation is intended to make packaging into an InterSystems Package Manager module straightforward once ObjectScript classes and loader scripts are finalized.
