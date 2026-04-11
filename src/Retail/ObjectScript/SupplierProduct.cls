Class Retail.SupplierProduct Extends %Persistent [ DdlAllowed, SqlTableName = SupplierProduct ]
{

Property Product As Retail.Products [ Required ];

Property SupplierCode As %String(MAXLEN = 40);

Property SupplierName As %String(MAXLEN = 120);

Property SupplierCountry As %String(MAXLEN = 10);

Property SupplierTier As %Integer;

Property PreferredSupplierFlag As %Boolean;

Property LeadTimeDays As %Integer;

Property MinOrderQty As %Integer;

Property OrderMultipleQty As %Integer;

Property UnitCost As %Numeric(SCALE = 2);

Property Currency As %String(MAXLEN = 10);

Property RiskScore As %Integer;

Property ShipMode As %String(MAXLEN = 20);

Index ProductSupplierIdx On (Product, SupplierCode) [ Unique ];

Index SupplierCodeIdx On SupplierCode;

}
