Class Retail.PurchaseOrders Extends %Persistent [ DdlAllowed, SqlTableName = PurchaseOrders ]
{

Property PoNumber As %String(MAXLEN = 40) [ Required ];

Property Store As Retail.Stores [ Required ];

Property SupplierProduct As Retail.SupplierProduct [ Required ];

Property OrderDate As Retail.Calendar [ Required ];

Property ExpectedReceiptDate As Retail.Calendar [ Required ];

Property ActualReceiptDate As Retail.Calendar;

Property OrderedQty As %Integer;

Property ReceivedQty As %Integer;

Property UnitCost As %Numeric(SCALE = 2);

Property Status As %String(MAXLEN = 20);

Property UrgentFlag As %Boolean;

Index PoNumberIdx On PoNumber [ Unique ];

Index StoreDateIdx On (Store, OrderDate);

}
