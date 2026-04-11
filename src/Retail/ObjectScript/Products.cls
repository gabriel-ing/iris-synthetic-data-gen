Class Retail.Products Extends %Persistent [ DdlAllowed, SqlTableName = Products ]
{

Property Sku As %String(MAXLEN = 40) [ Required ];

Property ProductName As %String(MAXLEN = 120);

Property Department As %String(MAXLEN = 40);

Property Category As %String(MAXLEN = 40);

Property Subcategory As %String(MAXLEN = 60);

Property Brand As %String(MAXLEN = 60);

Property PrivateLabelFlag As %Boolean;

Property Seasonality As %String(MAXLEN = 30);

Property UnitSize As %String(MAXLEN = 30);

Property BaseUnitCost As %Numeric(SCALE = 2);

Property BaseRegularPrice As %Numeric(SCALE = 2);

Property LaunchDate As Retail.Calendar;

Property DiscontinueDate As Retail.Calendar;

Index SkuIdx On Sku [ Unique ];

Index DepartmentIdx On Department;

Index CategoryIdx On Category;

}
