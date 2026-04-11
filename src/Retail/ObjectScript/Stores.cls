Class Retail.Stores Extends %Persistent [ DdlAllowed, SqlTableName = Stores ]
{

Property StoreCode As %String(MAXLEN = 40) [ Required ];

Property StoreName As %String(MAXLEN = 120);

Property StoreFormat As %String(MAXLEN = 40);

Property Region As %String(MAXLEN = 20);

Property District As %String(MAXLEN = 20);

Property City As %String(MAXLEN = 40);

Property State As %String(MAXLEN = 10);

Property OpenDate As %TimeStamp;

Property SquareFeet As %Integer;

Property ActiveFlag As %Boolean;

Index StoreCodeIdx On StoreCode [ Unique ];

Index RegionIdx On Region;

Index FormatIdx On StoreFormat;

}
