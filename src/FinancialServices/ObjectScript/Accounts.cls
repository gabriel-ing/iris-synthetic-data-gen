Class Finance.Accounts Extends %Persistent [ DdlAllowed, SqlTableName = Accounts ]
{

Property AccountNumber As %String(MAXLEN = 40) [ Required ];

Property Customer As Finance.Customers [ Required ];

Property AccountType As %String(MAXLEN = 30);

Property Status As %String(MAXLEN = 20);

Property OpenedAt As %String(MAXLEN = 35);

Property ClosedAt As %String(MAXLEN = 35);

Property BillingCycleDay As %Integer;

Property AutopayFlag As %Boolean;

Index AccountNumberIdx On AccountNumber [ Unique ];

Index CustomerIdx On Customer;

}