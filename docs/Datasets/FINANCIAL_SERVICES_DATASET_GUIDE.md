# Financial Services Dataset Guide

This guide describes the current Financial Services dataset in this repository: what each table represents, how the generated values behave, and the kinds of demos the dataset supports well.

## Overview

The Financial Services domain models a card-payment ecosystem with customers, accounts, cards, merchants, transactions, and disputes. It is designed for fraud, risk, payments, and chargeback demos rather than for core banking or full account-ledger simulations.

Current package and entrypoints:

- IRIS package: `Finance`
- Python package root: `src/FinancialServices/python/DataGen`
- Lazy-compile sentinel: `Finance.Customers`
- Shared IRIS loader call: `do ##class(SyntheticDataGen.DataLoader).LoadData("FinancialServices")`

Current generated outputs:

- `customers.csv`
- `accounts.csv`
- `cards.csv`
- `merchants.csv`
- `transactions.csv`
- `disputes.csv`

## Quick SQL Starter

The examples below use simplified DDL that mirrors the core tables in this dataset, followed by a few starter queries for fraud, dispute, and portfolio analysis.

### Representative DDL

```sql
CREATE TABLE Finance.Customers (
	CustomerId INTEGER NOT NULL,
	CreatedAt VARCHAR(35),
	Status VARCHAR(20),
	Segment VARCHAR(20),
	RiskScore INTEGER,
	State VARCHAR(20),
	SegmentTxnMultiplier DOUBLE,
	SegmentAmountMultiplier DOUBLE,
	SegmentEcomMultiplier DOUBLE,
	SegmentDeclineMultiplier DOUBLE,
	SegmentDisputeMultiplier DOUBLE,
	PRIMARY KEY (CustomerId)
);

CREATE TABLE Finance.Accounts (
	AccountNumber VARCHAR(40) NOT NULL,
	CustomerId INTEGER NOT NULL,
	AccountType VARCHAR(30),
	Status VARCHAR(20),
	OpenedAt VARCHAR(35),
	ClosedAt VARCHAR(35),
	BillingCycleDay INTEGER,
	AutopayFlag BOOLEAN,
	PRIMARY KEY (AccountNumber)
);

CREATE TABLE Finance.Cards (
	CardId INTEGER NOT NULL,
	CustomerId INTEGER,
	AccountNumber VARCHAR(40),
	CardType VARCHAR(20),
	Status VARCHAR(20),
	OpenedAt VARCHAR(35),
	ClosedAt VARCHAR(35),
	CardToken VARCHAR(80),
	CreditLimit INTEGER,
	PRIMARY KEY (CardId)
);

CREATE TABLE Finance.Merchants (
	MerchantId INTEGER NOT NULL,
	MerchantName VARCHAR(200),
	Category VARCHAR(40),
	RiskTier VARCHAR(20),
	PopularityWeight DOUBLE,
	Country VARCHAR(10),
	PRIMARY KEY (MerchantId)
);

CREATE TABLE Finance.Transactions (
	TransactionId BIGINT NOT NULL,
	CardId INTEGER,
	MerchantId INTEGER,
	AuthAt VARCHAR(35),
	PostedAt VARCHAR(35),
	Amount NUMERIC(18, 2),
	Currency VARCHAR(10),
	Channel VARCHAR(20),
	EntryMode VARCHAR(20),
	CardPresent INTEGER,
	Status VARCHAR(20),
	DeclineReason VARCHAR(50),
	IsFraud INTEGER,
	PRIMARY KEY (TransactionId)
);

CREATE TABLE Finance.Disputes (
	DisputeId BIGINT NOT NULL,
	TransactionId BIGINT,
	OpenedAt VARCHAR(35),
	ResolvedAt VARCHAR(35),
	ReasonCode VARCHAR(50),
	State VARCHAR(30),
	Outcome VARCHAR(40),
	DisputedAmount NUMERIC(18, 2),
	PRIMARY KEY (DisputeId)
);
```

### Sample Queries

```sql
SELECT
	Channel,
	COUNT(*) AS txn_count,
	ROUND(AVG(CASE WHEN Status = 'APPROVED' THEN 1 ELSE 0 END), 4) AS approval_rate,
	ROUND(AVG(CASE WHEN IsFraud = 1 THEN 1 ELSE 0 END), 4) AS fraud_rate
FROM Finance.Transactions
GROUP BY Channel
ORDER BY txn_count DESC;

SELECT
	m.Category,
	m.RiskTier,
	COUNT(*) AS dispute_count,
	ROUND(AVG(d.DisputedAmount), 2) AS avg_disputed_amount
FROM Finance.Disputes d
JOIN Finance.Transactions t ON d.TransactionId = t.TransactionId
JOIN Finance.Merchants m ON t.MerchantId = m.MerchantId
GROUP BY m.Category, m.RiskTier
ORDER BY dispute_count DESC;

SELECT
	c.Segment,
	COUNT(*) AS blocked_card_count
FROM Finance.Cards ca
JOIN Finance.Customers c ON ca.CustomerId = c.CustomerId
WHERE ca.Status = 'BLOCKED'
GROUP BY c.Segment
ORDER BY blocked_card_count DESC;
```

## What The Tables Represent

| Table | What it represents |
| --- | --- |
| `Customers` | The account-holder population. Each customer has a segment, lifecycle status, geographic attributes, and a risk score that affects transaction and dispute behavior. |
| `Accounts` | The lightweight account layer between customers and cards. It adds account type, lifecycle timing, billing-cycle semantics, and autopay behavior without turning the dataset into a full core-banking ledger. |
| `Cards` | Payment cards tied to customer-owned accounts. Cards carry lifecycle fields such as opened/closed timestamps, credit limits, status, and tokenization-style identifiers for card-product demos. |
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

### Accounts

Accounts add a small but important ownership layer between the customer and the card portfolio.

Current account types include:

- `DEPOSIT`
- `REVOLVING_CREDIT`

Current account statuses include:

- `ACTIVE`
- `CLOSED`

Useful interpretation:

- `REVOLVING_CREDIT` accounts are the natural home for billing-cycle and autopay-style demos.
- `DEPOSIT` vs `REVOLVING_CREDIT` gives a more believable portfolio split than linking every card directly to a customer with no account context.
- The current model intentionally keeps one account per customer, which improves realism without expanding into multi-account households or full checking-and-savings modeling.

### Cards

Cards are instruments on top of the account layer rather than standalone accounts. A customer may have multiple cards on the same owning account, and card lifecycle matters for fraud, authorization, and operational demos.

Current card statuses include:

- `ACTIVE`
- `BLOCKED`
- `CLOSED`

Useful interpretation:

- `BLOCKED` supports fraud-operations and card-control demos.
- `CLOSED` supports portfolio attrition and lifecycle views.
- Card-to-account linkage makes it possible to explain instrument-level behavior without losing the owning customer and account context.

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
- The current account layer is intentionally lightweight: one account per customer, no full householding, and no balance ledger.
- Disputes are post-transaction case records, so they are best used for operational and risk analysis rather than accounting close demos.
- Fraud and dispute patterns are intentionally amplified enough to make demos readable; that is useful for presentations, but it should be stated if someone treats the output as production-like class imbalance.
- `DeleteDataset("FinancialServices")` is useful before repeatable demos if you want a clean rerun.
- If you want a short live demo, use a smaller scale factor and focus on one story: fraud, disputes, or merchant risk.
