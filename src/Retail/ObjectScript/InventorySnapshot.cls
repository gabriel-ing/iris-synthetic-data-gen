Class Retail.InventorySnapshot Extends %Persistent [ DdlAllowed, SqlTableName = InventorySnapshot ]
{

Property SnapshotDate As Retail.Calendar [ Required ];

Property Store As Retail.Stores [ Required ];

Property Product As Retail.Products [ Required ];

Property OnHandQty As %Numeric(SCALE = 2);

Property ReservedQty As %Numeric(SCALE = 2);

Property AvailableQty As %Numeric(SCALE = 2);

Property InTransitQty As %Numeric(SCALE = 2);

Property OnOrderQty As %Numeric(SCALE = 2);

Property SafetyStockQty As %Numeric(SCALE = 2);

Property ReorderPointQty As %Numeric(SCALE = 2);

Property ReorderTargetQty As %Numeric(SCALE = 2);

Property UnitCost As %Numeric(SCALE = 2);

Property RegularPrice As %Numeric(SCALE = 2);

Property MarkdownPrice As %Numeric(SCALE = 2);

Property DaysOfSupply As %Numeric(SCALE = 2);

Index SnapshotUnique On (SnapshotDate, Store, Product) [ Unique ];

Index StoreDateIdx On (Store, SnapshotDate);

Index ProductDateIdx On (Product, SnapshotDate);

}