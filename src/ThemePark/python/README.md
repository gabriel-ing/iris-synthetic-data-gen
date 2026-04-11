# Theme Park Synthetic Data Generator

This package generates the Theme Park Management demo dataset used by the root SyntheticDataGen module.

## Outputs

- `parks.csv`
- `zones.csv`
- `rides.csv`
- `ride_maintenance.csv`
- `employees.csv`
- `shifts.csv`
- `guests.csv`
- `tickets.csv`
- `incidents.csv`
- `feedback.csv`

## CSV Generation

From `src/ThemePark/python`:

```bash
python -m DataGen.main --config config/sample_config.yaml
python -m DataGen.main --config config/sample_config.yaml --scale-factor 2
```

The output directory is controlled by the YAML config.

## Direct IRIS Insert

From `src/ThemePark/python`:

```bash
python -m DataGen.main_iris --config config/sample_config.yaml --package ThemePark --clear-existing
```

Current `main_iris.py` options:

- `--config`
- `--package` with default `ThemePark`
- `--clear-existing`
- `--commit-every`
- `--scale-factor`

## Tests

From `src/ThemePark/python`:

```bash
python -m pytest
```

## Through ZPM

After installing the root module in IRIS:

```objectscript
do ##class(SyntheticDataGen.DataLoader).LoadData("ThemePark")
do ##class(SyntheticDataGen.DataLoader).LoadData("ThemePark",2)
do ##class(SyntheticDataGen.DataLoader).DeleteDataset("ThemePark")
```

`ThemePark.Parks` is the lazy-compile sentinel class for this domain.
