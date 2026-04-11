# Financial Services Dataset Guide

This guide describes the current Financial Services dataset in this repository: what each table represents, how the generated values behave, and the kinds of demos the dataset supports well.

## Overview

The Financial Services domain models a card-payment ecosystem with customers, cards, merchants, transactions, and disputes. It is designed for fraud, risk, payments, and chargeback demos rather than for core banking or full account-ledger simulations.

Current package and entrypoints:

- IRIS package: `Finance`
- Python package root: `src/FinancialServices/python/DataGen`
- Lazy-compile sentinel: `Finance.Customers`
- Shared IRIS loader call: `do ##class(SyntheticDataGen.DataLoader).LoadData("FinancialServices")`

Current generated outputs:

- `customers.csv`
- `cards.csv`
- `merchants.csv`
- `transactions.csv`
- `disputes.csv`

## What The Tables Represent

| Table | What it represents |
| --- | --- |
| `Customers` | The account-holder population. Each customer has a segment, lifecycle status, geographic attributes, and a risk score that affects transaction and dispute behavior. |
| `Cards` | Payment cards tied to customers. Cards carry lifecycle fields such as opened/closed timestamps, credit limits, status, and tokenization-style identifiers for card-product demos. |
| `Merchants` | Merchants that accept card payments. They include category and risk-tier attributes that influence dispute and fraud behavior. |
| `Transactions` | The core payment-event table. It records amount, timestamps, merchant, card, channel, entry mode, approval/decline state, and fraud indicators. |
| `Disputes` | Post-transaction chargebacks and customer disputes. These rows link back to transactions and capture reason, current state, outcome, and resolution timing. |

## Current Value Semantics

### Customers

The customer population is behavior-driven rather than purely uniform. The generator currently uses segment-based multipliers that affect transaction frequency, e-commerce share, fraud rate, and dispute rate.

Current segment vocabulary includes:

- `STUDENT`
- `MASS`
- `AFFLUENT`
- `HIGHRISK`
- `DORMANT`

Useful interpretation:

- `MASS` is the baseline broad retail population.
- `AFFLUENT` tends to support higher spend patterns.
- `HIGHRISK` is intended for fraud and risk demos.
- `DORMANT` is useful for lifecycle and inactivity stories.
- `STUDENT` gives a lower-ticket, different-channel behavioral cluster.

Customer lifecycle status currently uses:

- `ACTIVE`
- `CLOSED`

### Cards

Cards are instruments rather than standalone accounts. A customer may have multiple cards, and card lifecycle matters for fraud, authorization, and operational demos.

Current card statuses include:

- `ACTIVE`
- `BLOCKED`
- `CLOSED`

Useful interpretation:

- `BLOCKED` supports fraud-operations and card-control demos.
- `CLOSED` supports portfolio attrition and lifecycle views.

### Merchants

Merchants are modeled as payment-acceptance endpoints with both business category and risk metadata.

Current merchant categories include:

- `GROCERY`
- `FUEL`
- `DINING`
- `TRAVEL`
- `RETAIL`
- `DIGITAL`

Current merchant risk tiers include:

- `LOW`
- `MED`
- `HIGH`

Useful interpretation:

- `DIGITAL` and higher-risk tiers are useful when showing elevated dispute or fraud exposure.
- Pareto-style merchant popularity means a relatively small merchant set can account for a large share of transaction volume, which is good for concentration demos.

### Transactions

This is the main fact table for most demo work. It is intentionally rich enough to support approval-rate, fraud-rate, and channel-mix analysis.

Current transaction channel vocabulary includes:

- `ECOM`
- `POS`

Current entry-mode vocabulary includes:

- `CHIP`
- `TAP`
- `MANUAL`

Current transaction statuses include:

- `APPROVED`
- `DECLINED`
- `REFUNDED`
- `REVERSED`

Current decline reasons include:

- `INSUFFICIENT_FUNDS`
- `SUSPECTED_FRAUD`
- `LIMIT_EXCEEDED`
- `INVALID_CVV`

Useful interpretation:

