# IRIS Embedded Python SQLError 246 Troubleshooting

## Symptom

You see an error like:

```text
<THROW> ... <PYTHON EXCEPTION> 246 <class 'irisbuiltins.SQLError'>:
```

with no useful SQL text after the colon.

## Current Fastest Reset Path

For the most common rerun failures, clear the dataset and reload it through `SyntheticDataGen.DataLoader`.

From an IRIS session:

```objectscript
do ##class(SyntheticDataGen.DataLoader).DeleteDataset("FinancialServices")
do ##class(SyntheticDataGen.DataLoader).LoadData("FinancialServices")
```

If you want to keep the compiled classes in place while clearing the rows:

```objectscript
do ##class(SyntheticDataGen.DataLoader).DeleteDataset("FinancialServices",0)
do ##class(SyntheticDataGen.DataLoader).LoadData("FinancialServices")
```

## Current Loader Contract

Current shared IRIS loader class:

- `SyntheticDataGen.DataLoader`

Current key methods:

- `EnsureDatasetClasses(dataset)`
- `LoadData(dataset, scaleFactor="", configPath="", clearExisting=0)`
- `DeleteDataset(dataset, deleteClasses=1)`

Valid dataset names:

- `FinancialServices`
- `SupplyChain`
- `Retail`
- `ThemePark`

Important positional order for `LoadData()`:
1. dataset
2. scale factor
3. config path
4. clear-existing flag

Incorrect positional arguments are one of the easier ways to get confusing embedded Python failures.

## Current Package and Sentinel Map

- `FinancialServices` -> package `Finance` -> sentinel `Finance.Customers`
- `SupplyChain` -> package `SupplyChain` -> sentinel `SupplyChain.DimCustomer`
- `Retail` -> package `Retail` -> sentinel `Retail.Stores`
- `ThemePark` -> package `ThemePark` -> sentinel `ThemePark.Parks`

## Basic Checks

From an IRIS session:

```objectscript
write $get(^SyntheticDataGen("InstallRoot")),!
write $classmethod("%Dictionary.ClassDefinition","%ExistsId","Finance.Customers"),!
write $classmethod("%Dictionary.ClassDefinition","%ExistsId","SupplyChain.DimCustomer"),!
write $classmethod("%Dictionary.ClassDefinition","%ExistsId","Retail.Stores"),!
write $classmethod("%Dictionary.ClassDefinition","%ExistsId","ThemePark.Parks"),!
```

If the install root is blank, reinstall the module or call `SetInstallRoot(...)` explicitly.

## Manual Child-First Clear Orders

`DeleteDataset()` already knows these orders. Use them only if you are isolating individual SQL statements.

Financial Services:

```text
Finance.Disputes
Finance.Transactions
Finance.Cards
Finance.Merchants
Finance.Customers
```

Supply Chain:

```text
SupplyChain.InventorySnapshotDaily
SupplyChain.InventoryMovement
SupplyChain.StockCountEvent
SupplyChain.ShipmentLine
SupplyChain.PurchaseOrderLine
SupplyChain.SalesOrderLine
SupplyChain.ProductSupplier
SupplyChain.DimCustomer
SupplyChain.DimSupplier
SupplyChain.DimLocation
SupplyChain.DimProduct
SupplyChain.DimDate
```

Retail:

```text
Retail.InventorySnapshot
Retail.SalesTransactions
Retail.StockTransfers
Retail.PurchaseOrders
Retail.Promotions
Retail.SupplierProduct
Retail.UserStoreAccess
Retail.Users
Retail.Products
Retail.Stores
Retail.Roles
Retail.Calendar
```

Theme Park:

```text
ThemePark.Feedback
ThemePark.Incidents
ThemePark.RideMaintenance
ThemePark.Shifts
ThemePark.Tickets
ThemePark.Employees
ThemePark.Guests
ThemePark.Rides
ThemePark.Zones
ThemePark.Parks
```

## Known Project-Specific Causes

- Duplicate keys or unique-index collisions from prior partial loads.
- Stale cached `DataGen` modules in embedded Python after switching domains or rerunning in the same session.
- Incorrect positional arguments passed to `LoadData()`.
- Datatype mismatches in embedded Python SQL binding.
- Financial Services boolean-like fields must bind as `0` and `1` for integer-backed IRIS columns.
- The Supply Chain IRIS loader is most reliable when nullable values are passed as empty strings in this environment and `%Date` values are passed as IRIS logical-date integers.

## Isolate the First Failing Statement

Use embedded Python in IRIS to run one statement at a time:

```bash
cat <<'EOF' | docker-compose exec -T iris iris session iris
zn "USER"
do ##class(%SYS.Python).Run("import iris; s=iris.sql.prepare('DELETE FROM Finance.Disputes'); s.execute(); print('ok disputes')")
do ##class(%SYS.Python).Run("import iris; s=iris.sql.prepare('DELETE FROM Finance.Transactions'); s.execute(); print('ok txns')")
halt
EOF
```

Apply the same pattern to insert statements if a delete succeeds but the load still fails.

## Reinstall or Recompile the Loader

If the runtime behavior does not match the code on disk, reload the module into the container:

```bash
cat <<'EOF' | docker-compose exec -T iris iris session iris
zn "USER"
zpm "load /home/irisowner/dev -v"
halt
EOF
```

Then retry the failing `LoadData(...)` call.

## Minimal Handoff Data

If the error remains blank, collect:

- exact command used
- dataset name
- the full `LoadData()` or `DeleteDataset()` call
- whether the dataset already existed in IRIS
- the first individual SQL statement that fails when executed alone
- current row counts for the affected tables

That is usually enough to identify whether the failure is a constraint violation, a stale-code problem, or a binding issue.