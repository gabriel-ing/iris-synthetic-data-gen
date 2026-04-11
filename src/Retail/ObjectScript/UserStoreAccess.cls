Class Retail.UserStoreAccess Extends %Persistent [ DdlAllowed, SqlTableName = UserStoreAccess ]
{

Property UserRef As Retail.Users [ Required ];

Property Store As Retail.Stores [ Required ];

Property AccessType As %String(MAXLEN = 20);

Index UserStoreIdx On (UserRef, Store) [ Unique ];

Index StoreIdx On Store;

}
