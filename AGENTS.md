# Synthetic Dataset Generation for InterSystems IRIS

Synthetic Financial Services Dataset Generator: Complete Build Plan

This plan is written for a builder agent to implement a configurable, reproducible generator that produces a reasonably realistic relational dataset for storage/retrieval demos (and light analytics exploration), without aiming for statistically faithful training data.
Key requirements captured from our discussion:

Single currency
90-day transaction window
Realistic-looking tables with referential integrity and time-consistent events
Output scales with configurable parameters (N), including a “large scale” mode
Focus on generation first; IRIS loading later


1) Objectives and non-objectives
Objectives

Generate 5 linked tables:

Customers
Cards
Merchants
Transactions
Disputes


Preserve business invariants:

Valid foreign keys
Time ordering (card opened before txn; dispute after txn)
Reasonable distributions (not uniform randomness)


Include demo-friendly edge cases:

Declines, refunds/reversals
Blocked/closed cards
A few high-dispute merchants
A small number of “bursty” cards for velocity/fraud-style demos


Deterministic output:

Same config + seed produces identical dataset


Scalable generation:

Small mode fits in memory
Large mode streams/partitions output without building giant DataFrames



Non-objectives

No real PII, no real PANs. Use tokens or obviously synthetic values.
Not aiming for perfect statistical fidelity, only plausibility.


2) Technology and library choices
Choose a baseline stack that supports both small and large output.
Core generation (recommended)

numpy for deterministic RNG and sampling
pandas for small-mode assembly and CSV writing
pyarrow (Parquet) and/or polars for large-mode streaming writes

Optional “realistic strings”

Faker or mimesis for merchant names and safe synthetic customer labels (if desired)

Keep this optional and disable by default for speed and minimal PII.



Output format

CSV for simplicity and easy DB import
Parquet for large scale and partitioned storage
Support both via config flag


3) Configuration model (N-driven scaling)
You want “generate dataset with N values where N is configurable.” Make this explicit:
Approach A (recommended): explicit table counts
Config includes counts.* directly, so N can mean whatever you want.

Pros: simplest and unambiguous
Cons: user must set 5 numbers

Approach B: single scale factor N with ratios
Config includes:

scale_factor: N
base_counts and multipliers/ratios
Example:
base: Customers=1000, Merchants=500, Cards=1500, Txns=10000, Disputes=200
then multiply all counts by N, with optional caps or derived constraints

I recommend supporting both:

If counts.* present, use them
Else compute counts from scale_factor * base_counts

Minimum config schema
Provide the builder agent this config contract:

