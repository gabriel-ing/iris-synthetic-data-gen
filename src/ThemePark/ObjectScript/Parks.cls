Class ThemePark.Parks Extends %Persistent [ DdlAllowed, SqlTableName = Parks ]
{

Property ParkCode As %String(MAXLEN = 40) [ Required ];

Property ParkName As %String(MAXLEN = 120);

Property Region As %String(MAXLEN = 30);

Property Country As %String(MAXLEN = 5);

Property ParkType As %String(MAXLEN = 30);

Property OpeningDate As %TimeStamp;

Property OperatingModel As %String(MAXLEN = 40);

Property DailyCapacity As %Integer;

Property ActiveFlag As %Boolean;

Index ParkCodeIdx On ParkCode [ Unique ];

Index RegionIdx On Region;

Index ParkTypeIdx On ParkType;

Storage Default
{
<Data name="ParksDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>ParkCode</Value>
</Value>
<Value name="3">
<Value>ParkName</Value>
</Value>
<Value name="4">
<Value>Region</Value>
</Value>
<Value name="5">
<Value>Country</Value>
</Value>
<Value name="6">
<Value>ParkType</Value>
</Value>
<Value name="7">
<Value>OpeningDate</Value>
</Value>
<Value name="8">
<Value>OperatingModel</Value>
</Value>
<Value name="9">
<Value>DailyCapacity</Value>
</Value>
<Value name="10">
<Value>ActiveFlag</Value>
</Value>
</Data>
<DataLocation>^ThemePark.ParksD</DataLocation>
<DefaultData>ParksDefaultData</DefaultData>
<IdLocation>^ThemePark.ParksD</IdLocation>
<IndexLocation>^ThemePark.ParksI</IndexLocation>
<StreamLocation>^ThemePark.ParksS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
