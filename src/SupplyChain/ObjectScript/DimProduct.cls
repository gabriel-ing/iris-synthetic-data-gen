Class SupplyChain.DimProduct Extends %Persistent [ DdlAllowed, SqlTableName = DimProduct ]
{

Property Sku As %String(MAXLEN = 40) [ Required ];

Property ProductName As %String(MAXLEN = 120);

Property Brand As %String(MAXLEN = 60);

Property Category As %String(MAXLEN = 40);

Property Subcategory As %String(MAXLEN = 40);

Property Uom As %String(MAXLEN = 20);

Property UnitsPerCase As %Integer;

Property UnitWeightKg As %Double;

Property UnitVolumeM3 As %Double;

Property TemperatureZone As %String(MAXLEN = 20);

Property IsPerishable As %Boolean;

Property ShelfLifeDays As %Integer;

Property StandardCost As %Numeric(SCALE = 2);

Property ListPrice As %Numeric(SCALE = 2);

Property LaunchDate As SupplyChain.DimDate;

Property DiscontinueDate As SupplyChain.DimDate;

Index SkuIdx On Sku [ Unique ];

Index CategoryIdx On Category;

Index BrandIdx On Brand;

Index TemperatureIdx On TemperatureZone;

Index PerishableIdx On IsPerishable;

Storage Default
{
<Data name="DimProductDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>Sku</Value>
</Value>
<Value name="3">
<Value>ProductName</Value>
</Value>
<Value name="4">
<Value>Brand</Value>
</Value>
<Value name="5">
<Value>Category</Value>
</Value>
<Value name="6">
<Value>Subcategory</Value>
</Value>
<Value name="7">
<Value>Uom</Value>
</Value>
<Value name="8">
<Value>UnitsPerCase</Value>
</Value>
<Value name="9">
<Value>UnitWeightKg</Value>
</Value>
<Value name="10">
<Value>UnitVolumeM3</Value>
</Value>
<Value name="11">
<Value>TemperatureZone</Value>
</Value>
<Value name="12">
<Value>IsPerishable</Value>
</Value>
<Value name="13">
<Value>ShelfLifeDays</Value>
</Value>
<Value name="14">
<Value>StandardCost</Value>
</Value>
<Value name="15">
<Value>ListPrice</Value>
</Value>
<Value name="16">
<Value>LaunchDate</Value>
</Value>
<Value name="17">
<Value>DiscontinueDate</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.DimProductD</DataLocation>
<DefaultData>DimProductDefaultData</DefaultData>
<IdLocation>^SupplyChain.DimProductD</IdLocation>
<IndexLocation>^SupplyChain.DimProductI</IndexLocation>
<StreamLocation>^SupplyChain.DimProductS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