```yaml
seed: 42
currency: "GBP"

time:
  start_date: "2026-01-01"
  days: 90
  timezone: "UTC"

scale:
  mode: "explicit"       # "explicit" or "factor"
  factor: 1              # used if mode="factor"
  counts:                # used if mode="explicit"
    customers: 1000
    merchants: 500
    cards: 1500
    transactions: 10000
    disputes: 200

output:
  format: "csv"          # "csv" or "parquet"
  path: "./out"
  partition_transactions_by: "day"   # "day" | "none"
  overwrite: true

behavior:
  segments:
    - name: "STUDENT"
      weight: 0.15
      txn_rate_multiplier: 0.8
      avg_amount_multiplier: 0.7
      ecom_multiplier: 1.4
      decline_multiplier: 1.0
      dispute_multiplier: 1.1
    - name: "MASS"
      weight: 0.50
      txn_rate_multiplier: 1.0
      avg_amount_multiplier: 1.0
      ecom_multiplier: 1.0
      decline_multiplier: 1.0
      dispute_multiplier: 1.0
    - name: "AFFLUENT"
      weight: 0.15
      txn_rate_multiplier: 1.2
      avg_amount_multiplier: 1.6
      ecom_multiplier: 0.9
      decline_multiplier: 0.8
      dispute_multiplier: 0.9
    - name: "HIGHRISK"
      weight: 0.10
      txn_rate_multiplier: 1.0
      avg_amount_multiplier: 1.0
      ecom_multiplier: 1.4
      decline_multiplier: 1.6
      dispute_multiplier: 1.8
    - name: "DORMANT"
      weight: 0.10
      txn_rate_multiplier: 0.1
      avg_amount_multiplier: 0.8
      ecom_multiplier: 1.0
      decline_multiplier: 1.0
      dispute_multiplier: 1.0

  merchants:
    category_weights:
      GROCERY: 0.22
      FUEL: 0.10
      DINING: 0.18
      TRAVEL: 0.08
      RETAIL: 0.30
      DIGITAL: 0.12
    risk_tier_weights:
      LOW: 0.80
      MED: 0.15
      HIGH: 0.05
    popularity_pareto_alpha: 2.0

  transactions:
    base_decline_rate: 0.08
    base_refund_rate: 0.02
    base_ecom_share: 0.20
    weekly_seasonality: true

  disputes:
    target_count: 200
    base_rate: 0.02
    ecom_multiplier: 2.0
    highrisk_customer_multiplier: 2.0
    highrisk_merchant_multiplier: 2.5
    reason_weights:
      FRAUD: 0.40
      NOT_RECEIVED: 0.25
      DUPLICATE: 0.10
      NOT_AS_DESCRIBED: 0.20
      CANCELLED: 0.05
    outcome_weights:
      CUSTOMER_WON: 0.55
      MERCHANT_WON: 0.30
      WITHDRAWN: 0.10
      CHARGEBACK: 0.05

edge_cases:
  enable: true
  customers_with_no_cards: 10
  cards_with_only_declines: 10
  blocked_cards_mid_window: 20
  fraud_bursts:
    count_cards: 8
    txns_per_card: 20
    burst_hours: 2
    amount_range: [1.0, 25.0]
```

4) Data model (tables, keys, minimal columns)
Keep schemas minimal but expressive and joinable.
Customers

CustomerId (PK, integer)
CreatedAt (datetime)
Status (ACTIVE/CLOSED)
Segment (from config)
RiskScore (0–100 integer)
Region (synthetic set)

Cards

CardId (PK)
CustomerId (FK -> Customers)
CardType (DEBIT/CREDIT)
Status (ACTIVE/BLOCKED/CLOSED)
OpenedAt (datetime)
ClosedAt (nullable datetime)
CardToken (string unique, safe)
CreditLimit (nullable/0 for debit)

Merchants

MerchantId (PK)
MerchantName (synthetic)
Category (from config)
RiskTier (LOW/MED/HIGH)
PopularityWeight (float, for sampling)
Country (fixed “GB” unless you later want multi-country)

Transactions

TransactionId (PK; prefer integer for scale)
CardId (FK -> Cards)
MerchantId (FK -> Merchants)
AuthAt (datetime)
PostedAt (datetime)
Amount (decimal)
Currency (fixed)
Channel (POS/ECOM)
EntryMode (CHIP/TAP/MANUAL, optional)
CardPresent (boolean derived from channel)
Status (APPROVED/DECLINED/REFUNDED/REVERSED)
DeclineReason (nullable)
IsFraud (boolean, rare)

Disputes

DisputeId (PK)
TransactionId (FK -> Transactions; unique if 0..1 dispute per txn)
OpenedAt (datetime)
ResolvedAt (nullable)
ReasonCode
State (OPEN/UNDER_REVIEW/RESOLVED)
Outcome (nullable unless RESOLVED)
DisputedAmount (usually equals txn amount; sometimes partial)


5) Generation strategy: order, algorithms, and invariants
Generation order is fixed:

Merchants
Customers
Cards
Transactions (partitioned)
Disputes
Edge cases injection (some can be earlier)

Determinism rules

Use one master seed from config.
Derive sub-seeds per table for stability across changes:

seed_merchants = hash(seed, "merchants"), etc.


Ensure ID generation is deterministic:

Sequential numeric IDs are easiest and fastest for large scale.



5.1 Merchants generation
Algorithm:

Create MerchantId 1..M
Assign Category using config weights
Assign RiskTier using config weights
Assign PopularityWeight from Pareto-like distribution:

w = pareto(alpha) + 1
Normalize to probabilities later when sampling merchants for transactions


