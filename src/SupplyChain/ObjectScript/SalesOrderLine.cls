Class SupplyChain.SalesOrderLine Extends %Persistent [ DdlAllowed, SqlTableName = SalesOrderLine ]
{

Property SalesOrderId As %String(MAXLEN = 40) [ Required ];

Property LineNumber As %Integer [ Required ];

Property Customer As SupplyChain.DimCustomer [ Required ];

Property Product As SupplyChain.DimProduct [ Required ];

Property ShipFromLocation As SupplyChain.DimLocation [ Required ];

Property ShipToLocation As SupplyChain.DimLocation [ Required ];

Property OrderDate As SupplyChain.DimDate [ Required ];

Property RequestedShipDate As SupplyChain.DimDate [ Required ];

Property PromisedDeliveryDate As SupplyChain.DimDate [ Required ];

Property ActualDeliveryDate As SupplyChain.DimDate;

Property OrderedQty As %Numeric(SCALE = 2);

Property AllocatedQty As %Numeric(SCALE = 2);

Property ShippedQty As %Numeric(SCALE = 2);

Property BackorderedQty As %Numeric(SCALE = 2);

Property UnitSellPrice As %Numeric(SCALE = 2);

Property Status As %String(MAXLEN = 30);

Property Channel As %String(MAXLEN = 20);

Index SalesOrderLineUnique On (SalesOrderId, LineNumber) [ Unique ];

Index CustomerIdx On Customer;

Index ProductIdx On Product;

Index OrderDateIdx On OrderDate;

Index StatusIdx On Status;

Index ChannelIdx On Channel;

Storage Default
{
<Data name="SalesOrderLineDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>SalesOrderId</Value>
</Value>
<Value name="3">
<Value>LineNumber</Value>
</Value>
<Value name="4">
<Value>Customer</Value>
</Value>
<Value name="5">
<Value>Product</Value>
</Value>
<Value name="6">
<Value>ShipFromLocation</Value>
</Value>
<Value name="7">
<Value>ShipToLocation</Value>
</Value>
<Value name="8">
<Value>OrderDate</Value>
</Value>
<Value name="9">
<Value>RequestedShipDate</Value>
</Value>
<Value name="10">
<Value>PromisedDeliveryDate</Value>
</Value>
<Value name="11">
<Value>ActualDeliveryDate</Value>
</Value>
<Value name="12">
<Value>OrderedQty</Value>
</Value>
<Value name="13">
<Value>AllocatedQty</Value>
</Value>
<Value name="14">
<Value>ShippedQty</Value>
</Value>
<Value name="15">
<Value>BackorderedQty</Value>
</Value>
<Value name="16">
<Value>UnitSellPrice</Value>
</Value>
<Value name="17">
<Value>Status</Value>
</Value>
<Value name="18">
<Value>Channel</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.SalesOrderLineD</DataLocation>
<DefaultData>SalesOrderLineDefaultData</DefaultData>
<IdLocation>^SupplyChain.SalesOrderLineD</IdLocation>
<IndexLocation>^SupplyChain.SalesOrderLineI</IndexLocation>
<StreamLocation>^SupplyChain.SalesOrderLineS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
