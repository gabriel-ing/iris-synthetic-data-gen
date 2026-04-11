Class ThemePark.Shifts Extends %Persistent [ DdlAllowed, SqlTableName = Shifts ]
{

Property ShiftNumber As %String(MAXLEN = 50) [ Required ];

Property Employee As ThemePark.Employees [ Required ];

Property Park As ThemePark.Parks [ Required ];

Property Zone As ThemePark.Zones [ Required ];

Property Ride As ThemePark.Rides;

Property ShiftStart As %TimeStamp;

Property ShiftEnd As %TimeStamp;

Property ShiftType As %String(MAXLEN = 20);

Property AssignmentType As %String(MAXLEN = 30);

Property CoverageStatus As %String(MAXLEN = 30);

Property OvertimeFlag As %Boolean;

Index ShiftNumberIdx On ShiftNumber [ Unique ];

Index EmployeeStartIdx On (Employee, ShiftStart);

Index ParkZoneStartIdx On (Park, Zone, ShiftStart);

Storage Default
{
<Data name="ShiftsDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>ShiftNumber</Value>
</Value>
<Value name="3">
<Value>Employee</Value>
</Value>
<Value name="4">
<Value>Park</Value>
</Value>
<Value name="5">
<Value>Zone</Value>
</Value>
<Value name="6">
<Value>Ride</Value>
</Value>
<Value name="7">
<Value>ShiftStart</Value>
</Value>
<Value name="8">
<Value>ShiftEnd</Value>
</Value>
<Value name="9">
<Value>ShiftType</Value>
</Value>
<Value name="10">
<Value>AssignmentType</Value>
</Value>
<Value name="11">
<Value>CoverageStatus</Value>
</Value>
<Value name="12">
<Value>OvertimeFlag</Value>
</Value>
</Data>
<DataLocation>^ThemePark.ShiftsD</DataLocation>
<DefaultData>ShiftsDefaultData</DefaultData>
<IdLocation>^ThemePark.ShiftsD</IdLocation>
<IndexLocation>^ThemePark.ShiftsI</IndexLocation>
<StreamLocation>^ThemePark.ShiftsS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
