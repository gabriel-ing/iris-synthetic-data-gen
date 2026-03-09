Class SupplyChain.DimCustomer Extends %Persistent [ DdlAllowed, SqlTableName = DimCustomer ]
{

Property CustomerNumber As %String(MAXLEN = 40);

Property CustomerName As %String(MAXLEN = 120);

Property CustomerType As %String(MAXLEN = 20);

Property Segment As %String(MAXLEN = 40);

Property Country As %String(MAXLEN = 5);

Property Region As %String(MAXLEN = 40);

Property ServiceLevelTargetPct As %Numeric(SCALE = 2);

Property DefaultShipToLocation As SupplyChain.DimLocation;

Index CustomerNumberIdx On CustomerNumber [ Unique ];

Index CustomerTypeIdx On CustomerType;

Index SegmentIdx On Segment;

Index RegionIdx On Region;

Storage Default
{
<Data name="DimCustomerDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>CustomerNumber</Value>
</Value>
<Value name="3">
<Value>CustomerName</Value>
</Value>
<Value name="4">
<Value>CustomerType</Value>
</Value>
<Value name="5">
<Value>Segment</Value>
</Value>
<Value name="6">
<Value>Country</Value>
</Value>
<Value name="7">
<Value>Region</Value>
</Value>
<Value name="8">
<Value>ServiceLevelTargetPct</Value>
</Value>
<Value name="9">
<Value>DefaultShipToLocation</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.DimCustomerD</DataLocation>
<DefaultData>DimCustomerDefaultData</DefaultData>
<IdLocation>^SupplyChain.DimCustomerD</IdLocation>
<IndexLocation>^SupplyChain.DimCustomerI</IndexLocation>
<StreamLocation>^SupplyChain.DimCustomerS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
