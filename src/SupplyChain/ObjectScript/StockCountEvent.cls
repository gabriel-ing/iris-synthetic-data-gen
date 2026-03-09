Class SupplyChain.StockCountEvent Extends %Persistent [ DdlAllowed, SqlTableName = StockCountEvent ]
{

Property Location As SupplyChain.DimLocation [ Required ];

Property Product As SupplyChain.DimProduct [ Required ];

Property CountDate As SupplyChain.DimDate [ Required ];

Property SystemQty As %Numeric(SCALE = 2);

Property CountedQty As %Numeric(SCALE = 2);

Property VarianceQty As %Numeric(SCALE = 2);

Property VarianceReason As %String(MAXLEN = 80);

Index LocationDateIdx On (Location, CountDate);

Index ProductDateIdx On (Product, CountDate);

Storage Default
{
<Data name="StockCountEventDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>Location</Value>
</Value>
<Value name="3">
<Value>Product</Value>
</Value>
<Value name="4">
<Value>CountDate</Value>
</Value>
<Value name="5">
<Value>SystemQty</Value>
</Value>
<Value name="6">
<Value>CountedQty</Value>
</Value>
<Value name="7">
<Value>VarianceQty</Value>
</Value>
<Value name="8">
<Value>VarianceReason</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.StockCountEventD</DataLocation>
<DefaultData>StockCountEventDefaultData</DefaultData>
<IdLocation>^SupplyChain.StockCountEventD</IdLocation>
<IndexLocation>^SupplyChain.StockCountEventI</IndexLocation>
<StreamLocation>^SupplyChain.StockCountEventS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
