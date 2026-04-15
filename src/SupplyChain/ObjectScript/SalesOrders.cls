Class SupplyChain.SalesOrders Extends %Persistent [ DdlAllowed, SqlTableName = SalesOrders ]
{

Property SalesOrderId As %String(MAXLEN = 40) [ Required ];

Property Customer As SupplyChain.DimCustomer [ Required ];

Property ShipFromLocation As SupplyChain.DimLocation [ Required ];

Property ShipToLocation As SupplyChain.DimLocation [ Required ];

Property OrderDate As SupplyChain.DimDate [ Required ];

Property RequestedShipDate As SupplyChain.DimDate [ Required ];

Property PromisedDeliveryDate As SupplyChain.DimDate [ Required ];

Property ActualDeliveryDate As SupplyChain.DimDate;

Property Status As %String(MAXLEN = 30);

Property Channel As %String(MAXLEN = 20);

Property OrderLineCount As %Integer;

Property OrderedQtyTotal As %Numeric(SCALE = 2);

Property ShippedQtyTotal As %Numeric(SCALE = 2);

Property BackorderedQtyTotal As %Numeric(SCALE = 2);

Property OrderValue As %Numeric(SCALE = 2);

Index SalesOrderIdIdx On SalesOrderId [ Unique ];

Index CustomerIdx On Customer;

}