- `ECOM` vs `POS` is the main operational channel split.
- `MANUAL` entry mode is a good signal for e-commerce and exception paths.
- `REFUNDED` and `REVERSED` are intentionally distinct, so they support post-authorization and post-settlement stories.
- Decline reasons are useful for rule-engine, alerting, and operational workflow demos.

### Disputes

Disputes represent the chargeback and post-transaction case-management layer. They support both customer-impact and merchant-risk stories.

Current dispute reasons include:

- `FRAUD`
- `NOT_RECEIVED`
- `DUPLICATE`
- `NOT_AS_DESCRIBED`
- `CANCELLED`

Current dispute states include:

- `OPEN`
- `UNDER_REVIEW`
- `RESOLVED`

Current dispute outcomes include:

- `CUSTOMER_WON`
- `MERCHANT_WON`
- `WITHDRAWN`
- `CHARGEBACK`

Useful interpretation:

- `FRAUD` disputes are the obvious bridge to fraud analytics.
- `NOT_RECEIVED` and `NOT_AS_DESCRIBED` are useful for merchant-quality and channel-risk demos.
- Outcome fields let you show both operational workload and financial outcome.

## Time And Scale Behavior

The current generator is built around a configurable time window and seed-driven repeatability.

Useful current behavior:

- Default simulation window is 90 days in the sample configuration.
- Weekly seasonality is supported.
- Card opened/closed dates can fall outside the active simulation window.
- Disputes open after transactions and may resolve later, which makes the data useful for lagging-case demos.
- Runtime scale-factor overrides are supported through the CLI and through `DataLoader.LoadData(...)`.

## Edge Cases Already Supported

The Financial Services dataset already includes purposeful edge-case generation, which makes it stronger than a purely average-case demo dataset.

Current supported edge-case themes include:

- customers with no cards
- cards with only declines
- cards blocked mid-window
- concentrated fraud bursts across a small card set

These are especially useful when the audience wants to see whether dashboards, rules, or ML pipelines still behave well under abnormal conditions.

## Suggested Demo Projects

### 1. Fraud Operations Cockpit

Build a dashboard that shows:

- fraud rate by channel
- suspicious clusters by merchant and card
- blocked-card activity
- decline reason trends over time

Why it works:

- the dataset has explicit fraud signals, channel splits, and concentrated edge-case bursts.

### 2. Chargeback And Dispute Analytics

Build a workflow view for:

- dispute intake volume
- open vs resolved cases
- customer-won vs merchant-won outcomes
- dispute reasons by merchant category

Why it works:

- the dispute model already contains reason, state, and outcome fields with realistic lag between purchase and case handling.

### 3. Merchant Risk Scorecard

Show how merchants compare on:

- approval rate
- dispute rate
- fraud-linked transaction share
- refund and reversal rates

Why it works:

- merchants have both category and risk-tier semantics, and the transaction table is dense enough to support KPI-style aggregation.

### 4. Customer Segment Behavior Demo

Compare `STUDENT`, `MASS`, `AFFLUENT`, `HIGHRISK`, and `DORMANT` populations on:

- spend
- frequency
- digital-channel share
- decline rate
- dispute rate

Why it works:

- customer segments are intentionally behavior-driving, not just descriptive.

### 5. Authorization Strategy Simulation

Demonstrate how approval policy changes might affect:

- fraud capture
- customer friction
- false-positive declines
- high-risk merchant exposure

Why it works:

- the transaction status and decline-reason structure supports approval-rule storytelling well.

## Good Starter Metrics For A Demo

If you want a quick first dashboard, these metrics usually tell the story fastest:

- approval rate
- decline rate by reason
- e-commerce share of volume
- fraud rate by merchant category
- dispute rate by channel
- average ticket size by customer segment
- blocked-card count over time

## Useful Caveats And Suggestions

- This is a payments dataset, not a full bank-account or general-ledger dataset.
- Disputes are post-transaction case records, so they are best used for operational and risk analysis rather than accounting close demos.
- Fraud and dispute patterns are intentionally amplified enough to make demos readable; that is useful for presentations, but it should be stated if someone treats the output as production-like class imbalance.
- `DeleteDataset("FinancialServices")` is useful before repeatable demos if you want a clean rerun.
- If you want a short live demo, use a smaller scale factor and focus on one story: fraud, disputes, or merchant risk.
