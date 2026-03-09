Class SyntheticDataGen.DataLoader Extends %RegisteredObject
{

ClassMethod LoadData(pDataset As %String, pConfig As %String = "", pClearExisting As %Integer = 0) As %Status [ Language = python ]
{
        import sys
        import importlib
        import iris 

        def _to_bool(value):
            if isinstance(value, bool):
                return value
            if value is None:
                return False
            return str(value).strip().lower() in {"1", "true", "t", "yes", "y", "on"}

        # Check if dataset is valid
        if pDataset not in ["FinancialServices", "SupplyChain"]:
            raise ValueError("Invalid dataset. Must be 'FinancialServices' or 'SupplyChain'.") 

        iris._SYSTEM.OBJ.Import(f'/home/irisowner/dev/src/{pDataset}/ObjectScript')

        python_root = f'/home/irisowner/dev/src/{pDataset}/python'
        if python_root in sys.path:
            sys.path.remove(python_root)
        sys.path.insert(0, python_root)

        # Ensure the DataGen package is reloaded from the selected dataset path.
        for name in list(sys.modules):
            if name == "DataGen" or name.startswith("DataGen."):
                del sys.modules[name]

        importlib.invalidate_caches()

        import DataGen.main_iris as main_iris

        package = "Finance" if pDataset == "FinancialServices" else "SupplyChain"
        config_path = pConfig if pConfig else f"{python_root}/config/sample_config.yaml"
        main_iris.main(
            config_path=config_path,
            package=package,
            clear_existing=_to_bool(pClearExisting),
        )
}

}
