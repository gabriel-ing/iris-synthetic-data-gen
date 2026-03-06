# Synthetic Financial Dataset Generator

Synthetic dataset generator for Financial Services demos (InterSystems IRIS-ready later).

Detailed architecture and extension guide:

- `docs/SYNTHETIC_DATA_GEN_ARCHITECTURE.md`

## What it generates

- `customers.csv`
- `cards.csv`
- `merchants.csv`
- `transactions.csv` (or daily partitions)
- `disputes.csv`

## Quick start

1. Create a Python 3.10+ environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run generator:

```bash
python -m synthetic_data_gen.main --config config/sample_config.yaml
```

Output is written to `./out` by default.

## Run tests

```bash
pytest
```

## Load into InterSystems IRIS

1. Install IRIS DB-API package:

```bash
pip install intersystems-irispython
```

2. Print DDL only (easy copy/paste):

```bash
python scripts/load_csv_to_iris.py --package finance --print-ddl
```

3. Create tables and load CSV data:

```bash
python scripts/load_csv_to_iris.py \
	--data-dir out \
	--server localhost --port 52776 \
	--namespace USER --username SuperUser --password SYS \
	--package finance \
	--chunk-size 5000
```

4. Optional reset of tables before load:

```bash
python scripts/load_csv_to_iris.py --data-dir out --package finance --drop-existing
```

## Direct Insert Into IRIS (No CSV)

Use the alternate entrypoint to generate in memory and insert directly with
`iris.sql.prepare(...).execute(...)`.

```bash
python -m synthetic_data_gen.main_iris \
	--config config/sample_config.yaml \
	--package finance \
	--clear-existing \
	--commit-every 20000
```

Notes:
- This mode expects the `iris` Python module to be available (IRIS Embedded Python or `intersystems-irispython`).
- It does not create CSV files.
- It assumes your classes/tables already exist in IRIS.

### Class reference columns used by generator

- `cards.csv`: uses `Customer` (reference to `finance.Customers`)
- `transactions.csv`: uses `Card` and `Merchant` (references to `finance.Cards` and `finance.Merchants`)
- `disputes.csv`: uses `Transactions` (reference to `finance.Transactions`)

### IRIS SQL arrow notation examples

```sql
SELECT TOP 10
	t.TransactionId,
	t.Card->CardType AS CardType,
	t.Card->Customer->Segment AS CustomerSegment,
	t.Merchant->MerchantName AS MerchantName,
	t.Merchant->Country AS MerchantCountry,
	t.Amount,
	t.Status
FROM finance.Transactions t
ORDER BY t.TransactionId;
```

```sql
SELECT
	d.DisputeId,
	d.Transactions->Status AS TxnStatus,
	d.Transactions->Merchant->Category AS MerchantCategory,
	d.Transactions->Card->Customer->RiskScore AS CustomerRiskScore,
	d.DisputedAmount
FROM finance.Disputes d;
```

## Notes

- Deterministic output from `seed` + config.
- Current implementation targets CSV output first.
- Merchant names are generated as synthetic company names via Faker.
- Merchant country distribution is USA-primary with additional countries included.
- IRIS loading can be added in a later phase.
