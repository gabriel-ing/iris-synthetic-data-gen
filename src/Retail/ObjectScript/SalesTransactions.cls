Class Retail.SalesTransactions Extends %Persistent [ DdlAllowed, SqlTableName = SalesTransactions ]
{

Property TransactionNumber As %String(MAXLEN = 50) [ Required ];

Property BasketNumber As %String(MAXLEN = 40);

Property TransactionDate As Retail.Calendar [ Required ];

Property Store As Retail.Stores [ Required ];

Property Customer As Retail.Customers [ Required ];

Property Product As Retail.Products [ Required ];

Property Channel As %String(MAXLEN = 30);

Property PaymentMethod As %String(MAXLEN = 30);

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

Index CustomerDateIdx On (Customer, TransactionDate);

Index ProductDateIdx On (Product, TransactionDate);

Storage Default
{
<Data name="SalesTransactionsDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>TransactionNumber</Value>
</Value>
<Value name="3">
<Value>BasketNumber</Value>
</Value>
<Value name="4">
<Value>TransactionDate</Value>
</Value>
<Value name="5">
<Value>Store</Value>
</Value>
<Value name="6">
<Value>Customer</Value>
</Value>
<Value name="7">
<Value>Product</Value>
</Value>
<Value name="8">
<Value>Channel</Value>
</Value>
<Value name="9">
<Value>PaymentMethod</Value>
</Value>
<Value name="10">
<Value>Units</Value>
</Value>
<Value name="11">
<Value>GrossSalesAmount</Value>
</Value>
<Value name="12">
<Value>DiscountAmount</Value>
</Value>
<Value name="13">
<Value>NetSalesAmount</Value>
</Value>
<Value name="14">
<Value>CogsAmount</Value>
</Value>
<Value name="15">
<Value>Promotion</Value>
</Value>
<Value name="16">
<Value>FulfillmentType</Value>
</Value>
<Value name="17">
<Value>ReturnFlag</Value>
</Value>
<Value name="18">
<Value>StockoutFlag</Value>
</Value>
</Data>
<DataLocation>^Retail.SalesTransactionsD</DataLocation>
<DefaultData>SalesTransactionsDefaultData</DefaultData>
<IdLocation>^Retail.SalesTransactionsD</IdLocation>
<IndexLocation>^Retail.SalesTransactionsI</IndexLocation>
<StreamLocation>^Retail.SalesTransactionsS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
