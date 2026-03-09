Supply Chain Demo Dataset Specification (Retail + Distribution) for IRIS Class-First Model
This is the complete, class-first specification for a realistic retail/distribution dataset in InterSystems IRIS, designed to support IRIS implicit joins using -> by modelling relationships as object references. No CREATE TABLE DDL is included; each “table” is a custom persistent class.
Assumptions (explicit so your builder agent can implement deterministically)

Inventory is held at DCs and optionally at Stores (enabled by DimLocation.LocationType).
Dates in transactional tables are references to DimDate to maximise -> usage.
InventoryMovement.Qty is signed (positive increases stock, negative decreases stock).
Surrogate %ID is used as the storage identity; “business keys” are enforced via unique indexes.

If any of those assumptions are wrong, change them now because they affect both realism and generator complexity.

1) Naming, Modelling, and IRIS Requirements
1.1 Naming

Table/class names: PascalCase (example: SalesOrderLine, InventorySnapshotDaily).
Property names: PascalCase (example: OrderDate, ShipFromLocation).
Avoid underscores in identifiers.

1.2 Persistence and implicit join ->
To enable Alias->ReferenceProperty->Field in IRIS SQL:

Each entity is a persistent class (typically extends %Persistent).
Relationships are object references, not integer foreign keys (example: Property Product As DimProduct;).
Transaction classes store references to dimension classes (Product, Location, Supplier, Customer, Date).

1.3 Keys and uniqueness

Use %ID as the primary identity for all classes.
Define unique indexes for natural keys and business identifiers to keep the dataset stable and queryable:

DimProduct.Sku
DimLocation.LocationCode
For line tables, uniqueness on (OrderId, LineNumber) patterns.



1.4 Referential integrity policy

All reference properties in transactional tables are required unless explicitly marked nullable.
Null references are allowed only where business reality warrants it:

InventoryMovement.FromLocation can be null for initial stocking adjustments.
InventoryMovement.ToLocation can be null for write-offs.
ShipmentLine.SalesOrderLine can be null if you later model transfers not tied to sales.




2) Core Entities (Classes) and Their Specifications
The following set is intended to be “robust but not ERP-level”, while still realistic.
Core dimensions

DimDate
DimProduct
DimLocation
DimSupplier
DimCustomer

Core relationship bridge

ProductSupplier

Core transactions

PurchaseOrderLine
SalesOrderLine
ShipmentLine
InventoryMovement

Core performance snapshot (strongly recommended)

InventorySnapshotDaily

If you must keep physical tables minimal, InventorySnapshotDaily can be derived from InventoryMovement, but hackathon teams typically benefit from having it materialised.

3) Class Specifications (Properties, References, Indexes, Notes)
For each class below:

“References” are object references used for -> in SQL.
“Indexes” are what you should define to support performance and uniqueness.
“Notes” highlight realism and generator implications.

3.1 DimDate
Purpose: time dimension enabling -> traversal for calendar logic and seasonality.
Properties

DateKey (unique integer, e.g., 20260306)
CalendarDate (date)
Year, Quarter, Month, WeekOfYear, DayOfWeek
IsWeekend (boolean)
Optional: IsHoliday, HolidayName, FiscalYear, FiscalPeriod

Indexes

Unique: DateKey
Non-unique: CalendarDate, YearMonth (optional derived), WeekOfYear

Notes

Generate this first for the full horizon (recommended 18–24 months daily).


3.2 DimProduct
Purpose: SKU master data.
Properties

Natural key:

Sku (string, unique)


Descriptive:

ProductName, Brand, Category, Subcategory


Units and handling:

Uom (EA/CASE/KG)
UnitsPerCase (integer, nullable if not used)
UnitWeightKg, UnitVolumeM3
TemperatureZone (Ambient/Chilled/Frozen)
IsPerishable (boolean), ShelfLifeDays (nullable when not perishable)


Financial:

StandardCost (decimal)
ListPrice (decimal)


Lifecycle:

LaunchDate (reference to DimDate, optional)
DiscontinueDate (reference to DimDate, optional)



References

LaunchDate -> DimDate (optional)
DiscontinueDate -> DimDate (optional)

Indexes

Unique: Sku
Non-unique: Category, Brand, TemperatureZone, IsPerishable

Notes

Include multiple categories with different behaviours (fast movers, seasonal, bulky, perishable) to create interesting downstream analysis.


3.3 DimLocation
Purpose: all physical nodes (DCs, Stores, Customer sites, Supplier sites).
Properties

Natural key:

LocationCode (string, unique)


Descriptive:

