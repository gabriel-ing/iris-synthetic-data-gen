sops = [
    {
        "sop_id": "SOP-00",
        "name": "Data Dictionary and Allowed Values (Single Source of Truth)",
        "description": (
            "Canonical definitions for all enums and key field semantics (e.g., AuthAt vs PostedAt, "
            "CardPresent meaning), plus join keys and validation guidance. Intended to be retrieved whenever "
            "the agent needs to interpret or validate values."
        ),
        "process_area": "governance",
        "entities": ["customer", "card", "merchant", "transaction", "dispute"],
        "risk_level": "all",
        "related_tables": [
            "ModestExpectationsCaptial.Customers",
            "ModestExpectationsCaptial.Cards",
            "ModestExpectationsCaptial.Merchants",
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Disputes",
        ],
        "key_fields": {
            "Cards.Status": ["ACTIVE", "BLOCKED", "CLOSED"],
            "Merchants.RiskTier": ["LOW", "MED", "HIGH"],
            "Merchants.Category": ["GROCERY", "DIGITAL", "RETAIL", "FUEL", "TRAVEL", "DINING"],
            "Transactions.Channel": ["ECOM", "POS"],
            "Transactions.EntryMode": ["MANUAL", "CHIP", "TAP"],
            "Transactions.Status": ["APPROVED", "DECLINED", "REFUNDED", "REVERSED"],
            "Transactions.DeclineReason": ["INSUFFICIENT_FUNDS", "SUSPECTED_FRAUD", "LIMIT_EXCEEDED", "INVALID_CVV"],
            "Disputes.ReasonCode": ["DUPLICATE", "FRAUD", "NOT_AS_DESCRIBED", "NOT_RECEIVED", "CANCELLED"],
            "Disputes.State": ["OPEN", "UNDER_REVIEW", "RESOLVED"],
            "Disputes.Outcome": ["CUSTOMER_WON", "MERCHANT_WON", "WITHDRAWN", "CHARGEBACK"],
        },
        "allowed_actions": [],
        "required_justifications": ["Reference allowed values when validating or generating updates."],
        "retrieval_tags": ["type:data_dictionary", "must_retrieve:true"],
        "golden_questions": [
            "What does REVERSED mean vs REFUNDED?",
            "What are the allowed values for dispute outcomes and states?"
        ],
    },
    {
        "sop_id": "SOP-01",
        "name": "Customer Risk Posture and Segmentation",
        "description": (
            "How to interpret Customers.RiskScore, Segment, Region, and segment multipliers; defines expected "
            "behavior bands for transaction count/amount/ecom share/declines/disputes and review triggers."
        ),
        "process_area": "risk",
        "entities": ["customer", "transaction"],
        "risk_level": "med",
        "related_tables": [
            "ModestExpectationsCaptial.Customers",
            "ModestExpectationsCaptial.Transactions",
        ],
        "key_fields": [
            "Customers.RiskScore", "Customers.Segment", "Customers.Region",
            "Customers.SegmentTxnMultiplier", "Customers.SegmentAmountMultiplier",
            "Customers.SegmentEcomMultiplier", "Customers.SegmentDeclineMultiplier",
            "Customers.SegmentDisputeMultiplier",
            "Transactions.Amount", "Transactions.Channel", "Transactions.Status",
        ],
        "allowed_actions": ["recommend:monitoring", "recommend:review", "recommend:block_card"],
        "required_justifications": [
            "Cite customer segment and risk score.",
            "Cite observed vs expected behavior using segment multipliers."
        ],
        "retrieval_tags": ["process_area:risk", "entity:customer"],
        "golden_questions": [
            "Is this customer behaving outside their segment profile?",
            "Should we increase monitoring for this customer?"
        ],
    },
    {
        "sop_id": "SOP-02",
        "name": "Card Lifecycle Actions (ACTIVE/BLOCKED/CLOSED)",
        "description": (
            "Permitted card status transitions and when to apply them. Includes decision table for BLOCK vs CLOSE, "
            "and requirements for audit notes and escalation."
        ),
        "process_area": "card_ops",
        "entities": ["card", "customer", "transaction", "dispute"],
        "risk_level": "high",
        "related_tables": [
            "ModestExpectationsCaptial.Cards",
            "ModestExpectationsCaptial.Customers",
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Disputes",
        ],
        "key_fields": [
            "Cards.Status", "Cards.OpenedAt", "Cards.ClosedAt", "Cards.CreditLimit",
            "Transactions.IsFraud", "Transactions.Status", "Transactions.DeclineReason",
            "Disputes.State", "Disputes.Outcome",
        ],
        "allowed_actions": ["write:Cards.Status", "write:Cards.ClosedAt", "recommend:close_card"],
        "required_justifications": [
            "Cite triggering evidence (fraud flags, dispute patterns, velocity).",
            "Explain why BLOCK is sufficient vs why CLOSE is necessary (if used)."
        ],
        "retrieval_tags": ["process_area:card_ops", "actionable:true"],
        "golden_questions": [
            "Should I block this card now?",
            "What evidence do I need to close it?"
        ],
    },
    {
        "sop_id": "SOP-03",
        "name": "Transaction Triage (APPROVED/DECLINED/REFUNDED/REVERSED)",
        "description": (
            "How to interpret transaction statuses operationally, including AuthAt vs PostedAt differences, and how "
            "to respond when PostedAt is missing or delayed."
        ),
        "process_area": "txn_ops",
        "entities": ["transaction", "card", "merchant"],
        "risk_level": "med",
        "related_tables": [
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Cards",
            "ModestExpectationsCaptial.Merchants",
        ],
        "key_fields": [
            "Transactions.Status", "Transactions.AuthAt", "Transactions.PostedAt",
            "Transactions.Amount", "Transactions.Currency",
            "Transactions.Channel", "Transactions.EntryMode", "Transactions.CardPresent",
        ],
        "allowed_actions": ["recommend:refund", "recommend:reverse", "recommend:investigate"],
        "required_justifications": [
            "Cite transaction timeline (AuthAt/PostedAt).",
            "Cite status semantics and why the recommended remediation applies."
        ],
        "retrieval_tags": ["process_area:txn_ops", "entity:transaction"],
        "golden_questions": [
            "Why was this reversed?",
            "Is this refund legitimate?"
        ],
    },
    {
        "sop_id": "SOP-04",
        "name": "Decline Reason Handling and Customer Remediation",
        "description": (
            "Decision tree for decline reasons (INSUFFICIENT_FUNDS, SUSPECTED_FRAUD, LIMIT_EXCEEDED, INVALID_CVV), "
            "including recommended actions and when to block the card or escalate."
        ),
        "process_area": "declines",
        "entities": ["transaction", "card", "customer", "merchant"],
        "risk_level": "med",
        "related_tables": [
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Cards",
            "ModestExpectationsCaptial.Customers",
            "ModestExpectationsCaptial.Merchants",
        ],
        "key_fields": [
            "Transactions.Status", "Transactions.DeclineReason", "Transactions.Amount",
            "Cards.CreditLimit", "Cards.Status",
            "Customers.RiskScore",
            "Merchants.RiskTier",
        ],
        "allowed_actions": ["recommend:customer_steps", "recommend:merchant_steps", "write:Cards.Status"],
        "required_justifications": [
            "Cite decline reason and recent pattern frequency.",
            "If blocking: cite fraud indicators beyond a single decline where possible."
        ],
        "retrieval_tags": ["process_area:declines", "actionable:true"],
        "golden_questions": [
            "What should we do about INVALID_CVV spikes?",
            "Is LIMIT_EXCEEDED a fraud signal here?"
        ],
    },
    {
        "sop_id": "SOP-05",
        "name": "Channel and EntryMode Risk Policy (ECOM/POS; MANUAL/CHIP/TAP)",
        "description": (
            "Risk matrix for Channel x EntryMode x CardPresent, with compensating controls and step-up actions. "
            "Defines high-risk combinations such as ECOM+MANUAL+CardPresent=0."
        ),
        "process_area": "fraud_policy",
        "entities": ["transaction", "merchant", "customer"],
        "risk_level": "high",
        "related_tables": [
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Merchants",
            "ModestExpectationsCaptial.Customers",
        ],
        "key_fields": [
            "Transactions.Channel", "Transactions.EntryMode", "Transactions.CardPresent",
            "Transactions.Amount",
            "Merchants.RiskTier", "Merchants.Category",
            "Customers.RiskScore",
        ],
        "allowed_actions": ["recommend:step_up", "recommend:monitoring", "write:Cards.Status"],
        "required_justifications": [
            "Cite the risk matrix cell (channel/entry/cardpresent).",
            "Cite merchant tier and amount context."
        ],
        "retrieval_tags": ["process_area:fraud_policy", "entity:transaction"],
        "golden_questions": [
            "Is this tap transaction risky?",
            "Why did we block an ecom manual entry?"
        ],
    },
    {
        "sop_id": "SOP-06",
        "name": "Fraud Triage and Containment (Rule-Based)",
        "description": (
            "Investigation playbook for suspected fraud using IsFraud, velocity, out-of-segment behavior, and merchant "
            "risk tier/category patterns. Ends with explicit containment options and escalation criteria."
        ),
        "process_area": "fraud_ops",
        "entities": ["transaction", "card", "customer", "merchant", "dispute"],
        "risk_level": "high",
        "related_tables": [
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Cards",
            "ModestExpectationsCaptial.Customers",
            "ModestExpectationsCaptial.Merchants",
            "ModestExpectationsCaptial.Disputes",
        ],
        "key_fields": [
            "Transactions.IsFraud", "Transactions.AuthAt", "Transactions.Amount",
            "Transactions.Channel", "Transactions.EntryMode", "Transactions.CardPresent",
            "Cards.Status",
            "Merchants.RiskTier", "Merchants.Category",
            "Disputes.ReasonCode", "Disputes.State",
        ],
        "allowed_actions": ["write:Cards.Status", "recommend:escalate", "recommend:monitoring"],
        "required_justifications": [
            "Cite at least two independent indicators (e.g., velocity + high-risk merchant).",
            "Provide an audit narrative summarizing evidence and action."
        ],
        "retrieval_tags": ["process_area:fraud_ops", "actionable:true"],
        "golden_questions": [
            "Should we block immediately?",
            "What’s the evidence that this is fraud vs legitimate activity?"
        ],
    },
    {
        "sop_id": "SOP-07",
        "name": "Velocity and Burst Spending Investigation",
        "description": (
            "How to compute and interpret velocity metrics (txn count/spend per 10m/1h/24h) per CardId and compare "
            "against segment multipliers. Includes false-positive guidance by merchant category."
        ),
        "process_area": "fraud_ops",
        "entities": ["transaction", "card", "customer"],
        "risk_level": "med",
        "related_tables": [
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Cards",
            "ModestExpectationsCaptial.Customers",
        ],
        "key_fields": [
            "Transactions.CardId", "Transactions.AuthAt", "Transactions.Amount",
            "Customers.SegmentTxnMultiplier", "Customers.SegmentAmountMultiplier",
        ],
        "allowed_actions": ["recommend:block_card", "recommend:monitoring"],
        "required_justifications": [
            "Cite the velocity window and counts/amounts.",
            "Compare to expected behavior using segment multipliers."
        ],
        "retrieval_tags": ["process_area:fraud_ops", "technique:velocity"],
        "golden_questions": [
            "Is this burst normal for TRAVEL or FUEL?",
            "Is the customer’s decline multiplier relevant here?"
        ],
    },
    {
        "sop_id": "SOP-08",
        "name": "Merchant Risk Monitoring and Escalation",
        "description": (
            "How to assess whether a merchant is trending risky using dispute rate, fraud rate (IsFraud), and decline "
            "rate, and when to recommend containment or tier adjustments."
        ),
        "process_area": "merchant_risk",
        "entities": ["merchant", "transaction", "dispute"],
        "risk_level": "med",
        "related_tables": [
            "ModestExpectationsCaptial.Merchants",
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Disputes",
        ],
        "key_fields": [
            "Merchants.RiskTier", "Merchants.Category", "Merchants.PopularityWeight",
            "Transactions.Status", "Transactions.DeclineReason", "Transactions.IsFraud",
            "Disputes.State", "Disputes.Outcome",
        ],
        "allowed_actions": ["recommend:containment", "recommend:tier_change", "write:Merchants.RiskTier"],
        "required_justifications": [
            "Cite metric deltas (e.g., dispute rate increasing) and time windows used.",
            "If changing tier: justify with threshold and sample size considerations."
        ],
        "retrieval_tags": ["process_area:merchant_risk", "entity:merchant"],
        "golden_questions": [
            "Is this merchant trending risky?",
            "Should we move them from MED to HIGH?"
        ],
    },
    {
        "sop_id": "SOP-09",
        "name": "Dispute Intake (OPEN/UNDER_REVIEW) and Eligibility",
        "description": (
            "Checks and required fields to open a dispute, set initial state, and map ReasonCode to evidence "
            "expectations. Covers invalid/duplicate dispute scenarios and linkage to transactions."
        ),
        "process_area": "disputes",
        "entities": ["dispute", "transaction", "card", "customer"],
        "risk_level": "med",
        "related_tables": [
            "ModestExpectationsCaptial.Disputes",
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Cards",
            "ModestExpectationsCaptial.Customers",
        ],
        "key_fields": [
            "Disputes.ReasonCode", "Disputes.State", "Disputes.DisputedAmount", "Disputes.OpenedAt",
            "Transactions.TransactionId", "Transactions.Status", "Transactions.Amount",
            "Transactions.Channel", "Transactions.EntryMode", "Transactions.CardPresent",
        ],
        "allowed_actions": ["write:Disputes(insert)", "write:Disputes.State"],
        "required_justifications": [
            "Confirm transaction exists and is eligible.",
            "Cite reason code and required data completeness checks."
        ],
        "retrieval_tags": ["process_area:disputes", "actionable:true"],
        "golden_questions": [
            "Can we open a dispute for this reversed transaction?",
            "What evidence is needed for NOT_RECEIVED?"
        ],
    },
    {
        "sop_id": "SOP-10",
        "name": "Dispute Investigation and Resolution Outcomes",
        "description": (
            "Decision table to resolve disputes and set Outcome (CUSTOMER_WON, MERCHANT_WON, WITHDRAWN, CHARGEBACK). "
            "Incorporates transaction context, card-present/entry mode, and merchant risk tier."
        ),
        "process_area": "disputes",
        "entities": ["dispute", "transaction", "merchant", "customer"],
        "risk_level": "med",
        "related_tables": [
            "ModestExpectationsCaptial.Disputes",
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Merchants",
            "ModestExpectationsCaptial.Customers",
        ],
        "key_fields": [
            "Disputes.State", "Disputes.Outcome", "Disputes.ResolvedAt", "Disputes.ReasonCode",
            "Transactions.Channel", "Transactions.EntryMode", "Transactions.CardPresent",
            "Merchants.RiskTier", "Merchants.Category",
        ],
        "allowed_actions": ["write:Disputes.State", "write:Disputes.Outcome", "write:Disputes.ResolvedAt"],
        "required_justifications": [
            "Cite which decision rule applied and why.",
            "Cite key supporting facts (channel/entry/cardpresent/merchant tier)."
        ],
        "retrieval_tags": ["process_area:disputes", "actionable:true"],
        "golden_questions": [
            "Likely outcome for FRAUD on ECOM MANUAL?",
            "When do we proceed to CHARGEBACK?"
        ],
    },
    {
        "sop_id": "SOP-11",
        "name": "Refunds, Reversals, and Customer Remediation",
        "description": (
            "Rules for when to treat items as REFUNDED vs REVERSED, how these relate to disputes, and when to "
            "recommend refund vs dispute. Includes remediation narrative templates."
        ),
        "process_area": "remediation",
        "entities": ["transaction", "dispute", "customer"],
        "risk_level": "low",
        "related_tables": [
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Disputes",
            "ModestExpectationsCaptial.Customers",
        ],
        "key_fields": [
            "Transactions.Status", "Transactions.Amount", "Transactions.PostedAt",
            "Disputes.State", "Disputes.Outcome",
        ],
        "allowed_actions": ["recommend:refund", "recommend:close_dispute"],
        "required_justifications": [
            "Explain why remediation is appropriate based on status and dispute linkage."
        ],
        "retrieval_tags": ["process_area:remediation"],
        "golden_questions": [
            "Should we refund or dispute?",
            "Why is a dispute open on a refunded transaction?"
        ],
    },
    {
        "sop_id": "SOP-12",
        "name": "Agent Action Policy, Safety Controls, and Audit Logging",
        "description": (
            "Governance for an agent that can write to IRIS: allowed write operations, two-phase (plan then execute), "
            "mandatory audit note format, confidence/threshold requirements, and rollback guidance."
        ),
        "process_area": "governance",
        "entities": ["customer", "card", "merchant", "transaction", "dispute"],
        "risk_level": "all",
        "related_tables": [
            "ModestExpectationsCaptial.Customers",
            "ModestExpectationsCaptial.Cards",
            "ModestExpectationsCaptial.Merchants",
            "ModestExpectationsCaptial.Transactions",
            "ModestExpectationsCaptial.Disputes",
        ],
        "key_fields": [
            "Cards.Status", "Cards.ClosedAt",
            "Merchants.RiskTier",
            "Disputes.State", "Disputes.Outcome", "Disputes.ResolvedAt",
        ],
        "allowed_actions": [
            "write:Cards.Status", "write:Cards.ClosedAt",
            "write:Disputes(insert)", "write:Disputes.State", "write:Disputes.Outcome", "write:Disputes.ResolvedAt",
            "write:Merchants.RiskTier"
        ],
        "required_justifications": [
            "Always produce: plan, evidence (fields+values), intended writes, and audit note.",
            "Never execute destructive changes outside allowlist."
        ],
        "retrieval_tags": ["type:governance", "must_retrieve:true", "actionable:true"],
        "golden_questions": [
            "Are we allowed to close a card automatically?",
            "What must be recorded when we block a card or resolve a dispute?"
        ],
    },
]

