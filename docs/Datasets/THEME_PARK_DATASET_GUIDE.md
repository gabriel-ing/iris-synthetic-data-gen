# Theme Park Dataset Guide

This guide describes the current Theme Park Management dataset in this repository: what each table represents, how the generated values behave, and the kinds of demos the dataset supports well.

## Overview

The Theme Park domain models a chaotic amusement-park operation with attractions, staffing, maintenance, guests, tickets, incidents, and post-visit feedback. It is designed for operational-support, triage, scheduling, summarization, and service-recovery demos rather than for full ticketing or safety-system replication.

Current package and entrypoints:

- IRIS package: `ThemePark`
- Python package root: `src/ThemePark/python/DataGen`
- Lazy-compile sentinel: `ThemePark.Parks`
- Shared IRIS loader call: `do ##class(SyntheticDataGen.DataLoader).LoadData("ThemePark")`

Current generated outputs:

- `parks.csv`
- `zones.csv`
- `rides.csv`
- `ride_maintenance.csv`
- `employees.csv`
- `shifts.csv`
- `guests.csv`
- `tickets.csv`
- `incidents.csv`
- `feedback.csv`

## What The Tables Represent

| Table | What it represents |
| --- | --- |
| `Parks` | Theme-park properties, including region, park type, operating model, and daily capacity. |
| `Zones` | Themed areas inside each park that group rides, staffing, and guest flow. |
| `Rides` | Attractions with ride type, thrill level, accessibility support, capacity, and operating status. |
| `RideMaintenance` | Scheduled and unscheduled maintenance work for rides, including downtime, severity, and vendor details. |
| `Employees` | Park staff with home zone, role, skill tier, hire timing, and mascot qualification. |
| `Shifts` | Individual staffing assignments across parks, zones, and sometimes specific rides. |
| `Guests` | Synthetic visitor profiles with segment, age band, party size, loyalty tier, and accessibility needs. |
| `Tickets` | Visit-level ticket facts including ticket type, entry channel, paid amount, add-ons, and visit status. |
| `Incidents` | Operational and guest-facing incidents such as outages, medical events, queue disruption, and weather delays. |
| `Feedback` | Guest feedback tied to tickets and sometimes rides, with sentiment, topic, rating, and follow-up need. |

## Current Value Semantics

### Parks And Zones

The dataset creates multiple parks with different operating shapes instead of cloning one park many times.

Current park semantics include:

- regions such as `SOUTHEAST`, `WEST`, `MIDWEST`, `NORTHEAST`, and `INTERNATIONAL`
- park types such as `DESTINATION`, `CITY`, `RESORT`, and `WATER`
- operating models such as `YEAR_ROUND`, `EXTENDED_HOURS`, `HOTEL_INTEGRATED`, and `SEASONAL_PEAK`

Useful interpretation:

- `DESTINATION` and `RESORT` parks support higher-traffic, higher-complexity ops stories.
- `WATER` parks are useful for seasonal and weather-sensitive examples.
- zone themes give the dataset a more natural operational grouping than a flat ride list.

### Rides And Maintenance

Rides are the core operational asset in the domain.

Current ride types include:

- `COASTER`
- `DARK_RIDE`
- `DROP_TOWER`
- `FAMILY_FLAT`
- `LOG_FLUME`
- `SIMULATOR`
- `WATER_RIDE`

Current ride status vocabulary includes:

- `OPERATING`
- `SEASONAL`
- `STANDBY`
- `LIMITED_HOURS`

Current maintenance types include:

- `INSPECTION`
- `EMERGENCY_REPAIR`
- `COSMETIC`
- `SENSOR_CALIBRATION`
- `RESTRAINT_TEST`

Useful interpretation:

- ride capacity, thrill level, and accessibility support make the tables usable for planning and guest-assistance stories.
- maintenance rows include both planned and active work, so outage and downtime demos do not rely on incidents alone.
- vendor names are included for third-party maintenance escalation stories.

### Employees And Shifts

The staffing model is lightweight but strong enough for scheduling and coverage demos.

Current role vocabulary includes:

- `RIDE_OPERATOR`
- `MECHANIC`
- `GUEST_SERVICES`
- `SAFETY_COORDINATOR`
- `ENTERTAINMENT_HOST`
- `AREA_SUPERVISOR`

Current shift semantics include:

- shift blocks such as `OPEN`, `MID`, `CLOSE`, and `OVERNIGHT`
- coverage statuses such as `STAFFED`, `CALL_OUT_COVERED`, `REDEPLOYED`, and `SHORT_HANDED`
- assignment types such as `RIDE_OPS`, `MAINTENANCE`, `GUEST_EXPERIENCE`, `SAFETY`, `PARADE`, and `SUPERVISION`