LocationName
LocationType (Dc/Store/CustomerSite/SupplierSite)


Geography:

Country, Region, City, Postcode
Optional: Latitude, Longitude


Operational:

TimeZone
Optional: CapacityPallets, IsActive



Indexes

Unique: LocationCode
Non-unique: LocationType, Region, Country, IsActive

Notes

If you want realistic shipping times and lane analysis, include geo coordinates or at least region groupings.


3.4 DimSupplier
Purpose: supplier master.
Properties

SupplierCode (optional natural key, unique if present)
SupplierName
SupplierTier (1/2/3)
Country
PreferredFlag (boolean)
PaymentTermsDays (integer)
Optional: RiskScore (0–100), SustainabilityRating

References

DefaultShipFromLocation -> DimLocation (optional but recommended)

Indexes

Unique: SupplierCode (if used)
Non-unique: SupplierTier, Country, PreferredFlag

Notes

If you don’t include supplier-specific behaviour (lead time distributions, disruption rates), supplier analytics will be flat and unrealistic.


3.5 DimCustomer
Purpose: customer master (for B2C or B2B) and segmentation.
Properties

CustomerNumber (optional natural key)
CustomerName
CustomerType (Consumer/B2B)
Segment (Value/Standard/Premium or B2B segment)
Country, Region
Optional: ServiceLevelTargetPct

References

Optional: DefaultShipToLocation -> DimLocation (useful if you model customer sites explicitly)

Indexes

Unique: CustomerNumber (if used)
Non-unique: CustomerType, Segment, Region

Notes

If you don’t actually need individual consumers, you can model “customer groups” instead to keep volumes manageable. But you said you want broad re-use, so keeping customers is valuable.


4) Relationship and Policy Classes
4.1 ProductSupplier
Purpose: allowed sourcing combinations and planned lead time/cost. This is critical for believable purchasing.
References

Product -> DimProduct (required)
Supplier -> DimSupplier (required)

Properties

IsPrimarySupplier (boolean)
Ordering constraints:

MinOrderQty
OrderMultipleQty
PackSize (optional; can be derived from UnitsPerCase)


Planning parameters:

PlannedLeadTimeDays (integer)
UnitPurchaseCost (decimal)


Optional logistics:

Incoterm
ShipMode (Ocean/Air/Road)



Indexes

Unique: (Product, Supplier)
Non-unique: Supplier, Product, IsPrimarySupplier

Notes

If you skip this class, POs become random and you lose realistic constraints (MOQ, multiples, lead time expectations).


5) Transaction Classes
5.1 PurchaseOrderLine
Purpose: inbound purchasing, line-level. Header is represented by PurchaseOrderId.
Business identifiers

PurchaseOrderId (string/int)
LineNumber (integer)

References

Supplier -> DimSupplier
Product -> DimProduct
ShipFromLocation -> DimLocation (optional but recommended)
DeliverToLocation -> DimLocation (required; typically a DC)
OrderDate -> DimDate
ExpectedReceiptDate -> DimDate
ReceiptDate -> DimDate (nullable)

Properties

Quantities:

OrderedQty
ReceivedQty (0 until received; may be partial)


Financial:

UnitPurchaseCost


Status:

Status (Open/PartReceived/Closed/Cancelled)
CancelReason (nullable)


Optional derived/stored:

PlannedLeadTimeDays (from ProductSupplier at order time)
ActualLeadTimeDays (when received)



Indexes

Unique: (PurchaseOrderId, LineNumber)
Non-unique: Supplier, DeliverToLocation, OrderDate, Status

Notes

Make partial receipts common enough to be realistic (but not so common that the data becomes noisy and frustrating).


5.2 SalesOrderLine
Purpose: demand, order promising, backorders.
Business identifiers

SalesOrderId
LineNumber

References

Customer -> DimCustomer
Product -> DimProduct
ShipFromLocation -> DimLocation (usually a DC)
ShipToLocation -> DimLocation (store or customer site)
OrderDate -> DimDate
RequestedShipDate -> DimDate
PromisedDeliveryDate -> DimDate
ActualDeliveryDate -> DimDate (nullable until delivered)

Properties

Quantities:

OrderedQty
AllocatedQty (what inventory is reserved)
ShippedQty
BackorderedQty (OrderedQty - ShippedQty when not fully shipped)


Pricing:

UnitSellPrice
Optional: DiscountPct, NetUnitPrice (if you want fewer calculations)


Status and channel:

Status (Open/PartShipped/Shipped/Delivered/Cancelled)
Channel (Store/Ecomm/B2B)



Indexes

Unique: (SalesOrderId, LineNumber)
Non-unique: Customer, ShipFromLocation, OrderDate, Channel, Status

