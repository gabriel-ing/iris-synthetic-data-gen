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
        set requiredClasses = "Finance.Customers,Finance.Accounts,Finance.Cards,Finance.Merchants,Finance.Transactions,Finance.Disputes"
    } elseif pDataset = "SupplyChain" {
        set objectScriptRoot = installRoot_"SupplyChain"_sep_"ObjectScript"_sep
        set sentinelClass = "SupplyChain.DimCustomer"
        set requiredClasses = "SupplyChain.DimDate,SupplyChain.DimProduct,SupplyChain.DimLocation,SupplyChain.DimSupplier,SupplyChain.DimCustomer,SupplyChain.ProductSupplier,SupplyChain.SalesOrders,SupplyChain.PurchaseOrders,SupplyChain.SalesOrderLine,SupplyChain.PurchaseOrderLine,SupplyChain.ShipmentLine,SupplyChain.InventoryMovement,SupplyChain.InventorySnapshotDaily,SupplyChain.StockCountEvent"
    } elseif pDataset = "Retail" {
        set objectScriptRoot = installRoot_"Retail"_sep_"ObjectScript"_sep
        set sentinelClass = "Retail.Stores"
        set requiredClasses = "Retail.Calendar,Retail.Roles,Retail.Users,Retail.UserStoreAccess,Retail.Stores,Retail.Customers,Retail.Products,Retail.SupplierProduct,Retail.Promotions,Retail.PurchaseOrders,Retail.StockTransfers,Retail.SalesTransactions,Retail.InventorySnapshot"
    } elseif pDataset = "ThemePark" {
        set objectScriptRoot = installRoot_"ThemePark"_sep_"ObjectScript"_sep
        set sentinelClass = "ThemePark.Parks"
        set requiredClasses = "ThemePark.Parks,ThemePark.Zones,ThemePark.Rides,ThemePark.RideMaintenance,ThemePark.QueueSnapshot,ThemePark.Employees,ThemePark.Shifts,ThemePark.Guests,ThemePark.Tickets,ThemePark.Incidents,ThemePark.Feedback"
    } else {
        quit $$$ERROR($$$GeneralError, "Invalid dataset. Must be 'FinancialServices', 'SupplyChain', 'Retail', or 'ThemePark'.")
    }

    if '##class(%File).DirectoryExists(objectScriptRoot) {
        quit $$$ERROR($$$GeneralError, "Dataset ObjectScript source directory not found: "_objectScriptRoot)
    }

    set sc = $system.OBJ.LoadDir(objectScriptRoot, "ck")
    if $$$ISERR(sc) {
        quit sc
    }

    for i = 1:1:$length(requiredClasses, ",") {
        set className = $piece(requiredClasses, ",", i)
        if '$classmethod("%Dictionary.CompiledClass", "%ExistsId", className) {
            set sc = $$$ERROR($$$GeneralError, "Dataset classes were not compiled for "_pDataset_" from "_objectScriptRoot_". Missing compiled class "_className)
            quit
        }
    }

    if $$$ISERR(sc) {
        quit sc
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
            if result.%SQLCODE '= 0, result.%SQLCODE '= 100 {
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

ClassMethod RunSmokeTest(pScaleFactor As %Integer = 1) As %Status [ Language = python ]
{
        import sys
        import importlib
        import tempfile
        from pathlib import Path

        import yaml
        import iris

        loader = iris.cls("SyntheticDataGen.DataLoader")

        scale_raw = str(pScaleFactor).strip()
        scale_factor = int(scale_raw or "1")
        if scale_factor <= 0:
            raise ValueError("Smoke test scale factor must be a positive integer.")

        install_root = loader.GetInstallRoot()
        if not install_root:
            raise RuntimeError(
                'SyntheticDataGen install root is not configured in ^SyntheticDataGen("InstallRoot"). '
                "Reinstall the package or call ##class(SyntheticDataGen.DataLoader).SetInstallRoot(...)."
            )

        install_root = Path(str(install_root))
        datasets = [
            ("FinancialServices", "Finance"),
            ("SupplyChain", "SupplyChain"),
            ("Retail", "Retail"),
            ("ThemePark", "ThemePark"),
        ]
        smoke_overrides = {
            "FinancialServices": {
                "time": {"days": 14},
                "scale": {
                    "mode": "factor",
                    "factor": scale_factor,
                    "base_counts": {
                        "customers": 12,
                        "merchants": 8,
                        "cards": 16,
                        "transactions": 80,
                        "disputes": 4,
                    },
                },
            },
            "SupplyChain": {
                "time": {"days": 60},
                "scale": {
                    "mode": "factor",
                    "factor": scale_factor,
                    "base_counts": {
                        "products": 40,
                        "locations": 12,
                        "suppliers": 20,
                        "customers": 60,
                        "product_suppliers": 100,
                        "sales_order_lines": 300,
                        "purchase_order_lines": 120,
                        "stock_count_events": 24,
                    },
                },
            },
            "Retail": {
                "time": {"days": 21},
                "scale": {
                    "mode": "factor",
                    "factor": scale_factor,
                    "base_counts": {
                        "users": 10,
                        "stores": 6,
                        "products": 18,
                        "supplier_products": 28,
                        "promotions": 8,
                        "purchase_orders": 24,
                        "stock_transfers": 10,
                        "sales_transactions": 120,
                        "inventory_snapshots": 72,
                    },
                },
            },
            "ThemePark": {
                "time": {"days": 30},
                "scale": {
                    "mode": "factor",
                    "factor": scale_factor,
                    "base_counts": {
                        "parks": 4,
                        "zones": 12,
                        "rides": 24,
                        "ride_maintenance": 36,
                        "employees": 48,
                        "shifts": 160,
                        "guests": 120,
                        "tickets": 180,
                        "incidents": 24,
                        "feedback": 72,
                    },
                },
            },
        }

        def _load_domain_modules(dataset_name: str):
            python_root = install_root / dataset_name / "python"
            if not python_root.is_dir():
                raise FileNotFoundError(f"Dataset Python directory not found: {python_root}")

            python_root_str = str(python_root)
            if python_root_str in sys.path:
                sys.path.remove(python_root_str)
            sys.path.insert(0, python_root_str)

            for name in list(sys.modules):
                if name == "DataGen" or name.startswith("DataGen."):
                    del sys.modules[name]

            importlib.invalidate_caches()

            import DataGen.config as dataset_config
            import DataGen.main_iris as main_iris

            return dataset_config, main_iris

        for dataset, package in datasets:
            status = loader.EnsureDatasetClasses(dataset)
            if iris.system.Status.IsError(status):
                raise RuntimeError(iris.system.Status.GetErrorText(status))

            dataset_config, main_iris = _load_domain_modules(dataset)
            config = dataset_config._deep_merge(dataset_config._default_config(), smoke_overrides[dataset])

            with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as handle:
                yaml.safe_dump(config, handle, sort_keys=False)
                temp_config_path = handle.name

            try:
                print(f"Smoke loading {dataset} with scale factor {scale_factor}")
                main_iris.main(
                    config_path=temp_config_path,
                    package=package,
                    clear_existing=True,
                )
            finally:
                Path(temp_config_path).unlink(missing_ok=True)
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
        compiled_class = iris.cls("%Dictionary.CompiledClass")
        sentinel = {
            "FinancialServices": "Finance.Customers",
            "SupplyChain": "SupplyChain.DimCustomer",
            "Retail": "Retail.Stores",
            "ThemePark": "ThemePark.Parks",
        }[dataset]
        dataset_classes_already_compiled = bool(compiled_class._ExistsId(sentinel))

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
