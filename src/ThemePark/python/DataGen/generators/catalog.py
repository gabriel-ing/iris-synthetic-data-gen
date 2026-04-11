from __future__ import annotations

ZONE_THEMES: list[dict[str, str]] = [
    {"theme": "ADVENTURE_HARBOR", "environment": "OUTDOOR", "intensity": "BALANCED"},
    {"theme": "COSMIC_BOARDWALK", "environment": "OUTDOOR", "intensity": "HIGH"},
    {"theme": "DINOSAUR_VALLEY", "environment": "HYBRID", "intensity": "FAMILY"},
    {"theme": "ENCHANTED_GARDENS", "environment": "OUTDOOR", "intensity": "LOW"},
    {"theme": "FOUNDERS_PLAZA", "environment": "HYBRID", "intensity": "LOW"},
    {"theme": "LAGOON_LIGHTS", "environment": "OUTDOOR", "intensity": "BALANCED"},
    {"theme": "PIXEL_PORT", "environment": "INDOOR", "intensity": "BALANCED"},
    {"theme": "ROARING_CANYON", "environment": "OUTDOOR", "intensity": "HIGH"},
    {"theme": "SKYLINE_STATION", "environment": "INDOOR", "intensity": "FAMILY"},
    {"theme": "STORYBOOK_COMMONS", "environment": "HYBRID", "intensity": "LOW"},
    {"theme": "SUNBURST_SHORES", "environment": "OUTDOOR", "intensity": "FAMILY"},
    {"theme": "VOLT_WORKS", "environment": "INDOOR", "intensity": "HIGH"},
]

RIDE_TYPE_DEFINITIONS: dict[str, dict[str, object]] = {
    "COASTER": {
        "thrill_levels": [4, 5],
        "height_range": (122, 140),
        "capacity_range": (900, 1800),
        "supports": ["PARTIAL", "LIMITED", "STANDARD"],
        "name_parts": (["Comet", "Iron", "Thunder", "Velocity", "Vortex"], ["Run", "Rush", "Drop", "Spiral", "Strike"]),
    },
    "DARK_RIDE": {
        "thrill_levels": [1, 2, 3],
        "height_range": (0, 102),
        "capacity_range": (700, 1500),
        "supports": ["STANDARD", "ENHANCED"],
        "name_parts": (["Mystic", "Midnight", "Phantom", "Starlight", "Whisper"], ["Voyage", "Expedition", "Cavern", "Chronicle", "Drift"]),
    },
    "DROP_TOWER": {
        "thrill_levels": [4, 5],
        "height_range": (122, 137),
        "capacity_range": (350, 720),
        "supports": ["PARTIAL", "STANDARD"],
        "name_parts": (["Sky", "Pulse", "Apex", "Gravity", "Summit"], ["Fall", "Tumble", "Plunge", "Drop", "Launch"]),
    },
    "FAMILY_FLAT": {
        "thrill_levels": [1, 2],
        "height_range": (0, 107),
        "capacity_range": (500, 1100),
        "supports": ["ENHANCED", "STANDARD"],
        "name_parts": (["Carousel", "Harbor", "Cloud", "Lantern", "Festival"], ["Spin", "Parade", "Swing", "Dash", "Flight"]),
    },
    "LOG_FLUME": {
        "thrill_levels": [2, 3],
        "height_range": (97, 122),
        "capacity_range": (650, 1200),
        "supports": ["STANDARD", "ENHANCED"],
        "name_parts": (["River", "Timber", "Canyon", "Splash", "Tidal"], ["Falls", "Current", "Plunge", "Run", "Rapids"]),
    },
    "SIMULATOR": {
        "thrill_levels": [2, 3, 4],
        "height_range": (97, 122),
        "capacity_range": (550, 1350),
        "supports": ["STANDARD", "ENHANCED"],
        "name_parts": (["Orbit", "Nova", "Portal", "Quantum", "Echo"], ["Mission", "Drive", "Jump", "Rescue", "Journey"]),
    },
    "WATER_RIDE": {
        "thrill_levels": [2, 3, 4],
        "height_range": (107, 127),
        "capacity_range": (600, 1300),
        "supports": ["PARTIAL", "STANDARD"],
        "name_parts": (["Lagoon", "Breaker", "Wave", "Coral", "Neptune"], ["Chase", "Slide", "Surge", "Sprint", "Quest"]),
    },
}

