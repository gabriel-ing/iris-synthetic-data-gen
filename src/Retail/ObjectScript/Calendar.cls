Class Retail.Calendar Extends %Persistent [ DdlAllowed, SqlTableName = Calendar ]
{

Property DateKey As %Integer [ Required ];

Property CalendarDate As %Date [ Required ];

Property Year As %Integer;

Property Quarter As %Integer;

Property Month As %Integer;

Property WeekOfYear As %Integer;

Property DayOfWeek As %Integer;

Property IsWeekend As %Boolean;

Property Season As %String(MAXLEN = 20);

Property FiscalPeriod As %String(MAXLEN = 16);

Property RetailEvent As %String(MAXLEN = 40);

Index DateKeyIdx On DateKey [ Unique ];

Index CalendarDateIdx On CalendarDate [ Unique ];

}
