Class SupplyChain.DimSupplier Extends %Persistent [ DdlAllowed, SqlTableName = DimSupplier ]
{

Property SupplierCode As %String(MAXLEN = 40);

Property SupplierName As %String(MAXLEN = 120);

Property SupplierTier As %Integer;

Property Country As %String(MAXLEN = 5);

Property PreferredFlag As %Boolean;

Property PaymentTermsDays As %Integer;

Property RiskScore As %Integer;

Property DefaultShipFromLocation As SupplyChain.DimLocation;

Index SupplierCodeIdx On SupplierCode [ Unique ];

Index TierIdx On SupplierTier;

Index CountryIdx On Country;

Index PreferredIdx On PreferredFlag;

Storage Default
{
<Data name="DimSupplierDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>SupplierCode</Value>
</Value>
<Value name="3">
<Value>SupplierName</Value>
</Value>
<Value name="4">
<Value>SupplierTier</Value>
</Value>
<Value name="5">
<Value>Country</Value>
</Value>
<Value name="6">
<Value>PreferredFlag</Value>
</Value>
<Value name="7">
<Value>PaymentTermsDays</Value>
</Value>
<Value name="8">
<Value>RiskScore</Value>
</Value>
<Value name="9">
<Value>DefaultShipFromLocation</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.DimSupplierD</DataLocation>
<DefaultData>DimSupplierDefaultData</DefaultData>
<IdLocation>^SupplyChain.DimSupplierD</IdLocation>
<IndexLocation>^SupplyChain.DimSupplierI</IndexLocation>
<StreamLocation>^SupplyChain.DimSupplierS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
