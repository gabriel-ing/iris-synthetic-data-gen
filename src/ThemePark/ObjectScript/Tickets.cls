Class ThemePark.Tickets Extends %Persistent [ DdlAllowed, SqlTableName = Tickets ]
{

Property TicketCode As %String(MAXLEN = 50) [ Required ];

Property Guest As ThemePark.Guests [ Required ];

Property Park As ThemePark.Parks [ Required ];

Property VisitDate As %TimeStamp;

Property TicketType As %String(MAXLEN = 30);

Property EntryChannel As %String(MAXLEN = 30);

Property PricePaid As %Numeric(SCALE = 2);

Property FastAccessFlag As %Boolean;

Property AddOnBundle As %String(MAXLEN = 40);

Property TicketStatus As %String(MAXLEN = 20);

Index TicketCodeIdx On TicketCode [ Unique ];

Index ParkVisitIdx On (Park, VisitDate);

Index GuestVisitIdx On (Guest, VisitDate);

Storage Default
{
<Data name="TicketsDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>TicketCode</Value>
</Value>
<Value name="3">
<Value>Guest</Value>
</Value>
<Value name="4">
<Value>Park</Value>
</Value>
<Value name="5">
<Value>VisitDate</Value>
</Value>
<Value name="6">
<Value>TicketType</Value>
</Value>
<Value name="7">
<Value>EntryChannel</Value>
</Value>
<Value name="8">
<Value>PricePaid</Value>
</Value>
<Value name="9">
<Value>FastAccessFlag</Value>
</Value>
<Value name="10">
<Value>AddOnBundle</Value>
</Value>
<Value name="11">
<Value>TicketStatus</Value>
</Value>
</Data>
<DataLocation>^ThemePark.TicketsD</DataLocation>
<DefaultData>TicketsDefaultData</DefaultData>
<IdLocation>^ThemePark.TicketsD</IdLocation>
<IndexLocation>^ThemePark.TicketsI</IndexLocation>
<StreamLocation>^ThemePark.TicketsS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
