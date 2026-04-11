Class ThemePark.Zones Extends %Persistent [ DdlAllowed, SqlTableName = Zones ]
{

Property ZoneCode As %String(MAXLEN = 40) [ Required ];

Property Park As ThemePark.Parks [ Required ];

Property ZoneName As %String(MAXLEN = 120);

Property Theme As %String(MAXLEN = 60);

Property Environment As %String(MAXLEN = 20);

Property FamilyIntensity As %String(MAXLEN = 20);

Property CapacityClass As %String(MAXLEN = 20);

Property IndoorFlag As %Boolean;

Index ZoneCodeIdx On ZoneCode [ Unique ];

Index ParkThemeIdx On (Park, Theme);

Storage Default
{
<Data name="ZonesDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>ZoneCode</Value>
</Value>
<Value name="3">
<Value>Park</Value>
</Value>
<Value name="4">
<Value>ZoneName</Value>
</Value>
<Value name="5">
<Value>Theme</Value>
</Value>
<Value name="6">
<Value>Environment</Value>
</Value>
<Value name="7">
<Value>FamilyIntensity</Value>
</Value>
<Value name="8">
<Value>CapacityClass</Value>
</Value>
<Value name="9">
<Value>IndoorFlag</Value>
</Value>
</Data>
<DataLocation>^ThemePark.ZonesD</DataLocation>
<DefaultData>ZonesDefaultData</DefaultData>
<IdLocation>^ThemePark.ZonesD</IdLocation>
<IndexLocation>^ThemePark.ZonesI</IndexLocation>
<StreamLocation>^ThemePark.ZonesS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
