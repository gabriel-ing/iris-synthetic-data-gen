Class SupplyChain.ShipmentLine Extends %Persistent [ DdlAllowed, SqlTableName = ShipmentLine ]
{

Property ShipmentId As %String(MAXLEN = 40) [ Required ];

Property LineNumber As %Integer [ Required ];

Property SalesOrderLine As SupplyChain.SalesOrderLine;

Property Product As SupplyChain.DimProduct [ Required ];

Property OriginLocation As SupplyChain.DimLocation [ Required ];

Property DestinationLocation As SupplyChain.DimLocation [ Required ];

Property ShipDate As SupplyChain.DimDate [ Required ];

Property DeliveryDate As SupplyChain.DimDate;

Property ShippedQty As %Numeric(SCALE = 2);

Property CarrierName As %String(MAXLEN = 80);

Property ServiceLevel As %String(MAXLEN = 30);

Property PlannedTransitDays As %Integer;

Property ActualTransitDays As %Integer;

Property FreightCost As %Numeric(SCALE = 2);

Property ShipmentStatus As %String(MAXLEN = 30);

Property DelayReason As %String(MAXLEN = 80);

Index ShipmentLineIdx On (ShipmentId, LineNumber);

Index SalesOrderLineIdx On SalesOrderLine;

Index ShipDateIdx On ShipDate;

Index OriginDestinationIdx On (OriginLocation, DestinationLocation);

Index ShipmentStatusIdx On ShipmentStatus;

Storage Default
{
<Data name="ShipmentLineDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>ShipmentId</Value>
</Value>
<Value name="3">
<Value>LineNumber</Value>
</Value>
<Value name="4">
<Value>SalesOrderLine</Value>
</Value>
<Value name="5">
<Value>Product</Value>
</Value>
<Value name="6">
<Value>OriginLocation</Value>
</Value>
<Value name="7">
<Value>DestinationLocation</Value>
</Value>
<Value name="8">
<Value>ShipDate</Value>
</Value>
<Value name="9">
<Value>DeliveryDate</Value>
</Value>
<Value name="10">
<Value>ShippedQty</Value>
</Value>
<Value name="11">
<Value>CarrierName</Value>
</Value>
<Value name="12">
<Value>ServiceLevel</Value>
</Value>
<Value name="13">
<Value>PlannedTransitDays</Value>
</Value>
<Value name="14">
<Value>ActualTransitDays</Value>
</Value>
<Value name="15">
<Value>FreightCost</Value>
</Value>
<Value name="16">
<Value>ShipmentStatus</Value>
</Value>
<Value name="17">
<Value>DelayReason</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.ShipmentLineD</DataLocation>
<DefaultData>ShipmentLineDefaultData</DefaultData>
<IdLocation>^SupplyChain.ShipmentLineD</IdLocation>
<IndexLocation>^SupplyChain.ShipmentLineI</IndexLocation>
<StreamLocation>^SupplyChain.ShipmentLineS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