Notes

If you don’t model allocation/backorder, you’ll struggle to create realistic service-level problems and inventory pressure.


5.3 ShipmentLine
Purpose: physical shipments (often 1..n per SalesOrderLine). Enables lane, carrier, transit analytics.
Business identifiers

ShipmentId
LineNumber

References

SalesOrderLine -> SalesOrderLine (nullable only if modelling transfers)
Product -> DimProduct
OriginLocation -> DimLocation
DestinationLocation -> DimLocation
ShipDate -> DimDate
DeliveryDate -> DimDate (nullable until delivered)

Properties

ShippedQty
Carrier:

CarrierName (string) or reference to optional DimCarrier
ServiceLevel (Ground/Express/etc.)


Transit performance:

PlannedTransitDays
ActualTransitDays (optional; can be derived)


Cost and status:

FreightCost
ShipmentStatus (Created/InTransit/Delivered/Delayed/Lost)
DelayReason (nullable)



Indexes

Non-unique: ShipmentId, ShipDate, OriginLocation, DestinationLocation, ShipmentStatus
Non-unique: SalesOrderLine (important for tracing)

Notes

If you want realism, allow split shipments: a single SalesOrderLine can map to multiple ShipmentLines with different ship dates.


5.4 InventoryMovement
Purpose: the stock ledger. This is the single most important table for realism.
References

Product -> DimProduct
FromLocation -> DimLocation (nullable)
ToLocation -> DimLocation (nullable)
MovementDate -> DimDate

Properties

MovementTimestamp (timestamp; optional but adds realism)
MovementType (Receipt/Ship/Transfer/Adjustment/StockCount)
ReferenceType (PurchaseOrder/SalesOrder/Shipment/Transfer/Adjustment)
ReferenceId (string/int; points to the business identifier)
Qty (signed decimal/integer)
UnitCost (decimal; optional for some movement types)
Optional: ReasonCode (Damage/Shrink/Expiry/SystemCorrection)

Indexes

Non-unique: (Product, MovementDate)
Non-unique: (FromLocation, MovementDate)
Non-unique: (ToLocation, MovementDate)
Non-unique: (ReferenceType, ReferenceId)

Notes

Your generator must prevent massive negative inventory unless you intentionally want an “ERP integrity issues” theme.
If you include perishable goods, you can introduce expiry write-offs as Adjustment movements.


6) Snapshot / Derived Class
6.1 InventorySnapshotDaily
Purpose: makes consumption easy for hackathon teams, supports fast dashboards, avoids heavy movement aggregation.
References

SnapshotDate -> DimDate
Product -> DimProduct
Location -> DimLocation

Properties

OnHandQty
AllocatedQty
AvailableQty (OnHandQty - AllocatedQty; can be stored or derived)
InTransitQty
SafetyStockQty
OnOrderQty (open POs not yet received)
Optional: InventoryValue

Indexes

Unique: (SnapshotDate, Product, Location)
Non-unique: (Location, SnapshotDate)
Non-unique: (Product, SnapshotDate)

Notes

Decide whether this is strictly consistent with movements or “close enough with minor discrepancies”. Minor discrepancies are realistic if you also model stock counts and shrink.


7) Optional Extension Classes (Add if you want more realism and re-use value)
If you want maximum hackathon value, add at least one of these. Otherwise the dataset risks feeling “sterile”.
7.1 PricePromotion
Purpose: promotion and price variation for demand spikes and margin analytics.
References

Product -> DimProduct
Optional: Location -> DimLocation (for store-specific promos)
StartDate -> DimDate
EndDate -> DimDate

Properties

PromoType (Discount/BOGO/Feature)
DiscountPct or PromoPrice
Optional: ExpectedLiftPct

Indexes

Non-unique: (Product, StartDate), (Location, StartDate)

7.2 ReturnLine
Purpose: reverse logistics, customer satisfaction, defect analysis.
References

SalesOrderLine -> SalesOrderLine (optional)
Customer -> DimCustomer
Product -> DimProduct
ReturnDate -> DimDate
Optional: ReturnToLocation -> DimLocation

Properties

ReturnQty
ReturnReason (Damaged/NotWanted/Defective/Late)
Disposition (Restock/Scrap/Refurbish)

7.3 StockCountEvent
Purpose: introduces shrink and reconciliation.
References

Location -> DimLocation
Product -> DimProduct
CountDate -> DimDate

Properties

SystemQty
CountedQty
VarianceQty
VarianceReason (Shrink/Damage/AdminError)

Generator link

