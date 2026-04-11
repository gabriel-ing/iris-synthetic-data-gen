Class Retail.StockTransfers Extends %Persistent [ DdlAllowed, SqlTableName = StockTransfers ]
{

Property TransferNumber As %String(MAXLEN = 40) [ Required ];

Property Product As Retail.Products [ Required ];

Property FromStore As Retail.Stores [ Required ];

Property ToStore As Retail.Stores [ Required ];

Property RequestDate As Retail.Calendar [ Required ];

Property ShipDate As Retail.Calendar [ Required ];

Property ReceiptDate As Retail.Calendar;

Property Quantity As %Integer;

Property Status As %String(MAXLEN = 20);

Property ReasonCode As %String(MAXLEN = 30);

Index TransferNumberIdx On TransferNumber [ Unique ];

Index ProductShipIdx On (Product, ShipDate);

}
