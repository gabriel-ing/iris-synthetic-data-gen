Class ThemePark.QueueSnapshot Extends %Persistent [ DdlAllowed, SqlTableName = QueueSnapshot ]
{

Property SnapshotAt As %TimeStamp;

Property Park As ThemePark.Parks [ Required ];

Property Ride As ThemePark.Rides [ Required ];

Property WaitMinutes As %Integer;

Property QueueLength As %Integer;

Property ThroughputPerHour As %Integer;

Property Status As %String(MAXLEN = 30);

Property FastAccessPressure As %Numeric(SCALE = 4);

Property DowntimeHours As %Numeric(SCALE = 2);

Index RideSnapshotIdx On (Ride, SnapshotAt);

Index ParkSnapshotIdx On (Park, SnapshotAt);

Storage Default
{
<Data name="QueueSnapshotDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>SnapshotAt</Value>
</Value>
<Value name="3">
<Value>Park</Value>
</Value>
<Value name="4">
<Value>Ride</Value>
</Value>
<Value name="5">
<Value>WaitMinutes</Value>
</Value>
<Value name="6">
<Value>QueueLength</Value>
</Value>
<Value name="7">
<Value>ThroughputPerHour</Value>
</Value>
<Value name="8">
<Value>Status</Value>
</Value>
<Value name="9">
<Value>FastAccessPressure</Value>
</Value>
<Value name="10">
<Value>DowntimeHours</Value>
</Value>
</Data>
<DataLocation>^ThemePark.QueueSnapshotD</DataLocation>
<DefaultData>QueueSnapshotDefaultData</DefaultData>
<IdLocation>^ThemePark.QueueSnapshotD</IdLocation>
<IndexLocation>^ThemePark.QueueSnapshotI</IndexLocation>
<StreamLocation>^ThemePark.QueueSnapshotS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}