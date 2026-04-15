# Dataset Improvement Action Plan

This document captures the current assessment of the synthetic datasets in this repository and the improvement work that should make the generators more useful, more realistic, and easier to adopt.

## Current Assessment

The datasets are already useful for demos, prototypes, and analytics walkthroughs. Their strongest value today is that they provide coherent domain stories instead of anonymous random tables.

Current strengths:

- Financial Services is strong for fraud, dispute, and payment-risk demos.
- Retail is strong for store operations, promotions, and inventory narratives.
- Supply Chain is strong for backlog, shipment, and inventory control-tower stories.
- Theme Park is strong for incident triage, staffing, and feedback summarization workflows.

Current weaknesses:

- several domains still flatten important real-world business concepts into line-level or event-only records
- default dataset scales can be too small to feel operationally realistic
- validations focus more on referential integrity than on realistic KPI ranges
- config ergonomics are inconsistent across domains
- cross-domain tooling is not yet uniform

## Prioritized Improvements

### 1. Define Supported Realism Tiers

Add named generation tiers per domain:

- `demo`
- `plausible`
- `stress`

Each tier should ship with expected KPI ranges so users know what kind of realism they are generating.

### 2. Replace Raw Config-First Entry With Scenario Presets

Ship named scenarios such as:

- retail holiday promotion surge
- financial-services fraud spike weekend
- supply-chain supplier disruption
- theme-park weather event day

### 3. Close One High-Value Schema Gap Per Domain

Phase-one targets:

- Financial Services: add account-level context between customers and cards
- Retail: add customer, basket, and payment context to sales
- Supply Chain: add order-header tables derived from existing order lines
- Theme Park: add queue and wait-time telemetry for rides

### 4. Add Realism Validators

Every run should emit KPI checks and warnings for domain realism, not only referential integrity.

Examples:

- transactions per store per day
- dispute-rate bands by channel
- shipment delay and partial-ship ranges
- ride wait-time and downtime ranges

### 5. Improve Config Ergonomics

Remove duplicated or overlapping knobs, standardize naming, and prefer named scale profiles over hand-edited row counts.

### 6. Normalize Platform Behavior

Bring CSV generation, direct IRIS load, and runtime behavior to parity across domains.

### 7. Improve Dataset Positioning

Add a top-level comparison table that shows:

- what each dataset is best for
- what it does not model well
- recommended scale tiers
- starter demo questions and SQL examples

### 8. Add Benchmark Profiles

Ship business profiles based on recognizable operating shapes, not only raw record counts.

Examples:

- regional card portfolio
- mid-market retailer
- multi-DC fulfillment network
- destination resort operator

## Phase-One Implementation Notes

The first coding pass for item 3 should favor additions that improve realism without rewriting the entire repo:

- derive new header or telemetry tables from existing facts where possible
- keep load and delete flows aligned with the new classes
- add validation coverage for the new entities
- preserve current CLI and loader signatures