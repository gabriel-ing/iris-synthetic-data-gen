Class ThemePark.Incidents Extends %Persistent [ DdlAllowed, SqlTableName = Incidents ]
{

Property IncidentNumber As %String(MAXLEN = 50) [ Required ];

Property Park As ThemePark.Parks [ Required ];

Property Zone As ThemePark.Zones;

Property Ride As ThemePark.Rides;

Property Ticket As ThemePark.Tickets;

Property ReportedEmployee As ThemePark.Employees;

Property IncidentAt As %TimeStamp;

Property IncidentType As %String(MAXLEN = 40);

Property Severity As %String(MAXLEN = 20);

Property Status As %String(MAXLEN = 30);

Property ImpactMinutes As %Integer;

Property Description As %String(MAXLEN = 240);

Property ResolutionSummary As %String(MAXLEN = 240);

Index IncidentNumberIdx On IncidentNumber [ Unique ];

Index ParkIncidentAtIdx On (Park, IncidentAt);

Index RideIncidentAtIdx On (Ride, IncidentAt);

Storage Default
{
<Data name="IncidentsDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>IncidentNumber</Value>
</Value>
<Value name="3">
<Value>Park</Value>
</Value>
<Value name="4">
<Value>Zone</Value>
</Value>
<Value name="5">
<Value>Ride</Value>
</Value>
<Value name="6">
<Value>Ticket</Value>
</Value>
<Value name="7">
<Value>ReportedEmployee</Value>
</Value>
<Value name="8">
<Value>IncidentAt</Value>
</Value>
<Value name="9">
<Value>IncidentType</Value>
</Value>
<Value name="10">
<Value>Severity</Value>
</Value>
<Value name="11">
<Value>Status</Value>
</Value>
<Value name="12">
<Value>ImpactMinutes</Value>
</Value>
<Value name="13">
<Value>Description</Value>
</Value>
<Value name="14">
<Value>ResolutionSummary</Value>
</Value>
</Data>
<DataLocation>^ThemePark.IncidentsD</DataLocation>
<DefaultData>IncidentsDefaultData</DefaultData>
<IdLocation>^ThemePark.IncidentsD</IdLocation>
<IndexLocation>^ThemePark.IncidentsI</IndexLocation>
<StreamLocation>^ThemePark.IncidentsS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
