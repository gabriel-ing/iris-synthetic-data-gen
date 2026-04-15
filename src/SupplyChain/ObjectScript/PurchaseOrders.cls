Class SupplyChain.PurchaseOrders Extends %Persistent [ DdlAllowed, SqlTableName = PurchaseOrders ]
{

Property PurchaseOrderId As %String(MAXLEN = 40) [ Required ];

Property Supplier As SupplyChain.DimSupplier [ Required ];

Property ShipFromLocation As SupplyChain.DimLocation;

Property DeliverToLocation As SupplyChain.DimLocation [ Required ];

Property OrderDate As SupplyChain.DimDate [ Required ];

Property ExpectedReceiptDate As SupplyChain.DimDate [ Required ];

Property ReceiptDate As SupplyChain.DimDate;

Property Status As %String(MAXLEN = 30);

Property OrderLineCount As %Integer;

Property OrderedQtyTotal As %Numeric(SCALE = 2);

Property ReceivedQtyTotal As %Numeric(SCALE = 2);

Property OrderValue As %Numeric(SCALE = 2);

Property LateReceiptFlag As %Boolean;

Index PurchaseOrderIdIdx On PurchaseOrderId [ Unique ];

Index SupplierIdx On Supplier;

}