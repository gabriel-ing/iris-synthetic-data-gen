Class SupplyChain.PurchaseOrderLine Extends %Persistent [ DdlAllowed, SqlTableName = PurchaseOrderLine ]
{

Property PurchaseOrderId As %String(MAXLEN = 40) [ Required ];

Property LineNumber As %Integer [ Required ];

Property Supplier As SupplyChain.DimSupplier [ Required ];

Property Product As SupplyChain.DimProduct [ Required ];

Property ShipFromLocation As SupplyChain.DimLocation;

Property DeliverToLocation As SupplyChain.DimLocation [ Required ];

Property OrderDate As SupplyChain.DimDate [ Required ];

Property ExpectedReceiptDate As SupplyChain.DimDate [ Required ];

Property ReceiptDate As SupplyChain.DimDate;

Property OrderedQty As %Numeric(SCALE = 2);

Property ReceivedQty As %Numeric(SCALE = 2);

Property UnitPurchaseCost As %Numeric(SCALE = 2);

Property Status As %String(MAXLEN = 30);

Property CancelReason As %String(MAXLEN = 80);

Property PlannedLeadTimeDays As %Integer;

Property ActualLeadTimeDays As %Integer;

Index PurchaseOrderLineUnique On (PurchaseOrderId, LineNumber) [ Unique ];

Index SupplierIdx On Supplier;

Index ProductIdx On Product;

Index OrderDateIdx On OrderDate;

Index StatusIdx On Status;

Storage Default
{
<Data name="PurchaseOrderLineDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>PurchaseOrderId</Value>
</Value>
<Value name="3">
<Value>LineNumber</Value>
</Value>
<Value name="4">
<Value>Supplier</Value>
</Value>
<Value name="5">
<Value>Product</Value>
</Value>
<Value name="6">
<Value>ShipFromLocation</Value>
</Value>
<Value name="7">
<Value>DeliverToLocation</Value>
</Value>
<Value name="8">
<Value>OrderDate</Value>
</Value>
<Value name="9">
<Value>ExpectedReceiptDate</Value>
</Value>
<Value name="10">
<Value>ReceiptDate</Value>
</Value>
<Value name="11">
<Value>OrderedQty</Value>
</Value>
<Value name="12">
<Value>ReceivedQty</Value>
</Value>
<Value name="13">
<Value>UnitPurchaseCost</Value>
</Value>
<Value name="14">
<Value>Status</Value>
</Value>
<Value name="15">
<Value>CancelReason</Value>
</Value>
<Value name="16">
<Value>PlannedLeadTimeDays</Value>
</Value>
<Value name="17">
<Value>ActualLeadTimeDays</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.PurchaseOrderLineD</DataLocation>
<DefaultData>PurchaseOrderLineDefaultData</DefaultData>
<IdLocation>^SupplyChain.PurchaseOrderLineD</IdLocation>
<IndexLocation>^SupplyChain.PurchaseOrderLineI</IndexLocation>
<StreamLocation>^SupplyChain.PurchaseOrderLineS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
