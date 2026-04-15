Class Retail.Customers Extends %Persistent [ DdlAllowed, SqlTableName = Customers ]
{

Property CustomerNumber As %String(MAXLEN = 40) [ Required ];

Property Segment As %String(MAXLEN = 20);

Property LoyaltyTier As %String(MAXLEN = 20);

Property HomeStore As Retail.Stores [ Required ];

Property PreferredChannel As %String(MAXLEN = 30);

Property JoinDate As %TimeStamp;

Property ActiveFlag As %Boolean;

Index CustomerNumberIdx On CustomerNumber [ Unique ];

Index HomeStoreIdx On HomeStore;

Storage Default
{
<Data name="CustomersDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>CustomerNumber</Value>
</Value>
<Value name="3">
<Value>Segment</Value>
</Value>
<Value name="4">
<Value>LoyaltyTier</Value>
</Value>
<Value name="5">
<Value>HomeStore</Value>
</Value>
<Value name="6">
<Value>PreferredChannel</Value>
</Value>
<Value name="7">
<Value>JoinDate</Value>
</Value>
<Value name="8">
<Value>ActiveFlag</Value>
</Value>
</Data>
<DataLocation>^Retail.CustomersD</DataLocation>
<DefaultData>CustomersDefaultData</DefaultData>
<IdLocation>^Retail.CustomersD</IdLocation>
<IndexLocation>^Retail.CustomersI</IndexLocation>
<StreamLocation>^Retail.CustomersS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}