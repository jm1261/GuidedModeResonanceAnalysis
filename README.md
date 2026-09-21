# GMRProcessor

`GMRProcessor` processes guided-mode resonance (GMR) image data. It contains
configuration models, image loading and analysis, region-of-interest (ROI)
support, experiment workflows, chemical-stability entry points, plotting
helpers, and logging.

See the detailed [GMRProcessor architecture](architecture.md) for component
ownership and data flow.

The repository pins Python with `.python-version`, installs dependencies from
`requirements.txt`, and runs its tests through `.github/workflows/ci.yml`.

## Setup

From the repository root, create or activate a Python environment and install
the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

Copy `local_config.example.yml` to the ignored `local_config.yml` file and set
paths for the data workflow you intend to run:

```yaml
PHOREST_DATA_ROOT: D:/data/phorest
CHEMICAL_STABILITY_DATA_ROOT: D:/data/chemical-stability
```

`GMR_DATA_ROOT` may be retained for local compatibility, but the current
scripts do not read it. `standard_plot_parameters.yml` contains the plotting
defaults used by GMR workflow entry points.

## Components

- `Config/` stores default YAML configuration and sensor geometry files.
- `GeneralUtils/` provides configuration models, path helpers, metadata, CSV
  output, and shared plotting helpers.
- `ImageUtils/` loads images, performs Gaussian, Fano, hybrid, centre, and
  maximum-intensity analysis, and defines ROI locator interfaces.
- `DataUtils/` contains data-processing helpers used by experiment scripts.
- `ExperimentScripts/` contains the time-experiment entry point and its logging
  bootstrap.
- `ChemicalStability/` contains chemical-stability workflow entry points.
- `Logging/` contains the logging configuration and log cleanup command.

## Running workflows

The time experiment requires `PHOREST_DATA_ROOT` and expects its input under
`SodiumHydroxideExperiment/ID0512`:

```powershell
python ExperimentScripts/TimeExperiment.py
```

Initialize the relevant logging area directly when testing a bootstrap:

```powershell
python ExperimentScripts/InitializeScripts.py
python GeneralUtils/InitializeGeneralUtils.py
python ImageUtils/InitializeImageUtils.py
```

Preview cleanup of application logs before deleting them:

```powershell
python Logging/cleanup_logs.py --dry-run
```

Run the focused tests from the repository root:

```powershell
python -m unittest discover --start-directory tests --pattern "test_*.py" --verbose
```

## Current limitations

The ROI locator implementations and several chemical-stability processing
functions are incomplete. The time-experiment workflow also contains processing
and plotting sections that are still under development. This repository is
self-contained when cloned independently.
