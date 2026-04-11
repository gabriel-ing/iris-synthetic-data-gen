Class ThemePark.RideMaintenance Extends %Persistent [ DdlAllowed, SqlTableName = RideMaintenance ]
{

Property MaintenanceNumber As %String(MAXLEN = 50) [ Required ];

Property Ride As ThemePark.Rides [ Required ];

Property ScheduledStart As %TimeStamp;

Property ActualStart As %TimeStamp;

Property ActualEnd As %TimeStamp;

Property MaintenanceType As %String(MAXLEN = 40);

Property Status As %String(MAXLEN = 30);

Property Severity As %String(MAXLEN = 20);

Property DowntimeHours As %Numeric(SCALE = 2);

Property IssueSummary As %String(MAXLEN = 240);

Property VendorName As %String(MAXLEN = 120);

Index MaintenanceNumberIdx On MaintenanceNumber [ Unique ];

Index RideStartIdx On (Ride, ScheduledStart);

Storage Default
{
<Data name="RideMaintenanceDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>MaintenanceNumber</Value>
</Value>
<Value name="3">
<Value>Ride</Value>
</Value>
<Value name="4">
<Value>ScheduledStart</Value>
</Value>
<Value name="5">
<Value>ActualStart</Value>
</Value>
<Value name="6">
<Value>ActualEnd</Value>
</Value>
<Value name="7">
<Value>MaintenanceType</Value>
</Value>
<Value name="8">
<Value>Status</Value>
</Value>
<Value name="9">
<Value>Severity</Value>
</Value>
<Value name="10">
<Value>DowntimeHours</Value>
</Value>
<Value name="11">
<Value>IssueSummary</Value>
</Value>
<Value name="12">
<Value>VendorName</Value>
</Value>
</Data>
<DataLocation>^ThemePark.RideMaintenanceD</DataLocation>
<DefaultData>RideMaintenanceDefaultData</DefaultData>
<IdLocation>^ThemePark.RideMaintenanceD</IdLocation>
<IndexLocation>^ThemePark.RideMaintenanceI</IndexLocation>
<StreamLocation>^ThemePark.RideMaintenanceS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
