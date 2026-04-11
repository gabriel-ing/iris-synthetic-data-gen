Class ThemePark.Rides Extends %Persistent [ DdlAllowed, SqlTableName = Rides ]
{

Property RideCode As %String(MAXLEN = 40) [ Required ];

Property Zone As ThemePark.Zones [ Required ];

Property RideName As %String(MAXLEN = 120);

Property RideType As %String(MAXLEN = 30);

Property ThrillLevel As %Integer;

Property HeightRequirementCm As %Integer;

Property CapacityPerHour As %Integer;

Property OpeningDate As %TimeStamp;

Property AccessibilitySupport As %String(MAXLEN = 30);

Property Status As %String(MAXLEN = 30);

Index RideCodeIdx On RideCode [ Unique ];

Index ZoneTypeIdx On (Zone, RideType);

Storage Default
{
<Data name="RidesDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>RideCode</Value>
</Value>
<Value name="3">
<Value>Zone</Value>
</Value>
<Value name="4">
<Value>RideName</Value>
</Value>
<Value name="5">
<Value>RideType</Value>
</Value>
<Value name="6">
<Value>ThrillLevel</Value>
</Value>
<Value name="7">
<Value>HeightRequirementCm</Value>
</Value>
<Value name="8">
<Value>CapacityPerHour</Value>
</Value>
<Value name="9">
<Value>OpeningDate</Value>
</Value>
<Value name="10">
<Value>AccessibilitySupport</Value>
</Value>
<Value name="11">
<Value>Status</Value>
</Value>
</Data>
<DataLocation>^ThemePark.RidesD</DataLocation>
<DefaultData>RidesDefaultData</DefaultData>
<IdLocation>^ThemePark.RidesD</IdLocation>
<IndexLocation>^ThemePark.RidesI</IndexLocation>
<StreamLocation>^ThemePark.RidesS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
