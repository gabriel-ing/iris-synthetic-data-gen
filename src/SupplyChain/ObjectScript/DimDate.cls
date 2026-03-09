Class SupplyChain.DimDate Extends %Persistent [ DdlAllowed, SqlTableName = DimDate ]
{

Property DateKey As %Integer [ Required ];

Property CalendarDate As %Date [ Required ];

Property Year As %Integer;

Property Quarter As %Integer;

Property Month As %Integer;

Property WeekOfYear As %Integer;

Property DayOfWeek As %Integer;

Property IsWeekend As %Boolean;

Index DateKeyIdx On DateKey [ Unique ];

Index CalendarDateIdx On CalendarDate;

Index YearMonthIdx On (Year, Month);

Storage Default
{
<Data name="DimDateDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>DateKey</Value>
</Value>
<Value name="3">
<Value>CalendarDate</Value>
</Value>
<Value name="4">
<Value>Year</Value>
</Value>
<Value name="5">
<Value>Quarter</Value>
</Value>
<Value name="6">
<Value>Month</Value>
</Value>
<Value name="7">
<Value>WeekOfYear</Value>
</Value>
<Value name="8">
<Value>DayOfWeek</Value>
</Value>
<Value name="9">
<Value>IsWeekend</Value>
</Value>
</Data>
<DataLocation>^SupplyChain.DimDateD</DataLocation>
<DefaultData>DimDateDefaultData</DefaultData>
<IdLocation>^SupplyChain.DimDateD</IdLocation>
<IndexLocation>^SupplyChain.DimDateI</IndexLocation>
<StreamLocation>^SupplyChain.DimDateS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
