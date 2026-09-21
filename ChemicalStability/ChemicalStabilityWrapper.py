###############################################################################
###############################################################################
#                           Chemical Testing Wrapper                          #
#                             Author: Joshua Male                             #
#                              Date: 31/03/2026                               #
#               Description: Chemical Stability Image Processor               #
#                     Project: Chemical Stability Testing                     #
#                                                                             #
#                         Script Designed for Python 3                        #
#           © Copyright Christopher Reardon, Josh Male, PhorestDX             #
#                                                                             #
#                   Software Release: Unreleased/Prototype                    #
###############################################################################
###############################################################################

# Imports
import InitializeChemicalStability  # noqa

import yaml
import logging
import GeneralUtils.FileIO as io

from pathlib import Path

# Start logging
logger = logging.getLogger(name=Path(__file__).stem)

# Configuration
project_root = Path(__file__).resolve().parents[1]
config_path = project_root / 'local_config.yml'
with config_path.open(mode='r', encoding='utf-8') as config_file:
    local_config = yaml.safe_load(config_file)
    logger.info(f'Loaded local configuration from: {config_path}')
plot_config_path = (
    project_root / 'standard_plot_parameters.yml'
)
logger.info(f'Loaded plot configuration from: {plot_config_path}')
with plot_config_path.open(mode='r', encoding='utf-8') as plot_config_file:
    plot_parameters = yaml.safe_load(plot_config_file)
    logger.info(f'Loaded plot parameters from: {plot_config_path}')

# Experimental Parameters
experiment = {
    "Root Path": project_root,
    "Experiment Path": (
        Path(local_config['CHEMICAL_STABILITY_DATA_ROOT']) / 'GMR4'
    ),
    "Results Path": (
        Path(local_config['CHEMICAL_STABILITY_DATA_ROOT']) / 'ProcessedData'
    ),
    "Config File": (
        Path(local_config['CHEMICAL_STABILITY_DATA_ROOT']) /
        'ChemicalStability.json',
    ),
    "Plot": False,
    "Measurement Type": "Chemical Stability",
    "Configuration Filename": "ChemicalStability.json",
    "Chip Type": "Mixed",
    "Process": "All List"
}
logger.info(f'Experimental parameters: {experiment}')

# Load configuration
config = io.ChemicalStabilityConfiguration(parameters=experiment)
