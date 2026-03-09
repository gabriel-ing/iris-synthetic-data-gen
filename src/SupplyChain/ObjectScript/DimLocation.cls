Class SupplyChain.DimLocation Extends %Persistent [ DdlAllowed, SqlTableName = DimLocation ]
{

Property LocationCode As %String(MAXLEN = 40) [ Required ];

Property LocationName As %String(MAXLEN = 120);

Property LocationType As %String(MAXLEN = 40);

Property Country As %String(MAXLEN = 5);

Property Region As %String(MAXLEN = 40);

Property City As %String(MAXLEN = 80);

Property Postcode As %String(MAXLEN = 20);

Property TimeZone As %String(MAXLEN = 60);

Property IsActive As %Boolean;

Index LocationCodeIdx On LocationCode [ Unique ];

Index TypeIdx On LocationType;

Index RegionIdx On Region;

Index CountryIdx On Country;

Index ActiveIdx On IsActive;


}
