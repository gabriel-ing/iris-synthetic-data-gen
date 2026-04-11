Class Retail.Roles Extends %Persistent [ DdlAllowed, SqlTableName = Roles ]
{

Property RoleName As %String(MAXLEN = 80) [ Required ];

Property AccessLevel As %String(MAXLEN = 30);

Property ToolTier As %String(MAXLEN = 20);

Property CanSeeCostData As %Boolean;

Property CanSeeSupplierData As %Boolean;

Property CanSeeChainwidePricing As %Boolean;

Property CanSeeInventoryForecast As %Boolean;

Index RoleNameIdx On RoleName [ Unique ];

}
