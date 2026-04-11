Class Retail.Promotions Extends %Persistent [ DdlAllowed, SqlTableName = Promotions ]
{

Property PromotionCode As %String(MAXLEN = 40) [ Required ];

Property Product As Retail.Products [ Required ];

Property Store As Retail.Stores;

Property StartDate As Retail.Calendar [ Required ];

Property EndDate As Retail.Calendar [ Required ];

Property PromoType As %String(MAXLEN = 30);

Property DiscountPct As %Numeric(SCALE = 4);

Property PromoPrice As %Numeric(SCALE = 2);

Property ExpectedLiftPct As %Numeric(SCALE = 4);

Property FundingSource As %String(MAXLEN = 20);

Index PromotionCodeIdx On PromotionCode [ Unique ];

Index ProductDateIdx On (Product, StartDate, EndDate);

}
