# Synthetic Data Generator Architecture and Extension Guide

## Purpose

This project generates a deterministic synthetic financial-services dataset and supports two loading patterns for InterSystems IRIS:

- CSV-first pipeline (`python -m synthetic_data_gen.main`)
- Direct insert pipeline with embedded Python (`python -m synthetic_data_gen.main_iris`)

It is designed to preserve relational integrity and temporal consistency while remaining configurable and reproducible.

## High-Level Data Model

Current domain tables/classes:

- `Customers`
- `Cards` -> references `Customers` via `Customer`
- `Merchants`
- `Transactions` -> references `Cards` via `Card`, `Merchants` via `Merchant`
- `Disputes` -> references `Transactions` via `Transactions`

Current IRIS persistent classes are in `src/finance/*.cls`.

## End-to-End Pipeline

Generation order and why:

1. Merchants: needed for transaction merchant sampling
2. Customers: needed for card assignment and customer behavior signals
3. Cards: needed for transaction card sampling and temporal constraints
4. Transactions: main fact table generated across the configured time window
5. Edge cases: controlled post-processing to inject demo scenarios
6. Disputes: generated from transaction outcomes and risk signals
7. Validation: integrity, temporal checks, count checks, realism checks
8. Output:
   - `main.py`: writes CSV files
   - `main_iris.py`: inserts directly into IRIS

## Module-by-Module Reference

### Core orchestration

- `synthetic_data_gen/main.py`
  - CSV mode entrypoint
  - Calls generator sequence, validation, summary, and writer
- `synthetic_data_gen/main_iris.py`
  - Direct-to-IRIS entrypoint
  - Calls generator sequence and validation, then executes prepared SQL inserts directly with `iris.sql.prepare(...).execute(...)`

### Configuration and reproducibility

- `synthetic_data_gen/config.py`
  - Loads YAML config
  - Deep-merges defaults with user config
  - Resolves counts via either:
    - explicit counts (`scale.mode = explicit`)
    - factor mode (`scale.mode = factor`)
- `synthetic_data_gen/rng.py`
  - Deterministic seed derivation by namespace (`sub_seed`)
  - Ensures each table generator gets stable RNG streams

### Table generators

- `synthetic_data_gen/generators/merchants.py`
  - Category/risk assignment from weighted distributions
  - Popularity skew via Pareto
  - Synthetic company names via Faker
  - Country distribution with USA as primary
- `synthetic_data_gen/generators/customers.py`
  - Segment assignment and risk-score distributions
  - `State` is US-state based
  - Includes behavior multipliers used downstream
- `synthetic_data_gen/generators/cards.py`
  - Card allocation to customers with realistic skew
  - Card open/close status and temporal fields
- `synthetic_data_gen/generators/transactions.py`
  - Daily/chunked generation logic over time window
  - Card and merchant weighted sampling
  - Amount model by merchant category
  - Declines/refunds/reversals, fraud flags
  - Enforces card temporal validity (`OpenedAt` / `ClosedAt`)
- `synthetic_data_gen/generators/disputes.py`
  - Weighted sampling from transactions
  - Uses channel/segment/merchant risk effects
  - Ensures dispute timing follows transaction posting

### Post-processing and quality

- `synthetic_data_gen/edge_cases.py`
  - Optional deterministic edge-case injection:
    - customers with no cards
    - cards with only declines
    - blocked cards
    - fraud bursts
- `synthetic_data_gen/validate.py`
  - FK checks
  - temporal checks
  - configured-count checks
  - soft realism checks

### Writers and loaders

- `synthetic_data_gen/writer.py`
  - CSV writing
  - optional day partitioning for transactions
- `scripts/load_csv_to_iris.py`
  - DB-API style IRIS loader from generated CSVs
  - clear DDL section
  - chunked `executemany` inserts

## Current Output Schemas

### `customers.csv`

- `CustomerId`
- `CreatedAt`
- `Status`
- `Segment`
- `RiskScore`
- `State`
- `SegmentTxnMultiplier`
- `SegmentAmountMultiplier`
- `SegmentEcomMultiplier`
- `SegmentDeclineMultiplier`
- `SegmentDisputeMultiplier`

### `cards.csv`

- `CardId`
- `Customer` (reference value to `Customers.CustomerId`)
- `CardType`
- `Status`
- `OpenedAt`
- `ClosedAt`
- `CardToken`
- `CreditLimit`

### `merchants.csv`

- `MerchantId`
- `MerchantName`
- `Category`
- `RiskTier`
- `PopularityWeight`
- `Country`

### `transactions.csv`

