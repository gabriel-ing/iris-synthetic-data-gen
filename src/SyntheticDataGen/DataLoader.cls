Include %occInclude

Class SyntheticDataGen.DataLoader Extends %RegisteredObject
{

ClassMethod PersistInstallRoot() As %Status
{
    quit ..SetInstallRoot(..DefaultInstallRoot())
}

ClassMethod DefaultInstallRoot() As %String
{
    set managerDir = $system.Util.ManagerDirectory()
    if managerDir '= "" {
        set sep = $select(managerDir["\\": "\\", 1: "/")
        set installRoot = $replace(managerDir, sep_"mgr"_sep, sep_"lib"_sep_"SyntheticDataGen"_sep)
        if installRoot '= managerDir {
            quit installRoot
        }
    }

    set binaryDir = $system.Util.BinaryDirectory()
    if binaryDir '= "" {
        set sep = $select(binaryDir["\\": "\\", 1: "/")
        set installRoot = $replace(binaryDir, sep_"bin"_sep, sep_"lib"_sep_"SyntheticDataGen"_sep)
        if installRoot '= binaryDir {
            quit installRoot
        }
    }

    quit ""
}

ClassMethod SetInstallRoot(pRoot As %String) As %Status
{
    set installRoot = $zstrip($get(pRoot), "<W")
    if installRoot = "" {
        quit $$$ERROR($$$GeneralError, "SyntheticDataGen install root cannot be empty")
    }

    set sep = $select(installRoot["\\": "\\", 1: "/")
    if $extract(installRoot, *) '= sep {
        set installRoot = installRoot_sep
    }

    set ^SyntheticDataGen("InstallRoot") = installRoot
    quit $$$OK
}

ClassMethod GetInstallRoot() As %String
{
    set installRoot = $zstrip($get(^SyntheticDataGen("InstallRoot")), "<W")
    if installRoot = "" {
        quit ""
    }

    set sep = $select(installRoot["\\": "\\", 1: "/")
    if $extract(installRoot, *) '= sep {
        set installRoot = installRoot_sep
    }

    quit installRoot
}

ClassMethod EnsureDatasetClasses(pDataset As %String) As %Status
{
    set installRoot = ..GetInstallRoot()
    if installRoot = "" {
        quit $$$ERROR($$$GeneralError, "SyntheticDataGen install root is not configured. Reinstall the package or call ##class(SyntheticDataGen.DataLoader).SetInstallRoot().")
    }

    set sep = $select(installRoot["\\": "\\", 1: "/")
    if pDataset = "FinancialServices" {
        set objectScriptRoot = installRoot_"FinancialServices"_sep_"ObjectScript"_sep
        set sentinelClass = "Finance.Customers"
    } elseif pDataset = "SupplyChain" {
        set objectScriptRoot = installRoot_"SupplyChain"_sep_"ObjectScript"_sep
        set sentinelClass = "SupplyChain.DimCustomer"
    } elseif pDataset = "Retail" {
        set objectScriptRoot = installRoot_"Retail"_sep_"ObjectScript"_sep
        set sentinelClass = "Retail.Stores"
    } elseif pDataset = "ThemePark" {
        set objectScriptRoot = installRoot_"ThemePark"_sep_"ObjectScript"_sep
        set sentinelClass = "ThemePark.Parks"
    } else {
        quit $$$ERROR($$$GeneralError, "Invalid dataset. Must be 'FinancialServices', 'SupplyChain', 'Retail', or 'ThemePark'.")
    }

    if $classmethod("%Dictionary.ClassDefinition", "%ExistsId", sentinelClass) {
        quit $$$OK
    }

    if '##class(%File).DirectoryExists(objectScriptRoot) {
        quit $$$ERROR($$$GeneralError, "Dataset ObjectScript source directory not found: "_objectScriptRoot)
    }

    set sc = $system.OBJ.LoadDir(objectScriptRoot, "ck")
    if $$$ISERR(sc) {
        quit sc
    }
    if '$classmethod("%Dictionary.ClassDefinition", "%ExistsId", sentinelClass) {
        quit $$$ERROR($$$GeneralError, "Dataset classes were not compiled for "_pDataset_" from "_objectScriptRoot)
    }

    quit $$$OK
}

