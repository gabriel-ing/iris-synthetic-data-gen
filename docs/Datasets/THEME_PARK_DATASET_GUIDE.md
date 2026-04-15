# Theme Park Dataset Guide

This guide describes the current Theme Park Management dataset in this repository: what each table represents, how the generated values behave, and the kinds of demos the dataset supports well.

## Overview

The Theme Park domain models a chaotic amusement-park operation with attractions, staffing, maintenance, guests, tickets, queue telemetry, incidents, and post-visit feedback. It is designed for operational-support, triage, scheduling, summarization, and service-recovery demos rather than for full ticketing or safety-system replication.

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
- `queue_snapshot.csv`
- `incidents.csv`
- `feedback.csv`

## Quick SQL Starter

The examples below use simplified DDL that mirrors the core tables in this dataset, followed by a few starter queries for attendance, maintenance, and guest-experience analysis.

### Representative DDL

```sql
CREATE TABLE ThemePark.Parks (
	ParkCode VARCHAR(40) NOT NULL,
	ParkName VARCHAR(120),
	Region VARCHAR(30),
	Country VARCHAR(5),
	ParkType VARCHAR(30),
	OpeningDate TIMESTAMP,
	OperatingModel VARCHAR(40),
	DailyCapacity INTEGER,
	ActiveFlag BOOLEAN,
	PRIMARY KEY (ParkCode)
);

CREATE TABLE ThemePark.Zones (
	ZoneCode VARCHAR(40) NOT NULL,
	ParkCode VARCHAR(40),
	ZoneName VARCHAR(120),
	Theme VARCHAR(60),
	Environment VARCHAR(20),
	FamilyIntensity VARCHAR(20),
	CapacityClass VARCHAR(20),
	IndoorFlag BOOLEAN,
	PRIMARY KEY (ZoneCode)
);

CREATE TABLE ThemePark.Rides (
	RideCode VARCHAR(40) NOT NULL,
	ZoneCode VARCHAR(40),
	RideName VARCHAR(120),
	RideType VARCHAR(30),
	ThrillLevel INTEGER,
	HeightRequirementCm INTEGER,
	CapacityPerHour INTEGER,
	OpeningDate TIMESTAMP,
	AccessibilitySupport VARCHAR(30),
	Status VARCHAR(30),
	PRIMARY KEY (RideCode)
);

CREATE TABLE ThemePark.RideMaintenance (
	MaintenanceNumber VARCHAR(50) NOT NULL,
	RideCode VARCHAR(40),
	ScheduledStart TIMESTAMP,
	ActualStart TIMESTAMP,
	ActualEnd TIMESTAMP,
	MaintenanceType VARCHAR(40),
	Status VARCHAR(30),
	Severity VARCHAR(20),
	DowntimeHours NUMERIC(18, 2),
	IssueSummary VARCHAR(240),
	VendorName VARCHAR(120),
	PRIMARY KEY (MaintenanceNumber)
);

CREATE TABLE ThemePark.Employees (
	EmployeeNumber VARCHAR(40) NOT NULL,
	ParkCode VARCHAR(40),
	HomeZoneCode VARCHAR(40),
	EmployeeName VARCHAR(120),
	RoleType VARCHAR(40),
	SkillTier VARCHAR(20),
	EmploymentType VARCHAR(20),
	HireDate TIMESTAMP,
	MascotQualifiedFlag BOOLEAN,
	ActiveFlag BOOLEAN,
	PRIMARY KEY (EmployeeNumber)
);

CREATE TABLE ThemePark.Shifts (
	ShiftNumber VARCHAR(50) NOT NULL,
	EmployeeNumber VARCHAR(40),
	ParkCode VARCHAR(40),
	ZoneCode VARCHAR(40),
	RideCode VARCHAR(40),
	ShiftStart TIMESTAMP,
	ShiftEnd TIMESTAMP,
	ShiftType VARCHAR(20),
	AssignmentType VARCHAR(30),
	CoverageStatus VARCHAR(30),
	OvertimeFlag BOOLEAN,
	PRIMARY KEY (ShiftNumber)
);

CREATE TABLE ThemePark.Guests (
	GuestNumber VARCHAR(40) NOT NULL,
	HomeCountry VARCHAR(5),
	Segment VARCHAR(30),
	AgeBand VARCHAR(20),
	PartySize INTEGER,
	AccessibilityNeeds VARCHAR(30),
	LoyaltyTier VARCHAR(30),
	VisitIntent VARCHAR(30),
	PRIMARY KEY (GuestNumber)
);

CREATE TABLE ThemePark.Tickets (
	TicketCode VARCHAR(50) NOT NULL,
	GuestNumber VARCHAR(40),
	ParkCode VARCHAR(40),
	VisitDate TIMESTAMP,
	TicketType VARCHAR(30),
	EntryChannel VARCHAR(30),
	PricePaid NUMERIC(18, 2),
	FastAccessFlag BOOLEAN,
	AddOnBundle VARCHAR(40),
	TicketStatus VARCHAR(20),
	PRIMARY KEY (TicketCode)
);

CREATE TABLE ThemePark.Incidents (
	IncidentNumber VARCHAR(50) NOT NULL,
	ParkCode VARCHAR(40),
	ZoneCode VARCHAR(40),
	RideCode VARCHAR(40),
	TicketCode VARCHAR(50),
	EmployeeNumber VARCHAR(40),
	IncidentAt TIMESTAMP,
	IncidentType VARCHAR(40),
	Severity VARCHAR(20),
	Status VARCHAR(30),
	ImpactMinutes INTEGER,
	Description VARCHAR(240),
	ResolutionSummary VARCHAR(240),
	PRIMARY KEY (IncidentNumber)
);

CREATE TABLE ThemePark.Feedback (
	FeedbackNumber VARCHAR(50) NOT NULL,
	TicketCode VARCHAR(50),
	ParkCode VARCHAR(40),
	RideCode VARCHAR(40),
	SubmittedAt TIMESTAMP,
	Channel VARCHAR(30),
	Rating INTEGER,
	Sentiment VARCHAR(20),
	Topic VARCHAR(40),
	Summary VARCHAR(240),
	RequiresFollowUp BOOLEAN,
	PRIMARY KEY (FeedbackNumber)
);
```