ROLE_DEFINITIONS: list[dict[str, object]] = [
    {"role": "RIDE_OPERATOR", "assignment": "RIDE_OPS", "skill_tiers": ["FOUNDATION", "LEAD"], "ride_eligible": True, "mascot_share": 0.0},
    {"role": "MECHANIC", "assignment": "MAINTENANCE", "skill_tiers": ["CERTIFIED", "SPECIALIST", "LEAD"], "ride_eligible": True, "mascot_share": 0.0},
    {"role": "GUEST_SERVICES", "assignment": "GUEST_EXPERIENCE", "skill_tiers": ["FOUNDATION", "CERTIFIED", "LEAD"], "ride_eligible": False, "mascot_share": 0.08},
    {"role": "SAFETY_COORDINATOR", "assignment": "SAFETY", "skill_tiers": ["CERTIFIED", "SPECIALIST", "LEAD"], "ride_eligible": True, "mascot_share": 0.0},
    {"role": "ENTERTAINMENT_HOST", "assignment": "PARADE", "skill_tiers": ["FOUNDATION", "CERTIFIED"], "ride_eligible": False, "mascot_share": 0.38},
    {"role": "AREA_SUPERVISOR", "assignment": "SUPERVISION", "skill_tiers": ["LEAD", "MANAGER"], "ride_eligible": False, "mascot_share": 0.02},
]

INCIDENT_DESCRIPTIONS: dict[str, list[str]] = {
    "RIDE_OUTAGE": [
        "ride dispatch paused after restraint sensor mismatch",
        "vehicle cycle stopped for repeated lap-bar fault signal",
        "ride control panel triggered a protective shutdown during load",
    ],
    "GUEST_MEDICAL": [
        "guest reported dizziness while exiting the attraction",
        "queue guest requested assistance after heat-related fatigue",
        "minor first-aid event reported near the attraction exit",
    ],
    "LOST_CHILD": [
        "party separation reported near the character greeting area",
        "child location support requested after queue handoff confusion",
        "guardian reported missing child near a parade crossover point",
    ],
    "WEATHER_DELAY": [
        "ride suspended after lightning alert reached the park perimeter",
        "operations paused because wind gusts exceeded operating limits",
        "storm band forced temporary outdoor attraction shutdown",
    ],
    "QUEUE_DISRUPTION": [
        "queue line stalled after merge-point crowding increased wait times",
        "guest flow backed up near accessibility entrance and dispatch lane",
        "boarding lane disruption caused temporary hold at the platform",
    ],
    "COSTUME_MALFUNCTION": [
        "mascot costume cooling unit failed during outdoor appearance",
        "character performer requested backstage relief after visibility issue",
        "costume zipper failure interrupted the scheduled meet-and-greet",
    ],
    "SECURITY_ESCALATION": [
        "guest behavior required supervisor and security response",
        "restricted-area access attempt triggered a localized security hold",
        "bag-screening disagreement escalated at the zone entry point",
    ],
    "FOOD_SPILL": [
        "walkway cleanup required after beverage spill near ride exit",
        "food cart overflow caused temporary slip-hazard closure",
        "condiment spill prompted rapid response from custodial crew",
    ],
}

