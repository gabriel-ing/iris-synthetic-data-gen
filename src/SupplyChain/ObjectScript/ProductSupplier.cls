Class SupplyChain.ProductSupplier Extends %Persistent [ DdlAllowed, SqlTableName = ProductSupplier ]
{

Property Product As SupplyChain.DimProduct [ Required ];

Property Supplier As SupplyChain.DimSupplier [ Required ];

Property IsPrimarySupplier As %Boolean;

Property MinOrderQty As %Numeric(SCALE = 2);

Property OrderMultipleQty As %Integer;

Property PackSize As %Integer;

Property PlannedLeadTimeDays As %Integer;

Property UnitPurchaseCost As %Numeric(SCALE = 2);

Property Incoterm As %String(MAXLEN = 20);

Property ShipMode As %String(MAXLEN = 20);

Index ProductSupplierUnique On (Product, Supplier) [ Unique ];

Index SupplierIdx On Supplier;

Index ProductIdx On Product;

Index PrimarySupplierIdx On IsPrimarySupplier;

Storage Default
{
<Data name="ProductSupplierDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>Product</Value>
</Value>
<Value name="3">
<Value>Supplier</Value>
</Value>
<Value name="4">
<Value>IsPrimarySupplier</Value>
</Value>
<Value name="5">
<Value>MinOrderQty</Value>
</Value>
<Value name="6">
<Value>OrderMultipleQty</Value>
</Value>
<Value name="7">
<Value>PackSize</Value>
</Value>
<Value name="8">
<Value>PlannedLeadTimeDays</Value>
</Value>
<Value name="9">
<Value>UnitPurchaseCost</Value>
</Value>
<Value name="10">
<Value>Incoterm</Value>
</Value>
<Value name="11">
<Value>ShipMode</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.ProductSupplierD</DataLocation>
<DefaultData>ProductSupplierDefaultData</DefaultData>
<IdLocation>^SupplyChain.ProductSupplierD</IdLocation>
<IndexLocation>^SupplyChain.ProductSupplierI</IndexLocation>
<StreamLocation>^SupplyChain.ProductSupplierS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
