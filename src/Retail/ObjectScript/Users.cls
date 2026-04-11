Class Retail.Users Extends %Persistent [ DdlAllowed, SqlTableName = Users ]
{

Property UserName As %String(MAXLEN = 60) [ Required ];

Property FullName As %String(MAXLEN = 120);

Property Email As %String(MAXLEN = 180);

Property RoleRef As Retail.Roles [ Required ];

Property AccessScope As %String(MAXLEN = 20);

Property ToolTier As %String(MAXLEN = 20);

Property CategoryScope As %String(MAXLEN = 40);

Property Region As %String(MAXLEN = 20);

Property PrimaryStore As Retail.Stores [ Required ];

Property CreatedAt As %TimeStamp;

Property ActiveFlag As %Boolean;

Index UserNameIdx On UserName [ Unique ];

Index AccessScopeIdx On AccessScope;

}