INCIDENT_RESOLUTIONS: dict[str, list[str]] = {
    "RIDE_OUTAGE": [
        "maintenance reset the affected train and completed a test cycle",
        "ride reopened after sensor calibration and supervisor sign-off",
        "ops transferred guests to alternate attractions with recovery passes",
    ],
    "GUEST_MEDICAL": [
        "first-aid team completed assessment and escorted the guest to rest area",
        "medical response closed the incident after hydration and observation",
        "guest party received follow-up support and relocation assistance",
    ],
    "LOST_CHILD": [
        "child was reunited with party after radio-assisted zone sweep",
        "guest relations completed identity verification and family reunification",
        "the park-wide locate protocol resolved the incident within minutes",
    ],
    "WEATHER_DELAY": [
        "operations resumed after the weather window cleared and all checks passed",
        "park operations delayed reopening until wind readings normalized",
        "affected guests received recovery entitlements during the delay window",
    ],
    "QUEUE_DISRUPTION": [
        "staff rerouted the queue and restored dispatch rhythm",
        "extra attendants reopened the merge lane and stabilized throughput",
        "queue control adjustments cleared the bottleneck",
    ],
    "COSTUME_MALFUNCTION": [
        "costuming swapped the performer into a backup suit and resumed appearances",
        "entertainment leadership moved the greeting indoors and completed the set",
        "the appearance was rescheduled and affected guests received digital recovery cards",
    ],
    "SECURITY_ESCALATION": [
        "security resolved the situation and released the area back to operations",
        "supervisor intervention de-escalated the guest interaction without further disruption",
        "the incident was documented and the zone reopened after clearance",
    ],
    "FOOD_SPILL": [
        "custodial staff sanitized the area and reopened the walkway",
        "the spill response team cleared the hazard and restored access",
        "temporary routing was removed after cleanup inspection",
    ],
}

FEEDBACK_SNIPPETS: dict[str, dict[str, list[str]]] = {
    "WAIT_TIME": {
        "positive": [
            "virtual queue timing was clearer than expected",
            "posted wait times stayed close to the actual experience",
            "staff kept the line moving and communicated well",
        ],
        "negative": [
            "wait time information changed too often in the app",
            "the queue moved slowly and updates were inconsistent",
            "line management felt confusing during the busiest hour",
        ],
    },
    "STAFF_FRIENDLINESS": {
        "positive": [
            "staff handled questions quickly and stayed upbeat",
            "operators were calm, friendly, and clear with instructions",
            "guest services solved a problem without a long escalation",
        ],
        "negative": [
            "the response at the counter felt rushed and impersonal",
            "staff instructions were inconsistent at the ride entrance",
            "it took too long to find someone who could help",
        ],
    },
    "RIDE_DOWNTIME": {
        "positive": [
            "the team explained the delay clearly and offered alternatives",
            "staff kept the downtime announcement short and well managed",
            "recovery options made the outage less frustrating",
        ],
        "negative": [
            "the ride went down with very little communication",
            "multiple closures made the headline attraction hard to enjoy",
            "downtime disrupted the visit more than expected",
        ],
    },
    "CLEANLINESS": {
        "positive": [
            "restrooms and public walkways stayed clean all day",
            "the park looked polished even during the afternoon rush",
            "cleanup crews were visible without getting in the way",
        ],
        "negative": [
            "tables and walkways stayed messy during peak lunch time",
            "restroom upkeep fell behind the crowd volume",
            "trash overflow was noticeable in one of the busiest zones",
        ],
    },
    "VALUE": {
        "positive": [
            "the ticket felt worth it once the add-ons were used",
            "the mix of rides and entertainment justified the price",
            "mobile offers made the day feel better priced",
        ],
        "negative": [
            "the experience felt expensive once extras were added",
            "premium access pricing was hard to justify",
            "food and add-ons pushed the visit above expectations",
        ],
    },
    "ACCESSIBILITY": {
        "positive": [
            "accessibility staff explained the process clearly and respectfully",
            "alternate entrance handling was smooth and well staffed",
            "support options made the visit much easier to manage",
        ],
        "negative": [
            "accessibility steps changed between attractions",
            "the process required too many separate explanations",
            "support was available but not communicated clearly enough",
        ],
    },
    "MASCOT_EXPERIENCE": {
        "positive": [
            "the character interaction felt organized and memorable",
            "mascot timing and photo flow worked really well",
            "the entertainment team kept the atmosphere lively",
        ],
        "negative": [
            "the mascot set ended abruptly and confused guests nearby",
            "photo timing around the character greeting felt rushed",
            "the entertainment lineup was harder to find than expected",
        ],
    },
    "FOOD_SERVICE": {
        "positive": [
            "mobile ordering pickup was faster than expected",
            "food service stayed efficient even during a busy window",
            "the dining team handled dietary questions well",
        ],
        "negative": [
            "food pickup lagged behind the quoted collection time",
            "the dining line and order handoff felt disorganized",
            "menu communication around allergens could be clearer",
        ],
    },
}