Create MerchantName as simple deterministic string unless Faker enabled:

Merchant {id:05d} is fine for demos



Acceptance criteria:

Category distribution roughly matches weights
RiskTier distribution roughly matches weights
Popularity weights not uniform; top 5 percent noticeably heavier

5.2 Customers generation
Algorithm:

Create CustomerId 1..C
Assign Segment by weights
Assign RiskScore

Use segment-influenced distribution:

HIGHRISK shifted higher
AFFLUENT shifted lower




CreatedAt spread over past 3 years before start_date
Status mostly ACTIVE (for realism; small CLOSED)

Acceptance criteria:

Segment distribution roughly matches weights
RiskScore is 0–100, with segment differentiation

5.3 Cards generation
Algorithm:

Create CardId 1..K
Assign each card to a customer using a skewed rule:

Most customers 1 card, some 2, few 3+
Implementation: precompute desired cards per customer then flatten, then truncate/extend to K


OpenedAt spread across last 2 years before start_date
Status distribution:

ACTIVE majority, small BLOCKED, small CLOSED


If CLOSED:

Set ClosedAt after OpenedAt, possibly before start_date or within window depending on desired stories


Generate CardToken as unique safe token:

e.g., tok_{CardId}_{random_suffix}


For CREDIT cards, assign CreditLimit from small set with skew

Invariants:

OpenedAt <= ClosedAt when closed
If status != CLOSED then ClosedAt null

Acceptance criteria:

FK valid
Cards per customer looks plausible (not uniform)

5.4 Transactions generation (90-day window, scalable)
This is the core. Implement it as a streaming/partitioned generator.
Key design choices:

Generate transactions in daily partitions (recommended), or fixed-size chunks (alternative).
Do not build all transactions in memory for large scale.

Algorithm outline per day:

Determine n_txn_today

Default: total_txns / days with remainder
Optional: weekly seasonality multiplier if enabled


Sample cards for today:

Weighted by customer segment activity:

Create card weights derived from customer segment txn_rate_multiplier




Sample merchants for today:

Use merchant popularity weights (normalized)


Assign channel:

Base eCom share, multiplied by segment ecom multiplier and optionally merchant category


Generate amounts:

Choose amount distribution based on merchant category:

Simple approach: category-specific lognormal parameters or min/max with occasional outliers


Multiply by segment avg_amount_multiplier


Decide approval/decline:

Start with base decline rate
Multiply by:

high risk customer
eCom channel
unusually large amount relative to category typical


If DECLINED:

Set DeclineReason from small weighted list (INSUFFICIENT_FUNDS, SUSPECTED_FRAUD, LIMIT_EXCEEDED, INVALID_CVV)




Decide refunds/reversals:

Only for approved transactions
Small probability, biased to eCom and travel categories
Represent as Status = REFUNDED or REVERSED

Keep amount positive; status indicates reversal, or optionally create a separate “refund transaction” table later




Timestamps:

AuthAt randomly within the day
PostedAt = AuthAt + minutes(0..180) for approved; for declined you can set PostedAt = AuthAt or null. Choose one and be consistent.



Outputs:

Write each partition immediately:

CSV: transactions_YYYY-MM-DD.csv
Parquet: transactions/date=YYYY-MM-DD/part-000.parquet



Invariants:

Card must be open at AuthAt (AuthAt >= OpenedAt)
If card closed, AuthAt <= ClosedAt
PostedAt >= AuthAt (if present)

Acceptance criteria:

Exactly total transaction count generated
No orphan FKs
Time constraints satisfied

5.5 Disputes generation (target count, weighted sampling)
Generate disputes after transactions exist.
Algorithm:

Compute dispute probability per transaction:

Start with base rate
Multiply by:

Channel = ECOM multiplier
Customer segment dispute_multiplier
Merchant risk tier multiplier
Category multiplier (optional: travel/digital higher)




Use weighted sampling without replacement until you reach target_count

If probabilities are too low, increase base rate or relax constraints in code automatically


For each selected transaction:

OpenedAt = PostedAt + days(1..45)
State:

Some remain OPEN
Most RESOLVED


If RESOLVED:

