Class ThemePark.Feedback Extends %Persistent [ DdlAllowed, SqlTableName = Feedback ]
{

Property FeedbackNumber As %String(MAXLEN = 50) [ Required ];

Property Ticket As ThemePark.Tickets [ Required ];

Property Park As ThemePark.Parks [ Required ];

Property Ride As ThemePark.Rides;

Property SubmittedAt As %TimeStamp;

Property Channel As %String(MAXLEN = 30);

Property Rating As %Integer;

Property Sentiment As %String(MAXLEN = 20);

Property Topic As %String(MAXLEN = 40);

Property Summary As %String(MAXLEN = 240);

Property RequiresFollowUp As %Boolean;

Index FeedbackNumberIdx On FeedbackNumber [ Unique ];

Index ParkSubmittedIdx On (Park, SubmittedAt);

Index TicketIdx On Ticket;

Storage Default
{
<Data name="FeedbackDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>FeedbackNumber</Value>
</Value>
<Value name="3">
<Value>Ticket</Value>
</Value>
<Value name="4">
<Value>Park</Value>
</Value>
<Value name="5">
<Value>Ride</Value>
</Value>
<Value name="6">
<Value>SubmittedAt</Value>
</Value>
<Value name="7">
<Value>Channel</Value>
</Value>
<Value name="8">
<Value>Rating</Value>
</Value>
<Value name="9">
<Value>Sentiment</Value>
</Value>
<Value name="10">
<Value>Topic</Value>
</Value>
<Value name="11">
<Value>Summary</Value>
</Value>
<Value name="12">
<Value>RequiresFollowUp</Value>
</Value>
</Data>
<DataLocation>^ThemePark.FeedbackD</DataLocation>
<DefaultData>FeedbackDefaultData</DefaultData>
<IdLocation>^ThemePark.FeedbackD</IdLocation>
<IndexLocation>^ThemePark.FeedbackI</IndexLocation>
<StreamLocation>^ThemePark.FeedbackS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}