- `TransactionId`
- `Card` (reference value to `Cards.CardId`)
- `Merchant` (reference value to `Merchants.MerchantId`)
- `AuthAt`
- `PostedAt`
- `Amount`
- `Currency`
- `Channel`
- `EntryMode`
- `CardPresent`
- `Status`
- `DeclineReason`
- `IsFraud`

### `disputes.csv`

- `DisputeId`
- `Transactions` (reference value to `Transactions.TransactionId`)
- `OpenedAt`
- `ResolvedAt`
- `ReasonCode`
- `State`
- `Outcome`
- `DisputedAmount`

## IRIS Integration Modes

### Mode A: CSV then load

1. Generate CSVs with `main.py`
2. Load with `scripts/load_csv_to_iris.py`

Best for:

- Auditable intermediate artifacts
- Re-running load without regeneration
- Data inspection/debugging

### Mode B: Direct insert (no CSV)

Use `main_iris.py` from an environment with IRIS Python available.

Best for:

- Fast iterative generation-to-database workflows
- Reduced disk I/O for large runs

## How IRIS class references are populated

Reference properties are inserted as referenced object IDs in SQL:

- `Cards.Customer` expects `Customers.CustomerId`
- `Transactions.Card` expects `Cards.CardId`
- `Transactions.Merchant` expects `Merchants.MerchantId`
- `Disputes.Transactions` expects `Transactions.TransactionId`

Arrow-notation query example:

```sql
SELECT TOP 20
  t.TransactionId,
  t.Card->Customer->Segment AS CustomerSegment,
  t.Merchant->MerchantName AS MerchantName,
  t.Amount
FROM finance.Transactions t;
```

## Testing Strategy

Tests live in `tests/`:

- `test_config.py`: config resolution (explicit and factor modes)
- `test_generation.py`: deterministic generation and validation checks
- `test_writer.py`: partitioned transaction writing
- `test_cli.py`: CLI smoke test and output creation

Run with:

```bash
.venv/Scripts/python.exe -m pytest
```

## What Is Reusable For Other Sectors

This project is intentionally split so only domain-specific layers need replacement.

### Reuse directly (high value, low change)

- `synthetic_data_gen/config.py`
  - config loading and scale derivation
- `synthetic_data_gen/rng.py`
  - deterministic sub-seeding pattern
- `synthetic_data_gen/writer.py`
  - CSV and partition writing primitives
- `synthetic_data_gen/validate.py` (structure)
  - reuse validation pattern; adapt business rules
- `synthetic_data_gen/main.py` and `synthetic_data_gen/main_iris.py` (orchestration skeleton)
  - preserve pipeline shape and swap generators
- `scripts/load_csv_to_iris.py` (loading pattern)
  - keep chunked loading framework; replace DDL and column mappings
- test harness in `tests/conftest.py`
  - reusable assembly and fixture approach

### Replace per domain (sector-specific)

- `synthetic_data_gen/generators/*.py`
  - these encode financial semantics and should be rewritten for healthcare, telecom, retail, manufacturing, etc.
- `src/finance/*.cls`
  - replace class definitions with your target sector schema
- edge-case scenarios in `edge_cases.py`
  - replace with domain-specific events (for example outages, claims spikes, shipment exceptions)
- realism checks in `validate.py`
  - tune to sector-specific quality metrics

## Template For New Sector Adaptation

Recommended approach:

1. Copy current package to a new domain package (for example `synthetic_data_gen_healthcare`).
2. Keep `config.py`, `rng.py`, `writer.py`, and orchestration files as baseline.
3. Design new entity graph and referential edges first.
4. Implement generators in topological order (dimensions before facts).
5. Add edge-case injector relevant to the new domain.
6. Update validation rules with domain invariants.
7. Update IRIS classes (`src/<domain>/*.cls`) and loader DDL/mapping.
8. Add/adjust tests:
   - deterministic outputs
   - FK integrity
   - temporal/business-rule invariants
   - loader smoke checks

## Practical Extension Tips

- Keep IDs as integer keys for performance and deterministic joins.
- Keep business distributions in config so they are tunable without code changes.
- Derive one RNG stream per table/module to avoid accidental coupling.
- Avoid writing giant in-memory fact tables for large scale; use chunk/day partitions.
- Validate early and fail fast before attempting database load.

## Known Current Constraints

- The `main_iris.py` direct mode assumes target IRIS classes/tables already exist.
- Realism warning thresholds are soft checks, not strict blockers.
- `State` in `customers.csv` is currently sampled from a representative subset of US state codes.

## Suggested Next Improvements

- Make country/state distributions configurable in YAML.
- Add optional index creation step after load for large query workloads.
- Add a generic plugin interface for domain generators.
- Add formal schema versioning in config and emitted metadata.