ClassMethod DeleteDataset(pDataset As %String, pDeleteClasses As %Integer = 1) As %Status
{
    set sc = $$$OK

    if pDataset = "FinancialServices" {
        set package = "Finance"
        set sentinelClass = "Finance.Customers"
        set deleteOrder = "Finance.Disputes,Finance.Transactions,Finance.Cards,Finance.Accounts,Finance.Merchants,Finance.Customers"
    } elseif pDataset = "SupplyChain" {
        set package = "SupplyChain"
        set sentinelClass = "SupplyChain.DimCustomer"
        set deleteOrder = "SupplyChain.InventorySnapshotDaily,SupplyChain.InventoryMovement,SupplyChain.StockCountEvent,SupplyChain.ShipmentLine,SupplyChain.PurchaseOrderLine,SupplyChain.SalesOrderLine,SupplyChain.PurchaseOrders,SupplyChain.SalesOrders,SupplyChain.ProductSupplier,SupplyChain.DimCustomer,SupplyChain.DimSupplier,SupplyChain.DimLocation,SupplyChain.DimProduct,SupplyChain.DimDate"
    } elseif pDataset = "Retail" {
        set package = "Retail"
        set sentinelClass = "Retail.Stores"
        set deleteOrder = "Retail.InventorySnapshot,Retail.SalesTransactions,Retail.StockTransfers,Retail.PurchaseOrders,Retail.Promotions,Retail.SupplierProduct,Retail.UserStoreAccess,Retail.Users,Retail.Customers,Retail.Products,Retail.Stores,Retail.Roles,Retail.Calendar"
    } elseif pDataset = "ThemePark" {
        set package = "ThemePark"
        set sentinelClass = "ThemePark.Parks"
        set deleteOrder = "ThemePark.Feedback,ThemePark.Incidents,ThemePark.QueueSnapshot,ThemePark.RideMaintenance,ThemePark.Shifts,ThemePark.Tickets,ThemePark.Employees,ThemePark.Guests,ThemePark.Rides,ThemePark.Zones,ThemePark.Parks"
    } else {
        quit $$$ERROR($$$GeneralError, "Invalid dataset. Must be 'FinancialServices', 'SupplyChain', 'Retail', or 'ThemePark'.")
    }

    if $classmethod("%Dictionary.ClassDefinition", "%ExistsId", sentinelClass) {
        for i = 1:1:$length(deleteOrder, ",") {
            set table = $piece(deleteOrder, ",", i)
            set result = ##class(%SQL.Statement).%ExecDirect(, "DELETE FROM "_table)
            if result.%SQLCODE '= 0 {
                set sc = $$$ERROR($$$GeneralError, "Failed to clear "_table_" SQLCODE="_result.%SQLCODE)
                quit
            }
        }

        if $$$ISERR(sc) {
            quit sc
        }

        set result = ##class(%SQL.Statement).%ExecDirect(, "COMMIT")
        if result.%SQLCODE '= 0 {
            quit $$$ERROR($$$GeneralError, "Failed to commit cleanup for "_pDataset_" SQLCODE="_result.%SQLCODE)
        }
    }

    if +$get(pDeleteClasses) && $classmethod("%Dictionary.ClassDefinition", "%ExistsId", sentinelClass) {
        set sc = $system.OBJ.DeletePackage(package)
        if $$$ISERR(sc) {
            quit sc
        }
    }

    quit $$$OK
}

ClassMethod LoadData(pDataset As %String, pScaleFactor As %Integer = "", pConfig As %String = "", pClearExisting As %Integer = 0) As %Status [ Language = python ]
{
        import sys
        import importlib
        from pathlib import Path
        import iris

        dataset = str(pDataset)
        if dataset not in ("FinancialServices", "SupplyChain", "Retail", "ThemePark"):
            raise ValueError("Invalid dataset. Must be 'FinancialServices', 'SupplyChain', 'Retail', or 'ThemePark'.")

        loader = iris.cls("SyntheticDataGen.DataLoader")
        class_definition = iris.cls("%Dictionary.ClassDefinition")
        sentinel = {
            "FinancialServices": "Finance.Customers",
            "SupplyChain": "SupplyChain.DimCustomer",
            "Retail": "Retail.Stores",
            "ThemePark": "ThemePark.Parks",
        }[dataset]
        dataset_classes_already_compiled = bool(class_definition._ExistsId(sentinel))

        install_root = loader.GetInstallRoot()
        if not install_root:
            raise RuntimeError(
                "SyntheticDataGen install root is not configured in ^SyntheticDataGen(\"InstallRoot\"). "
                "Reinstall the package or call ##class(SyntheticDataGen.DataLoader).SetInstallRoot(...)."
            )

        install_root = Path(str(install_root))
        python_root = install_root / dataset / "python"
        sample_config = python_root / "config" / "sample_config.yaml"

        if not python_root.is_dir():
            raise FileNotFoundError(f"Dataset Python directory not found: {python_root}")
        if not sample_config.is_file() and not pConfig:
            raise FileNotFoundError(f"Dataset sample config not found: {sample_config}")

        status = loader.EnsureDatasetClasses(dataset)
        if iris.system.Status.IsError(status):
            raise RuntimeError(iris.system.Status.GetErrorText(status))

        python_root_str = str(python_root)
        if python_root_str in sys.path:
            sys.path.remove(python_root_str)
        sys.path.insert(0, python_root_str)

        for name in list(sys.modules):
            if name == "DataGen" or name.startswith("DataGen."):
                del sys.modules[name]

        importlib.invalidate_caches()

        import DataGen.main_iris as main_iris

        package = {
            "FinancialServices": "Finance",
            "SupplyChain": "SupplyChain",
            "Retail": "Retail",
            "ThemePark": "ThemePark",
        }[dataset]
        clear_existing_requested = str(pClearExisting).strip().lower() in {"1", "true", "t", "yes", "y", "on"}
        clear_existing = clear_existing_requested and dataset_classes_already_compiled
        scale_factor_raw = str(pScaleFactor).strip()
        scale_factor_override = None
        if scale_factor_raw not in {"", "None"}:
            scale_factor_override = int(scale_factor_raw)
            if scale_factor_override <= 0:
                raise ValueError("Scale factor override must be a positive integer.")
        config_path = pConfig if pConfig else str(sample_config)
        main_iris.main(
            config_path=config_path,
            package=package,
            clear_existing=clear_existing,
            scale_factor_override=scale_factor_override,
        )
}

}
