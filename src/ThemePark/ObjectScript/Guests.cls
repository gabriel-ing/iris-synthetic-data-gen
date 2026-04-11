Class ThemePark.Guests Extends %Persistent [ DdlAllowed, SqlTableName = Guests ]
{

Property GuestNumber As %String(MAXLEN = 40) [ Required ];

Property HomeCountry As %String(MAXLEN = 5);

Property Segment As %String(MAXLEN = 30);

Property AgeBand As %String(MAXLEN = 20);

Property PartySize As %Integer;

Property AccessibilityNeeds As %String(MAXLEN = 30);

Property LoyaltyTier As %String(MAXLEN = 30);

Property VisitIntent As %String(MAXLEN = 30);

Index GuestNumberIdx On GuestNumber [ Unique ];

Index SegmentIdx On Segment;

Index LoyaltyTierIdx On LoyaltyTier;

Storage Default
{
<Data name="GuestsDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>GuestNumber</Value>
</Value>
<Value name="3">
<Value>HomeCountry</Value>
</Value>
<Value name="4">
<Value>Segment</Value>
</Value>
<Value name="5">
<Value>AgeBand</Value>
</Value>
<Value name="6">
<Value>PartySize</Value>
</Value>
<Value name="7">
<Value>AccessibilityNeeds</Value>
</Value>
<Value name="8">
<Value>LoyaltyTier</Value>
</Value>
<Value name="9">
<Value>VisitIntent</Value>
</Value>
</Data>
<DataLocation>^ThemePark.GuestsD</DataLocation>
<DefaultData>GuestsDefaultData</DefaultData>
<IdLocation>^ThemePark.GuestsD</IdLocation>
<IndexLocation>^ThemePark.GuestsI</IndexLocation>
<StreamLocation>^ThemePark.GuestsS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
