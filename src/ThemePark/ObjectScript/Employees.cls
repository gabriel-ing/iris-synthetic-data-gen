Class ThemePark.Employees Extends %Persistent [ DdlAllowed, SqlTableName = Employees ]
{

Property EmployeeNumber As %String(MAXLEN = 40) [ Required ];

Property Park As ThemePark.Parks [ Required ];

Property HomeZone As ThemePark.Zones [ Required ];

Property EmployeeName As %String(MAXLEN = 120);

Property RoleType As %String(MAXLEN = 40);

Property SkillTier As %String(MAXLEN = 20);

Property EmploymentType As %String(MAXLEN = 20);

Property HireDate As %TimeStamp;

Property MascotQualifiedFlag As %Boolean;

Property ActiveFlag As %Boolean;

Index EmployeeNumberIdx On EmployeeNumber [ Unique ];

Index ParkRoleIdx On (Park, RoleType);

Storage Default
{
<Data name="EmployeesDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>EmployeeNumber</Value>
</Value>
<Value name="3">
<Value>Park</Value>
</Value>
<Value name="4">
<Value>HomeZone</Value>
</Value>
<Value name="5">
<Value>EmployeeName</Value>
</Value>
<Value name="6">
<Value>RoleType</Value>
</Value>
<Value name="7">
<Value>SkillTier</Value>
</Value>
<Value name="8">
<Value>EmploymentType</Value>
</Value>
<Value name="9">
<Value>HireDate</Value>
</Value>
<Value name="10">
<Value>MascotQualifiedFlag</Value>
</Value>
<Value name="11">
<Value>ActiveFlag</Value>
</Value>
</Data>
<DataLocation>^ThemePark.EmployeesD</DataLocation>
<DefaultData>EmployeesDefaultData</DefaultData>
<IdLocation>^ThemePark.EmployeesD</IdLocation>
<IndexLocation>^ThemePark.EmployeesI</IndexLocation>
<StreamLocation>^ThemePark.EmployeesS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
