Class Retail.SalesTransactions Extends %Persistent [ DdlAllowed, SqlTableName = SalesTransactions ]
{

Property TransactionNumber As %String(MAXLEN = 50) [ Required ];

Property TransactionDate As Retail.Calendar [ Required ];

Property Store As Retail.Stores [ Required ];

Property Product As Retail.Products [ Required ];

Property Channel As %String(MAXLEN = 30);

Property Units As %Integer;

Property GrossSalesAmount As %Numeric(SCALE = 2);

Property DiscountAmount As %Numeric(SCALE = 2);

Property NetSalesAmount As %Numeric(SCALE = 2);

Property CogsAmount As %Numeric(SCALE = 2);

Property Promotion As Retail.Promotions;

Property FulfillmentType As %String(MAXLEN = 30);

Property ReturnFlag As %Boolean;

Property StockoutFlag As %Boolean;

Index TransactionNumberIdx On TransactionNumber [ Unique ];

Index StoreDateIdx On (Store, TransactionDate);

Index ProductDateIdx On (Product, TransactionDate);

}
