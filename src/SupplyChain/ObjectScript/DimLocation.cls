Class SupplyChain.DimLocation Extends %Persistent [ DdlAllowed, SqlTableName = DimLocation ]
{

Property LocationCode As %String(MAXLEN = 40) [ Required ];

Property LocationName As %String(MAXLEN = 120);

Property LocationType As %String(MAXLEN = 40);

Property Country As %String(MAXLEN = 5);

Property Region As %String(MAXLEN = 40);

Property City As %String(MAXLEN = 80);

Property Postcode As %String(MAXLEN = 20);

Property TimeZone As %String(MAXLEN = 60);

Property IsActive As %Boolean;

Index LocationCodeIdx On LocationCode [ Unique ];

Index TypeIdx On LocationType;

Index RegionIdx On Region;

Index CountryIdx On Country;

Index ActiveIdx On IsActive;

Storage Default
{
<Data name="DimLocationDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>LocationCode</Value>
</Value>
<Value name="3">
<Value>LocationName</Value>
</Value>
<Value name="4">
<Value>LocationType</Value>
</Value>
<Value name="5">
<Value>Country</Value>
</Value>
<Value name="6">
<Value>Region</Value>
</Value>
<Value name="7">
<Value>City</Value>
</Value>
<Value name="8">
<Value>Postcode</Value>
</Value>
<Value name="9">
<Value>TimeZone</Value>
</Value>
<Value name="10">
<Value>IsActive</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.DimLocationD</DataLocation>
<DefaultData>DimLocationDefaultData</DefaultData>
<IdLocation>^SupplyChain.DimLocationD</IdLocation>
<IndexLocation>^SupplyChain.DimLocationI</IndexLocation>
<StreamLocation>^SupplyChain.DimLocationS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
