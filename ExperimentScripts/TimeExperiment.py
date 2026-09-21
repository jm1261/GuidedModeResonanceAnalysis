###############################################################################
###############################################################################
#                               Time Experiment                               #
#                             Author: Joshua Male                             #
#                              Date: 19/08/2026                               #
#          Description: Experiment script for time-dependent analysis         #
#                            Project: GMRProcessor                            #
#                                                                             #
#                         Script designed for Python 3                        #
#                           © Copyright Joshua Male                           #
#                                                                             #
#                            Software release: 0.1                            #
###############################################################################
###############################################################################

"""
Dear future Josh, this script works, and it works pretty well. But there are
still some things that I'd like to sort and you can use this as a test bed.
Firstly, the way it saves out ROI labels is not perfect. Then there's the
way it processes data, that can be it's own function to trim down scripts. The
plotting works ok, but there are plenty more parameters I'd like to incorporate
plus their errors too. Also figure out how to get the other processing
functions working, again can use this as a test bed for sure. Then apply it to
the chemical stability bits, and should be good to go. Also fix whatever is
wrong in FileIO that is causing an error, and maybe merge the plotting scripts.
"""

# Imports
import InitializeScripts  #noqa

import yaml
import logging
import GeneralUtils.FileIO as io
import DataUtils.DataProcessing as dp
import ImageUtils.ImageUtilities as iu
import ExperimentScripts.Plotting as plot

from pathlib import Path

# Start logging
logger = logging.getLogger(name=Path(__file__).stem)

# Define the path to the experiment
project_root = Path(__file__).resolve().parents[1]
config_path = project_root / 'local_config.yml'
with config_path.open(mode='r', encoding='utf-8') as config_file:
    local_config = yaml.safe_load(config_file)
plot_config_path = (
    project_root / 'standard_plot_parameters.yml'
)
with plot_config_path.open(mode='r', encoding='utf-8') as plot_config_file:
    plot_parameters = yaml.safe_load(plot_config_file)

experiment = {
    "Root Path": project_root,
    "Experiment Path": Path(
        local_config['PHOREST_DATA_ROOT'],
        'SodiumHydroxideExperiment',
        'ID0512'
    ),
    "Results Path": Path(
        local_config['PHOREST_DATA_ROOT'],
        'SodiumHydroxideExperiment',
        'ProcessedData'
    ),
    "GMR ID": "ID0512",
    "Measurement Type": "Time",
    "Chip Type": "IMEC-II 4",
    "Serial Number": 260818
}
logger.info(f'Processing Experiment: {experiment}')

# Load images and select the region of interest (ROI)
config = io.ExperimentalConfiguration(parameters=experiment)
measurement_paths = config.get_measurement_paths()
info_lookup = config.get_info_dates()

for sample, values in info_lookup.items():
    logger.info(f'Processing sample: {sample}, with details: {values}')
    date, datapath = values
    new_user_config = io.creates_new_configs(
        default_config=config.default_config,
        default_path=config.default_path,
        root_path=Path(datapath),
        results_path=config.results_path,
        chip_type=config.chip_type,
        gmr_id=experiment["GMR ID"],
        measurement_type=experiment["Measurement Type"],
        analysis_method='fit_hybrid',
        figure_filename=f'{sample}_{date}.png',
        config_name=f'{sample}_{date}'
    )
    image_config = io.load_user_config(file_path=new_user_config)

    # Process ROI data
    logger.info(f'Building image metadata for {sample}_{date}')
    out_path = Path(image_config.SAVE_PATH, 'ROI_Data', f'{sample}_{date}.csv')
    if out_path.exists():
        logger.warning(f'File {out_path} already exists, skipping')
        continue
    images_dictionary, metapath = io.build_metadata(
        image_path=Path(datapath),
        image_config=image_config,
        id_number=experiment["GMR ID"]
    )
    roi_file = io.build_roi(
        sensor=sample,
        date=str(date),
        id_number=experiment["GMR ID"],
        image_path=Path(datapath),
        root_path=experiment["Root Path"],
        measurement_path=experiment["Experiment Path"],
        results_path=experiment["Results Path"]
    )
    logger.info(f'Processing ROI for {sample}_{date}')
    iu.process_roi(
        sensor=sample,
        date=str(date),
        id_number=experiment["GMR ID"],
        image_config=image_config,
        measurement_path=experiment["Experiment Path"],
        metapath=metapath,
        images_dictionary=images_dictionary,
        roi_file=roi_file
    )

# Process Data
for sample, values in info_lookup.items():
    """ Can probably put this into some sort of function. """
    logger.info(f'Processing sample: {sample}, with details: {values}')
    date, datapath = values
    results_path = Path(
        config.results_path,
        'ROI_Results',
        f'{config.data_path.stem}.json'
    )
    if results_path.is_file() is False:
        logger.warning(f'File {results_path} does not exist, skipping')
        continue
    results_config = io.load_json(file_path=results_path)
    roi_file = io.load_json(
        file_path=Path(
            datapath,
            f'ROI_SU{experiment["GMR ID"]}.json'
        )
    )
    image_config = io.load_user_config(
        file_path=Path(
            datapath,
            f'{sample}_{date}.yml'
        )
    )
    chip_features = io.get_chip_features(
        configuration=image_config,
        config_path=Path(
            config.root_path,
            'Config'
        )
    )
    results_dataframe = io.load_csv(
        file_path=Path(
            image_config.SAVE_PATH,
            'ROI_Data',
            experiment["Experiment Path"].stem,
            f'{sample}_{date}.csv'
        )
    )
    roi_labels = sorted(set(results_dataframe['ROI'].unique()))
    roi_pairs = [
        (roi_labels[i], roi_labels[i+1])
        for i in range(0, len(roi_labels) - 1, 2)
    ]

    results_processor = dp.ProcessData(
        results_dataframe=results_dataframe,
        analysis_method=image_config.ANALYSIS_METHOD.value,
        chip_features=chip_features,
        results_dictionary=results_config
    )

    for roi_A, roi_B in roi_pairs:
        roi_A_label = roi_file[roi_A]["label"]
        roi_label = roi_A_label.split('_')[0]
        sensor_label = roi_label
        time = float(sample.split('_')[0])  # unique to this script
        logger.info(
            f'Processing ROI pair: {roi_A}, {roi_B} '
            f'for GMR {sensor_label} on {experiment["GMR ID"]} '
            f'at timestamp {sample}'
        )
        results = results_processor.process_data(
            roi_A=roi_A,
            roi_B=roi_B,
            sensor_label=sensor_label,
            timestamp=time,
            timestamp_error=0.2
        )
        logger.info(f'Processed results {results}')
        results_config["Results"].update(results)
    io.save_json_dicts(
        out_path=results_path,
        dictionary=results_config
    )

# Plot the results
results_path = Path(
    config.results_path,
    'ROI_Results',
    f'{config.data_path.stem}.json'
)
if results_path.is_file() is False:
    logger.warning(f'File {results_path} does not exist')
    exit(69)
results_config = io.load_json(file_path=results_path)
plot_parameters.update({
    "out-path": Path(
        config.results_path,
        'ROI_Results',
        f'{config.data_path.stem}.png'
    ),
    "x-label": "Time [Hours]",
    "fit-line": True,
    "polynomial-order": 1,
    "legend-size": 6,
    "fit-fontsize": 7
})
plot.plot_time(
    results_dict=results_config,
    plot_parameters=plot_parameters
)