Generate an InventoryMovement adjustment to reconcile.

7.4 DimCarrier
Purpose: carrier analytics beyond a string name.
Properties

CarrierName (unique)
CarrierType (Parcel/LTL/FTL)
ReliabilityScore (optional)

ShipmentLine change

Replace CarrierName with Carrier reference.


8) Data Generation Contract (Rules for Realism)
This is the part your builder agent should treat as non-negotiable constraints.
8.1 Demand generation (SalesOrderLine)

Demand is driven by:

Product.Category, Region, Channel, and time (DimDate).


Include patterns:

Weekly seasonality (e.g., weekend uplift for some categories).
Annual seasonality (holiday peak, summer peak).
Random noise.


Include behaviours:

Cancellations (small %).
Partial shipments and backorders when inventory is insufficient.
Price variation if PricePromotion exists.



8.2 Replenishment generation (PurchaseOrderLine)

POs should be created only for valid (Product, Supplier) pairs in ProductSupplier.
Use a DC reorder policy:

Safety stock + lead time demand (approximation is fine).
Respect MinOrderQty and OrderMultipleQty.


Lead time realism:

ExpectedReceiptDate = OrderDate + PlannedLeadTimeDays.
ReceiptDate = ExpectedReceiptDate + random variance (including occasional large delays).


Include supplier heterogeneity:

Some suppliers are consistently late; others reliable.
Occasional disruptions concentrated by supplier tier or geography.



8.3 Fulfilment generation (ShipmentLine + InventoryMovement)

When fulfilling an SO:

Allocate inventory where possible, creating AllocatedQty.
Create one or more ShipmentLine records that sum to ShippedQty.
For each shipment, create matching InventoryMovement records:

Ship movement (negative qty) from OriginLocation.




Transit realism:

DeliveryDate = ShipDate + transit time with variability based on region/service level.



8.4 Inventory integrity and movements

Inventory changes must be explainable via InventoryMovement.
Allowed movement types and sign conventions:

Receipt: Qty > 0 into ToLocation
Ship: Qty < 0 out of FromLocation
Transfer: two movements or one movement with From/To (choose one approach and keep consistent)
Adjustment: signed, used for shrink/damage/expiry/system corrections


Prevent unrealistic states:

Avoid large negative OnHandQty unless explicitly modelling system issues.
Ensure ShippedQty does not exceed what was allocated/available unless you’re modelling overship.



8.5 Snapshot generation (InventorySnapshotDaily)

Compute daily per (Location, Product):

OnHandQty from cumulative movements.
AllocatedQty from open sales orders (not yet shipped).
OnOrderQty from open purchase orders (not yet received).
InTransitQty from shipped-but-not-delivered quantities (if modelled).


If you want “ERP messiness”:

introduce small discrepancies periodically and correct them via StockCountEvent and Adjustment movements.




9) Build Order (Dependency-Safe)
Recommended creation and population sequence (because references must exist before they can be assigned):

Create and populate DimDate
Create and populate DimProduct, DimLocation, DimSupplier, DimCustomer
Create and populate ProductSupplier
Seed initial inventory (either:

InventoryMovement adjustments on a start date, or
initial InventorySnapshotDaily plus balancing movements)


Generate SalesOrderLine across time
Generate ShipmentLine and corresponding InventoryMovement ship transactions
Generate PurchaseOrderLine and corresponding InventoryMovement receipt transactions
Generate or refresh InventorySnapshotDaily

If you do POs before demand, you’ll tend to overstock unrealistically unless you also generate forecasts. Demand-first forces the generator to show stock pressure and service outcomes.

10) Example IRIS SQL Usage (implicit joins with ->)
These examples demonstrate the intended usage pattern once references are object properties.


Sales by category and month:

Select sol->Product->Category, sol->OrderDate->Year, sol->OrderDate->Month, sum of sol.ShippedQty



Supplier on-time receipt rate:

Group by pol->Supplier->SupplierName, compare pol.ReceiptDate->CalendarDate to pol.ExpectedReceiptDate->CalendarDate



Lane performance:

Group by ship->OriginLocation->Region and ship->DestinationLocation->Region, average transit days



Your builder agent can include these as validation queries to prove the object references are wired correctly.

11) What I would challenge (so you don’t build an impressive-looking but shallow dataset)
If you only implement the “core” without at least one of:

promotions/price variation, or
stock counts/shrink, or
returns

then many hackathon teams will hit a ceiling quickly because the dataset won’t produce interesting anomalies, causal structure, or operational trade-offs. For broad re-use, I recommend adding StockCountEvent (plus adjustment movements) as the smallest high-impact realism booster.