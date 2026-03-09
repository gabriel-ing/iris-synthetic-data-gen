Class SupplyChain.InventoryMovement Extends %Persistent [ DdlAllowed, SqlTableName = InventoryMovement ]
{

Property Product As SupplyChain.DimProduct [ Required ];

Property FromLocation As SupplyChain.DimLocation;

Property ToLocation As SupplyChain.DimLocation;

Property MovementDate As SupplyChain.DimDate [ Required ];

Property MovementTimestamp As %TimeStamp;

Property MovementType As %String(MAXLEN = 30);

Property ReferenceType As %String(MAXLEN = 40);

Property ReferenceId As %String(MAXLEN = 60);

Property Qty As %Numeric(SCALE = 2);

Property UnitCost As %Numeric(SCALE = 2);

Property ReasonCode As %String(MAXLEN = 80);

Index ProductDateIdx On (Product, MovementDate);

Index FromLocationDateIdx On (FromLocation, MovementDate);

Index ToLocationDateIdx On (ToLocation, MovementDate);

Index ReferenceIdx On (ReferenceType, ReferenceId);

Storage Default
{
<Data name="InventoryMovementDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>Product</Value>
</Value>
<Value name="3">
<Value>FromLocation</Value>
</Value>
<Value name="4">
<Value>ToLocation</Value>
</Value>
<Value name="5">
<Value>MovementDate</Value>
</Value>
<Value name="6">
<Value>MovementTimestamp</Value>
</Value>
<Value name="7">
<Value>MovementType</Value>
</Value>
<Value name="8">
<Value>ReferenceType</Value>
</Value>
<Value name="9">
<Value>ReferenceId</Value>
</Value>
<Value name="10">
<Value>Qty</Value>
</Value>
<Value name="11">
<Value>UnitCost</Value>
</Value>
<Value name="12">
<Value>ReasonCode</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.InventoryMovementD</DataLocation>
<DefaultData>InventoryMovementDefaultData</DefaultData>
<IdLocation>^SupplyChain.InventoryMovementD</IdLocation>
<IndexLocation>^SupplyChain.InventoryMovementI</IndexLocation>
<StreamLocation>^SupplyChain.InventoryMovementS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