### Sample Queries

```sql
SELECT
	ParkCode,
	TicketType,
	COUNT(*) AS ticket_count,
	ROUND(SUM(PricePaid), 2) AS revenue
FROM ThemePark.Tickets
GROUP BY ParkCode, TicketType
ORDER BY revenue DESC;

SELECT
	p.ParkName,
	i.Severity,
	COUNT(*) AS incident_count
FROM ThemePark.Incidents i
JOIN ThemePark.Parks p ON i.ParkCode = p.ParkCode
GROUP BY p.ParkName, i.Severity
ORDER BY incident_count DESC;

SELECT
	r.RideType,
	m.Severity,
	ROUND(SUM(m.DowntimeHours), 2) AS total_downtime_hours
FROM ThemePark.RideMaintenance m
JOIN ThemePark.Rides r ON m.RideCode = r.RideCode
GROUP BY r.RideType, m.Severity
ORDER BY total_downtime_hours DESC;
```

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
| `QueueSnapshot` | A ride-day operational telemetry table estimating wait time, queue length, throughput, fast-access pressure, and closure or delay status. |
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

### Queue Operations

Queue telemetry adds a direct guest-experience operations layer that was previously only implied by incidents and ticket volume.

Current queue snapshot statuses include:

- `OPERATING`
- `DELAYED`
- `CLOSED`

Useful interpretation:

- `QueueSnapshot` rolls up ticket volume, ride capacity, maintenance downtime, and disruption incidents into a dashboard-friendly ride-day view.
- `FastAccessPressure` is useful for premium-access and queue-fairness discussions.
- `ThroughputPerHour`, `WaitMinutes`, and `QueueLength` make the dataset much more practical for live operations and guest-communications demos.

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

- `Tickets`, `QueueSnapshot`, `Rides`, `RideMaintenance`, and `Shifts` give enough demand and capacity signals to support a reasonable operational forecast demo.

## Notes

- The text fields for incidents and feedback are intentionally short and operational rather than narrative-heavy.
- `QueueSnapshot` is a synthetic ride-day operational estimate, not minute-by-minute telemetry from a live queue-management system.
- If you want more bespoke descriptions later, the easiest extension point is the phrase pools in `catalog.py` rather than the schema itself.
- `DeleteDataset("ThemePark")` is useful before repeatable demos if you want a clean rerun.