Useful interpretation:

- `SHORT_HANDED` shifts are useful for staffing-assistant and redeployment workflows.
- mascot-qualified employees support entertainment and costume-related operations examples.
- home-zone plus park assignment keeps the staffing model coherent enough for operational filtering.

### Guests And Tickets

The guest and ticket tables give the domain a realistic service layer rather than only asset operations.

Current guest segments include:

- `FAMILY`
- `THRILL_SEEKER`
- `TOUR_GROUP`
- `LOCAL_MEMBER`
- `SCHOOL_TRIP`
- `VIP_TRAVELER`

Current ticket types include:

- `DAY_PASS`
- `MULTI_DAY`
- `ANNUAL_PASS`
- `FAST_ACCESS`
- `VIP`

Current channel vocabulary includes:

- `MOBILE_APP`
- `WEBSITE`
- `ON_SITE`
- `HOTEL_DESK`
- `TRAVEL_AGENT`

Useful interpretation:

- loyalty tier, party size, and accessibility needs help support guest-service personalization demos.
- fast-access flags and add-on bundles make premium-service analysis possible.
- ticket statuses such as `USED`, `CANCELLED`, `NO_SHOW`, and `UPGRADED` support basic journey-state analysis.

### Incidents And Feedback

This is where the domain becomes especially useful for AI workflows.

Current incident types include:

- `RIDE_OUTAGE`
- `GUEST_MEDICAL`
- `LOST_CHILD`
- `WEATHER_DELAY`
- `QUEUE_DISRUPTION`
- `COSTUME_MALFUNCTION`
- `SECURITY_ESCALATION`
- `FOOD_SPILL`

Current severity vocabulary includes:

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

Current feedback topics include:

- `WAIT_TIME`
- `STAFF_FRIENDLINESS`
- `RIDE_DOWNTIME`
- `CLEANLINESS`
- `VALUE`
- `ACCESSIBILITY`
- `MASCOT_EXPERIENCE`
- `FOOD_SERVICE`

Useful interpretation:

- incidents are intentionally broad enough to support support-bot, triage, and summarization workflows.
- feedback is linked to both operational pain points and service quality, which makes complaint-routing demos straightforward.
- description and summary text currently comes from curated phrase pools in `src/ThemePark/python/DataGen/generators/catalog.py`, so expanding the text variety later does not require schema changes.

## Time And Scale Behavior

Useful current behavior:

- Default sample horizon is 120 days.
- Runtime scale-factor overrides are supported through the CLI and through `DataLoader.LoadData(...)`.
- Ride outages are deliberately common enough to support outage-triage examples.
- Negative feedback and follow-up flags are explicit generator concepts rather than accidental side effects.
- Shift coverage pressure and overtime are both modeled directly.

## Suggested Demo Projects

### 1. Ride Outage Incident Bot

Focus on:

- classifying outage incidents by severity
- summarizing likely impact to guests and park operations
- routing high-severity cases to maintenance or safety teams

Why it works:

- `Incidents`, `RideMaintenance`, `Rides`, and `Shifts` form a coherent operational triage loop.

### 2. Guest Complaint Triage

Focus on:

- prioritizing negative feedback
- routing issues by topic
- identifying complaints tied to outages, accessibility, or value concerns

Why it works:

- `Feedback` includes sentiment, rating, topic, summary text, and an explicit follow-up signal.

### 3. Staffing Assistant

Focus on:

- identifying short-handed zones
- finding eligible staff for redeployment
- spotting overtime pressure by park and shift block

Why it works:

- `Employees` and `Shifts` include role, skill tier, home zone, assignment type, and coverage status.

### 4. Daily Ops Summary

Focus on:

- summarizing incidents, maintenance, and guest feedback by park
- spotting which zones are under the most stress
- generating handoff notes between operations leaders

Why it works:

- the domain has both structured metrics and short text fields, so it fits summarization well.

### 5. Forecasting And Capacity Demo

Focus on:

- guest volume by park and ticket type
- likely ride pressure by zone and attraction type
- maintenance and staffing load over time

Why it works:

- `Tickets`, `Rides`, `RideMaintenance`, and `Shifts` give enough demand and capacity signals to support a reasonable operational forecast demo.

## Notes

- The text fields for incidents and feedback are intentionally short and operational rather than narrative-heavy.
- If you want more bespoke descriptions later, the easiest extension point is the phrase pools in `catalog.py` rather than the schema itself.
- `DeleteDataset("ThemePark")` is useful before repeatable demos if you want a clean rerun.