ResolvedAt = OpenedAt + days(3..60)
Outcome from weights


DisputedAmount equals Amount most of the time; sometimes partial (e.g., 20 percent of cases)



Invariants:

One dispute per transaction unless you explicitly allow multiple
OpenedAt after PostedAt
ResolvedAt after OpenedAt if present

Acceptance criteria:

Exactly N disputes
All refer to valid transactions
Plausible spread of reasons/outcomes


6) Edge cases injection (demo realism)
Implement these as optional post-processing steps controlled by config. They should be deterministic.
Recommended edge cases:

Customers with no cards:

Choose N customers and ensure no card assigned


Cards with only declines:

Choose N cards; for their transactions, force Status=DECLINED (either by reassigning or generating special transactions)


Blocked cards mid-window:

Pick N cards; set status to BLOCKED with BlockedAt (if you add it) or just set status and ensure later days don’t create approved transactions


Fraud bursts:

Pick N cards; inject txns_per_card small ECOM approved transactions within burst_hours
Optionally mark some as disputed later via higher probability



Acceptance criteria:

Each edge case is present and queryable
Does not break invariants


7) Large-scale strategy (what changes when N is big)
The generation logic should not change. Only execution strategy changes.
Must-have for scale

Chunked generation for Transactions:

Partition by day, or chunks of fixed rows (e.g., 1 million rows per file)


Avoid global joins in memory:

Precompute small lookup arrays:

card weights
merchant sampling probabilities


Use vectorised generation per chunk/day



Output for scale

Prefer Parquet for very large transactions volumes.
Keep dimension tables (customers/cards/merchants) as single files; they’re relatively small.
Partition transactions by date, because your demos will often query “last X days.”


8) Validation and quality checks (mandatory)
Implement a validation module that runs after generation and fails fast.
Integrity checks

Cards.CustomerId exists in Customers
Transactions.CardId exists in Cards
Transactions.MerchantId exists in Merchants
Disputes.TransactionId exists in Transactions
Disputes.TransactionId unique if 0..1 dispute per txn

Temporal checks

Transactions.AuthAt >= Cards.OpenedAt
If card ClosedAt not null: Transactions.AuthAt <= ClosedAt
Transactions.PostedAt >= AuthAt (if posted present)
Disputes.OpenedAt > Transactions.PostedAt
Disputes.ResolvedAt >= OpenedAt (if resolved present)

Count checks

Exactly configured counts per table (especially transactions and disputes)

Simple realism checks (not strict)

Top merchants account for more transactions than the median merchant
Disputes rate higher for ECOM than POS
HIGHRISK segment has higher decline rate than MASS


9) Implementation architecture (what the builder should implement)
Modules

config.py

parse YAML/JSON config
derive counts if scale factor mode


rng.py

deterministic RNG management and sub-seeding


generators/merchants.py
generators/customers.py
generators/cards.py
generators/transactions.py

supports partitioned writing


generators/disputes.py
edge_cases.py
writer.py

CSV and Parquet writers
partition naming scheme


validate.py
main.py

orchestrates generation order and validation



Data interchange conventions

Use numeric IDs for performance
Use ISO 8601 timestamps in CSV
Keep categorical fields as small strings (or integer codes if you want speed)

11) Acceptance criteria (what “done” means)
The builder agent should consider the generator complete when:

It generates all five tables with configurable counts (explicit or via scale factor).
It produces deterministic outputs given the same config and seed.
It can run in:

small mode: outputs single files for each table (transactions optionally one file)
large mode: transactions partitioned by day/chunk, without memory blowups


It passes validation checks listed above.
It includes edge cases controlled by config.
It emits a run summary:

counts per table
decline rate, refund rate, dispute rate
top 10 merchants by txn count
basic timing range stats




12) What I’d push back on (to avoid a fake-looking dataset)
Two common mistakes that make demos look synthetic:

Uniform randomness everywhere (each merchant gets similar traffic, each customer looks identical). You must implement skew via merchant popularity and customer segments.
Ignoring time relationships (disputes before transactions, transactions before card open). Those errors undermine credibility immediately.

This plan bakes both fixes in from the start.