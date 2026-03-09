Class SupplyChain.InventorySnapshotDaily Extends %Persistent [ DdlAllowed, SqlTableName = InventorySnapshotDaily ]
{

Property SnapshotDate As SupplyChain.DimDate [ Required ];

Property Product As SupplyChain.DimProduct [ Required ];

Property Location As SupplyChain.DimLocation [ Required ];

Property OnHandQty As %Numeric(SCALE = 2);

Property AllocatedQty As %Numeric(SCALE = 2);

Property AvailableQty As %Numeric(SCALE = 2);

Property InTransitQty As %Numeric(SCALE = 2);

Property SafetyStockQty As %Numeric(SCALE = 2);

Property OnOrderQty As %Numeric(SCALE = 2);

Property InventoryValue As %Numeric(SCALE = 2);

Index SnapshotUnique On (SnapshotDate, Product, Location) [ Unique ];

Index LocationDateIdx On (Location, SnapshotDate);

Index ProductDateIdx On (Product, SnapshotDate);

Storage Default
{
<Data name="InventorySnapshotDailyDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>SnapshotDate</Value>
</Value>
<Value name="3">
<Value>Product</Value>
</Value>
<Value name="4">
<Value>Location</Value>
</Value>
<Value name="5">
<Value>OnHandQty</Value>
</Value>
<Value name="6">
<Value>AllocatedQty</Value>
</Value>
<Value name="7">
<Value>AvailableQty</Value>
</Value>
<Value name="8">
<Value>InTransitQty</Value>
</Value>
<Value name="9">
<Value>SafetyStockQty</Value>
</Value>
<Value name="10">
<Value>OnOrderQty</Value>
</Value>
<Value name="11">
<Value>InventoryValue</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.InventorySnF192D</DataLocation>
<DefaultData>InventorySnapshotDailyDefaultData</DefaultData>
<IdLocation>^SupplyChain.InventorySnF192D</IdLocation>
<IndexLocation>^SupplyChain.InventorySnF192I</IndexLocation>
<StreamLocation>^SupplyChain.InventorySnF192S</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
