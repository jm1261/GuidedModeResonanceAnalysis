###############################################################################
###############################################################################
#                              File I/O Functions                             #
#                             Author: Joshua Male                             #
#                              Date: 30/04/2025                               #
#            Description: File Input, Output, and Handling Functions          #
#                            Project: GMRProcessor                            #
#                                                                             #
#                         Script designed for Python 3                        #
#                           © Copyright Joshua Male                           #
#                                                                             #
#                            Software release: 0.1                            #
###############################################################################
###############################################################################

# Imports
import os
import re
import yaml
import json
import logging
import numpy as np
import pandas as pd
import GeneralUtils.Plotting as plot
import ImageUtils.ImageUtilities as iu

from enum import Enum
from pathlib import Path
from typing import Any, Mapping
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError

# Set up logging
logger = logging.getLogger(name=Path(__file__).stem)


def load_json(file_path: os.PathLike) -> dict:
    """
    Function Details
    ================
    Loads .json file types.

    Use json python library to load a .json file.

    Parameters
    ----------
    file_path : string
        Path to file.

    Returns
    -------
    json file : dictionary
        .json dictionary file.

    Notes
    -----
    json files are typically dictionaries, as such the function is intended for
    use with dictionaries stored in .json file types.

    ---------------------------------------------------------------------------
    Update History
    ==============

    06/08/2024
    ----------
    Copied from previous work, documentation updated. JM.

    """
    with open(file_path, 'r') as file:
        return json.load(file)


def convert(o):
    """
    Function Details
    ================
    Check data type.

    Check type of data string.

    Parameters
    ----------
    o : string
        String to check.

    Returns
    -------
    TypeError : Boolean
        TypeError if string is not suitable.

    ---------------------------------------------------------------------------
    Update History
    ==============

    06/08/2024
    ----------
    Copied from previous work, documentation updated. JM.

    """
    if isinstance(o, np.generic):
        return o.item()
    raise TypeError(f'Cannot serialize object of {type(o)}')


def save_json_dicts(out_path: os.PathLike,
                    dictionary: dict) -> None:
    """
    Function Details
    ================
    Save .json file types.

    Use json python library to save a dictionary to a .json file.

    Parameters
    ----------
    out_path : string
        Path to file.
    dictionary : dictionary
        Dictionary to save.

    Returns
    -------
    None

    Notes
    -----
    json files are typically dictionaries, as such the function is intended for
    use with dictionaries stored in .json file types.

    ---------------------------------------------------------------------------
    Update History
    ==============

    06/08/2024
    ----------
    Copied from previous work, documentation updated. JM.

    """
    with open(out_path, 'w') as outfile:
        json.dump(
            dictionary,
            outfile,
            indent=2,
            default=convert)
        outfile.write('\n')


def load_csv(file_path: Path) -> pd.DataFrame:
    """
    Function Details
    ================
    Load a CSV file into a pandas DataFrame.

    Parameters
    ----------
    file_path: Path
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the CSV data.

    ---------------------------------------------------------------------------
    Update History
    ==============
    
    30/04/2025
    ----------
    Created and documented.

    """
    return pd.read_csv(
        filepath_or_buffer=file_path,
        sep=',',
        header=0
    )


class SensorType(Enum):
    """
    Class Details
    =============
    Standard typing for Phorest software.

    Parameters
    ----------
    None.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/04/2025
    ----------
    Copied from Chris and documented.

    """
    UOY = 'UoY'
    IMECI = 'IMEC-I'
    IMECII = 'IMEC-II'
    CALIBRATION = 'Calibration'


class ImageType(Enum):
    """
    Class Details
    =============
    Standard typing for Phorest software.

    Parameters
    ----------
    None.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/04/2025
    ----------
    Copied from Chris and documented.

    """
    PNG = 'png'
    JPG = 'jpg'
    TIF = 'tif'


class AnalysisMethod(Enum):
    """
    Class Details
    =============
    Standard typing for Phorest software.

    Parameters
    ----------
    None.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/04/2025
    ----------
    Copied from Chris and documented.

    """
    MAX_INTENSITY = "max_intensity"
    CENTRE = "centre"
    GAUSSIAN = "gaussian"
    FANO = "fano"
    FIT_HYBRID = "fit_hybrid"


class UserConfigModel(BaseModel):
    """
    Class Details
    =============
    Standard typing for Phorest software.

    Parameters
    ----------
    None.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/04/2025
    ----------
    Copied from Chris and documented.

    """
    GMR_ID: str = 'GMR_ID'
    SENSOR_SERIAL_NUMBER: int = Field(default=1, gt=0)
    SETUP_SERIAL_NUMBER: int = Field(default=1, gt=0)
    MEASUREMENT_TYPE: str = 'MEASUREMENT_TYPE'
    SENSOR_TYPE: SensorType
    CHIP_TYPE: int
    ROOT_PATH: str
    DATA_FORMAT: str = 'experimental'
    IMAGE_TYPE: ImageType = ImageType.TIF
    SAVE_PATH: str
    FIGURE_FILENAME: str = 'filename'
    ANALYSIS_METHOD: AnalysisMethod = Field(
        default=AnalysisMethod.MAX_INTENSITY
    )
    NUMBER_SUB_ROIS: int = Field(default=0, ge=0)
    DEVICE_SERIAL_NUMBER: int = Field(default=1, gt=0)
    MEASUREMENT_INTERVAL: int = Field(default=60, ge=0)


def saveuser_config(
        config: UserConfigModel,
        old_path: Path,
        new_path: Path
    ) -> None:
    """
    Function Details
    ================
    Saves a new config based on the changes made to an existing one. Do not use
    in normal circulation.

    Parameters
    ----------
    config: yaml
        Yaml structure.
    old_path, new_path: Path
        Original config path, new config path.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    30/04/2025
    ----------
    Copied and documented.

    """
    original_lines = []
    with open(old_path, 'r') as f:
        original_lines = f.readlines()

    config_dict = config.dict()

    # Convert enum values to strings
    for key, value in config_dict.items():
        if isinstance(value, Enum):
            config_dict[key] = value.value

    new_lines = []
    for line in original_lines:
        if ":" in line and not line.strip().startswith("#"):
            key = line.split(":")[0].strip()
            if key in config_dict:
                new_lines.append(f"{key}: {config_dict[key]}\n")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(new_path, 'w') as f:
        f.writelines(new_lines)


def creates_new_configs(
            default_config: UserConfigModel,
            default_path: Path,
            root_path: Path,
            results_path: Path,
            chip_type: str,
            gmr_id: str | None = None,
            sensor_serial_number: int | None = None,
            setup_serial_number: int | None = None,
            measurement_type: str | None = None,
            data_format: str | None = None,
            image_type: str | None = None,
            figure_filename : str | None = None,
            analysis_method: str | None = None,
            number_sub_rois: int | None = None,
            device_serial_number: int | None = None,
            measurement_interval: int | None = None,
            config_name: str | None = None
) -> Path:
    """
    Build and save a configuration derived from the default model.

    The supplied model is updated in place. Values omitted from the optional
    arguments remain unchanged from ``default_config``.

    Parameters
    ----------
    default_config: UserConfigModel
        Configuration model to update and write.
    default_path: Path
        Path to the default YAML configuration. Its stem is used for the
        output filename when ``config_name`` is omitted.
    root_path: Path
        Root directory where the generated configuration is written and
        assigned to ``ROOT_PATH``.
    results_path: Path
        Results directory assigned to ``SAVE_PATH``.
    chip_type: str
        Sensor type and chip number separated by a space, such as
        ``IMEC-II 4``. This value sets ``SENSOR_TYPE`` and ``CHIP_TYPE``.
    gmr_id, measurement_type, data_format, figure_filename: str, optional
        Optional values for the corresponding configuration fields.
    sensor_serial_number, setup_serial_number, number_sub_rois,
    device_serial_number, measurement_interval: int, optional
        Optional values for the corresponding configuration fields.
    image_type: str, optional
        Image type value accepted by ``ImageType``, such as ``tif``.
    analysis_method: str, optional
        Analysis method value accepted by ``AnalysisMethod``, such as
        ``gaussian``.
    config_name: str, optional
        Output filename stem. If omitted, ``default_path.stem`` is used.

    Returns
    -------
    config_path: Path
        Path to newly created config file.

    Raises
    ------
    ValueError
        If a supplied enum value is invalid, or if ``chip_type`` does not
        contain a recognized sensor type and an integer chip number.
    OSError
        If the default configuration cannot be read or the generated
        configuration cannot be written.

    ---------------------------------------------------------------------------
    Update History
    ==============

    30/04/2025
    ----------
    Copied and documented.

    26/05/2026
    ----------
    Added chip type to config creation.

    24/08/2026
    - Added optional implementation for ultimate control.

    """

    # Sensor
    if gmr_id is not None:
        default_config.GMR_ID = gmr_id
    if sensor_serial_number is not None:
        default_config.SENSOR_SERIAL_NUMBER = sensor_serial_number
    if setup_serial_number is not None:
        default_config.SETUP_SERIAL_NUMBER = setup_serial_number
    if measurement_type is not None:
        default_config.MEASUREMENT_TYPE = measurement_type
    default_config.SENSOR_TYPE = SensorType(chip_type.split(' ')[0])
    default_config.CHIP_TYPE = int(chip_type.split(' ')[-1])

    # Data
    default_config.ROOT_PATH = Path(root_path).as_posix()
    if data_format is not None:
        default_config.DATA_FORMAT = data_format
    if image_type is not None:
        default_config.IMAGE_TYPE = ImageType(image_type)
    default_config.SAVE_PATH = Path(results_path).as_posix()
    if figure_filename is not None:
        default_config.FIGURE_FILENAME = figure_filename

    # Image
    if analysis_method is not None:
        default_config.ANALYSIS_METHOD = AnalysisMethod(analysis_method)
    if number_sub_rois is not None:
        default_config.NUMBER_SUB_ROIS = number_sub_rois

    # Device
    if device_serial_number is not None:
        default_config.DEVICE_SERIAL_NUMBER = device_serial_number
    if measurement_interval is not None:
        default_config.MEASUREMENT_INTERVAL = measurement_interval

    # Config
    config_name = config_name or default_path.stem
    config_path = Path(root_path, f'{config_name}.yml')
    if config_path.is_file():
        logger.info(f'User Config at: {config_path} exists.')
        pass
    else:
        logger.info(f'Saving user config to: {config_path}')
        saveuser_config(
            config=default_config,
            old_path=default_path,
            new_path=config_path
        )
    return config_path


def load_user_config(file_path: Path) -> UserConfigModel:
    """
    Function Details
    ================
    Load user config file.

    Parameters
    ----------
    file_path: Path
        Path to config file.

    Returns
    -------
    UserConfigModel
        Validated configuration model loaded from the YAML file.

    Raises
    ------
    OSError
        If the configuration file cannot be opened.
    yaml.YAMLError
        If the file contains invalid YAML.
    TypeError
        If the YAML document is not a mapping of configuration fields.
    SystemExit
        With exit code ``67`` when the YAML values fail model validation.

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/04/2025
    ----------
    Copied and documented from Chris' original coding.

    """
    with open(file=file_path, mode='r') as f:
        config_data = yaml.safe_load(f)

    try:
        return UserConfigModel(**config_data)
    except ValidationError as e:
        for err in e.errors():
            field_name = '.'.join(str(x) for x in err['loc'])
            logger.error(f'Error in field {field_name}: {err["msg"]}')
        raise SystemExit(67)


def build_metadata(
        image_path: Path,
        image_config: UserConfigModel,
        id_number: str
) -> tuple[dict, Path]:
    """
    Function Details
    ================
    Helper function to determine the data path and build/load image metadata.

    Parameters
    ----------
    image_path : Path
        Path to the image file.
    image_config : UserConfigModel
        Image configuration object containing metadata information.
    id_number : str
        Unique identifier for the image.

    Returns
    -------
    dict
        A dictionary containing the image metadata.
    Path
        The path to the metadata directory.

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/05/2026
    ----------
    - Initial function development and testing.
    - Spawned from original process_sensors function.

    """
    datapath_old, datapath_new, datapath_stack = (
            Path(image_path, 'Pos0'),
            Path(image_path, 'Default'),
            Path(image_path)
        )
    if datapath_old.is_dir():
        metapath = datapath_old
    elif datapath_new.is_dir():
        metapath = datapath_new
    else:
        metapath = datapath_stack
    """ STILL HAVE CHANCE TO CHANGE THIS GOING FORWARD """
    image_metadata_builder = ImageMetaData(
        data_path=metapath,
        image_type=image_config.IMAGE_TYPE.value,
        sensor_ID=str(image_config.SENSOR_SERIAL_NUMBER),
        setup_ID=str(image_config.SETUP_SERIAL_NUMBER),
        reader_ID=str(image_config.DEVICE_SERIAL_NUMBER),
        every_Nth_element=1,
        image_metadata_name=f'image_metadata_SU{id_number}'
    )
    image_metadata_builder.build_imagemetadata(skip_existing=True)
    dictionary_path = image_metadata_builder.save_image_metadata()
    images_dictionary = load_json(file_path=dictionary_path)
    return images_dictionary, metapath


def build_roi(
        sensor: str,
        date: str,
        id_number: str,
        image_path: Path,
        root_path: Path,
        measurement_path: Path,
        results_path: Path
) -> dict:
    """
    Function Details
    ================
    Helper function to build ROI files, handle labels, and update sensor JSON
    results.

    Parameters
    ----------
    sensor, date, id_number: str
        Sensor name, date, and unique identifier for the image.
    image_path, measurement_path: Path
        Path to the image file and measurement directory.
    root_path, results_path: Path
        Path to repo root, path to save results.

    Returns
    -------
    dict
        Dictionary containing the ROI data for the sensor.

    Notes
    -----

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/05/2026
    ----------
    - Initial function development and testing.
    - Spawned from original process_sensors function.

    16/09/2026
    ----------
    - Adjusted with recent reformatting.

    """
    logger.info(f'Building ROI for sensor: {sensor}, date: {date}')
    selection_path = Path(results_path, 'ROI_Selection')
    check_dir_exists(dir_path=selection_path)
    roi_file_builder = ROIFileBuilder(
        image_path=image_path,
        config_path=Path(root_path, 'Config'),
        results_path=Path(selection_path, measurement_path.stem),
        ID_number=id_number,
        image_name=f'{sensor}_{date}'
    )
    roi_file_builder.build_ROIs()
    roi_file = roi_file_builder.rois
    results_file = Path(
        results_path,
        'ROI_Results',
        f'{measurement_path.stem}.json'
    )
    results_file.parent.mkdir(parents=True, exist_ok=True)
    if results_file.exists():
        logger.warning(f'File {results_file} already exists, loading')
        sensor_results = load_json(file_path=results_file)
    else:
        logger.info(f'File {results_file} does not exist, creating')
        sensor_results = {
            "Sensor IDs": {},
            "Results": {},
            "Average Results": {}
        }
    _ = roi_file_builder.get_ROI_labels()
    updated_IDs = roi_file_builder.save_ROI_labels(
        date=sensor,
        sensor_labels=sensor_results["Sensor IDs"]
    )
    sensor_results["Sensor IDs"] = updated_IDs
    save_json_dicts(
        out_path=results_file,
        dictionary=sensor_results
    )
    return roi_file


class ImageMetaData:
    """
    Class Details
    =============
    Class for building a list of images within a directory.

    Functions
    ---------
    __init__
    extractfile
    getfilesize
    build_imagemetadata
    save_image_metadata
    loads_existing_metadata

    Attributes
    ----------
    self
    data_path
    image_type
    image_size
    sensor_ID
    setup_ID
    reader_ID
    Nth
    image_metadata

    Notes
    -----
    Builds an image list for a specified directory. Image size is given in kB
    and converted to bytes.

    ---------------------------------------------------------------------------
    Update History
    ==============

    13/08/2024
    ----------
    Created.

    22/10/2024
    ----------
    Changed from HistoricalData class to build singular image list per
    directory. Removed execute function.

    """

    def __init__(
            self,
            data_path: os.PathLike,
            image_type: str,
            sensor_ID: str,
            setup_ID: str,
            reader_ID: str,
            image_size: int = 5000,
            every_Nth_element: int = 1,
            image_metadata_name: str = None
        ) -> None:
        """
        Function Details
        ================
        Initialize image list generation.

        Parameters
        ----------
        data_path: PathLike
            Path to data directory.
        image_type, sensor_ID, setup_ID, reader_ID: string
            File type of images, GMR/Sensor serial number, setup serial number,
            reader/device serial number.
        image_size, every_Nth_element: integer, optional
            Image size in kilobytes (kB). If blank, will default to 5000 kB.
            Select every Nth element of the data files list. If blank, will
            select all.
        image_metadata_name: string, optional
            Name of the metadata file to load. Defaults to
            'image_metadata_SU{self.setup_ID}.json'.

        Returns
        -------
        None, assigned class attributes.

        -----------------------------------------------------------------------
        Update History
        ==============

        13/08/2024
        ----------
        Created.

        22/10/2024
        ----------
        Adjusted for trimmed ImageList class.

        """
        self.data_path = Path(data_path).as_posix()
        self.image_type = image_type
        self.image_size = image_size * 1024
        self.sensor_ID = sensor_ID
        self.setup_ID = setup_ID
        self.reader_ID = reader_ID
        self.Nth = every_Nth_element
        self.image_metadata = {}
        if image_metadata_name:
            self.image_metadata_name = image_metadata_name
        else:
            self.image_metadata_name = f'image_metadata_SU{self.setup_ID:06d}'

    def extractfile(
            self,
            directory_path: os.PathLike,
            file_string: str
        ) -> list[str]:
        """
        Function Details
        ================
        Find files containing a certain string in their name in a target
        directory.

        Parameters
        -----------
        directory_path: PathLike
            Path to directory.
        file_string: str
            Desired string in file.

        Returns
        -------
        list: list[str]
            List of files in target directory containing the desired string.

        -----------------------------------------------------------------------
        Update History
        ==============

        02/07/2024
        ----------
        Copied from another repository, documentation tidied.

        """
        directory_list = sorted(os.listdir(directory_path))
        return [file for file in directory_list if file_string in file]

    def getfilesize(
            self,
            file_path: Path
        ) -> str:
        """
        Function Details
        ================
        Get file size from file path.

        Parameters
        ----------
        file_path: Path
            Path to file.

        Returns
        -------
        file size, None: integer, None
            If file path is found, return file size as bytes, else return None.

        -----------------------------------------------------------------------
        Update History
        ==============

        23/10/2024
        ----------
        Created.

        """
        try:
            return file_path.stat().st_size
        except FileNotFoundError:
            logger.warning(f'File not found: {file_path}')
            return None
        except PermissionError:
            logger.error(f'Permission denied for file: {file_path}')
            return None
        except OSError as e:
            logger.error(f'OS error occurred for file {file_path}: {str(e)}')
            return None

    def build_imagemetadata(
            self,
            get_time_stamps: bool = False,
            skip_existing: bool = True
        ) -> None:
        """
        Function Details
        ================
        Build image list metadata.

        Parameters
        ----------
        get_time_stamps: bool, optional
            If true, reads time stamps from image file names, otherwise file
            names.
        skip_existing: bool, optional
            If True, skips images already in existing metadata, defaults to
            True.

        See Also
        --------
        extractfile
        parse_date
        convert_datetime

        -----------------------------------------------------------------------
        Update History
        ==============

        13/08/2024
        ----------
        Created.

        19/08/2024
        ----------
        Adjusted date/time parsing function.

        18/10/2024
        ----------
        Change to the file path to include a relative path from root path, and
        data path from the user config file. Allows universality in data
        processing.

        22/10/2024
        ----------
        Change to function name and streamlining of processing. Change to only
        process one directory, not a list of directories. Added initial image
        error.

        23/10/2024
        ----------
        Update to file size error handling.

        """
        self.loads_existing_metadata()
        logger.info(
            f'Building image list for {self.data_path} using '
            f'{self.image_type} files')
        all_files = self.extractfile(
            directory_path=self.data_path,
            file_string=self.image_type)
        files = [
            file
            for index, file in enumerate(all_files)
            if index % self.Nth == 0]
        file_paths = [Path(self.data_path, file) for file in files]
        relative_paths = [
            (path.relative_to(self.data_path)).as_posix()
            for path in file_paths]
        file_names = [path.stem for path in file_paths]
        file_sizes = [self.getfilesize(file_path=path) for path in file_paths]
        errors = [
            'None' if size is not None and size >= self.image_size else
            ('Truncated Image' if size is not None else 'File Not Found')
            for size in file_sizes]
        processed = [False] * len(files)
        if get_time_stamps:
            time_stamps = [
                convert_datetime(
                    date_time=parse_date(
                        date_string=name))
                for name in file_names]
        else:
            time_stamps = [name for name in file_names]
        sensorID = [self.sensor_ID] * len(files)
        setupID = [self.setup_ID] * len(files)
        readerID = [self.reader_ID] * len(files)
        for name, sID, suID, rID, rpath, err, proc, time in zip(file_names,
                                                                sensorID,
                                                                setupID,
                                                                readerID,
                                                                relative_paths,
                                                                errors,
                                                                processed,
                                                                time_stamps):
            if skip_existing and name in self.image_metadata:
                continue
            self.image_metadata.update({
                f'{name}': {
                    "Sensor ID": f'{sID}',
                    "Setup ID": f'{suID}',
                    "Reader ID": f'{rID}',
                    "Root Path": f'{self.data_path}',
                    "File Path": f'{rpath}',
                    "Error": f'{err}',
                    "Processed": proc,
                    "Time Stamp": time}})
        logger.info(f'Image metadata for {self.data_path} completed')

    def save_image_metadata(self) -> Path:
        """
        Function Details
        ================
        Save image list to target destination with ID number.

        Returns
        -------
        out_path: Path
            Path to previously saved image metadata file.

        See Also
        --------
        save_json_dicts

        -----------------------------------------------------------------------
        Update History
        ==============

        22/10/2024
        ----------
        Created from old historical image list class method.

        """
        out_path = Path(self.data_path, f'{self.image_metadata_name}.json')
        save_json_dicts(
            out_path=out_path,
            dictionary=self.image_metadata)
        logger.info(f'Saved image metadata to {out_path}')
        self.image_metadata = {}
        logger.info('Reset image list')
        return out_path

    def loads_existing_metadata(self) -> None:
        """"
        Function Details
        ================
        Load existing image metadata from file if it exists.

        Parameters
        ----------
        image_metadata_name: string, optional
            Name of the metadata file to load. Defaults to
            'image_metadata_SU{self.setup_ID}.json'.

        Returns
        -------
        None.

        -----------------------------------------------------------------------
        Update History
        ==============

        23/10/2024
        ----------
        Created to handle merging of existing and new image metadata.

        """
        metadata_path = Path(
            self.data_path,
            f'{self.image_metadata_name}.json')
        if metadata_path.exists():
            logger.info(f'Existing metadata file found: {metadata_path}')
            try:
                self.image_metadata = load_json(file_path=metadata_path)
                logger.info('Loaded existing image metadata successfully')
            except json.JSONDecodeError:
                logger.error(
                    f'Error decoding JSON from {metadata_path}. '
                    f'Starting fresh')
            except Exception as e:
                logger.error(f'Unexpected error while loading metadata: {e}')
        else:
            logger.info('No existing metadata file found. Starting fresh')
            self.image_metadata = {}


def parse_date(date_string: str) -> datetime:
    """
    Function Details
    ================
    Parse time stamp information in various formats.

    Parameters
    ----------
    date_string: string
        Date and time string.

    Returns
    -------
    datetime: datetime
        Date and time as a datetime object.

    See Also
    --------
    datetime strptime

    Notes
    -----
    Add new timestamp formats to the top for loop.

    Accepted Formats
    ----------------
    * ID-YYYYmmdd_HHMMSS
    * ID-YYYYmmdd-HHMMSS
    * YYYYmmdd-HHMMSS
    * YYYYmmdd_HHMMSS
    * ddmmYYYY HHMM
    * YYYY-mm-dd HHMMSS
    * YYYYmmdd

    Example
    -------
    None.

    ----------------------------------------------------------------------------
    Update History
    ==============

    09/07/2024
    ----------
    Documentation updated.

    19/08/2024
    ----------
    Updated pattern matching algorithm.

    """
    patterns = [
        (r'\d{8}[-_]\d{6}', '%Y%m%d-%H%M%S'),
        (r'\d+-\d{8}[-_]\d{6}', '%Y%m%d-%H%M%S'),
        (r'\d{2}\d{2}\d{4}\s\d{4}', '%d%m%Y %H%M'),
        (r'\d{4}-\d{2}-\d{2}\s\d{6}', '%Y-%m-%d %H%M%S')
    ]
    old_formats = (
        "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y%m%d_%H%M%S", "%Y%m%d")

    for pattern, date_format in patterns:
        match = re.search(pattern, date_string)
        if match:
            date_str = match.group()
            date_str = date_str.replace('_', '-')  # Ensure consistent format
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError as e:
                logger.error(f'Parsing date error: {e}')
                print(f'[ERROR] Parsing date error: {e}')
                return None

    for fmt in old_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    logger.error(f'No valid timestamp found in {date_string}')
    print(f'[ERROR] No valid timestamp found in {date_string}')
    return None


def convert_datetime(date_time: datetime) -> float:
    """
    Function Details
    ================
    Convert datetime into seconds.

    Parameters
    ----------
    date_time: datetime
        Date and time as a datetime object.

    Returns
    -------
    time: float
        Time in seconds.

    See Also
    --------
    parse_date

    Notes
    -----
    None.

    Example
    -------
    None.

    ----------------------------------------------------------------------------
    Update History
    ==============

    09/07/2024
    ----------
    Created.

    """
    time = date_time.timestamp()
    return time


def get_chip_features(
        configuration: UserConfigModel,
        config_path: Path
) -> dict:
    """
    Function Details
    ================
    Pull in the GMR chip features.

    Parameters
    ----------
    configuration: yaml
        Image config file.
    config_path: Path
        Path to config directory.

    Returns
    -------
    chip_features: dict
        Dictionary containing chip features.

    ---------------------------------------------------------------------------
    Update History
    ==============

    30/04/2025
    ----------
    Copied and documented.

    26/05/2026
    ----------
    Added chip type to config loading.

    """
    sensor_type = configuration.SENSOR_TYPE.value
    chip_type = configuration.CHIP_TYPE
    config_file = f'{sensor_type}.json'
    chip = load_json(file_path=Path(config_path, config_file))
    chip_features = chip[f'{sensor_type} {chip_type}']
    chip_features['Measurement Type'] = configuration.MEASUREMENT_TYPE
    chip_features['Sensor Type'] = configuration.SENSOR_TYPE.value
    chip_features['Chip Type'] = configuration.CHIP_TYPE
    return chip_features


def get_first_file(
        image_path: Path,
        image_metadata_name: str
) -> Path:
    """
    Function Details
    ================
    Get the first file in each image_metadata file.

    Parameters
    ----------
    image_path: Path
        Path to images.
    image_metadata_name: str
        Name of the metadata file.

    Returns
    -------
    first_path: Path
        Path to first file.

    ---------------------------------------------------------------------------
    Update History
    ==============

    30/04/2025
    ----------
    Copied and documented.

    """
    images_metadata_filepath = Path(image_path, image_metadata_name)
    images_dictionary = load_json(file_path=images_metadata_filepath)
    keys = list(images_dictionary.keys())
    first_file = images_dictionary[keys[0]]
    first_path = Path(first_file["Root Path"], first_file["File Path"])
    return first_path


def check_dir_exists(dir_path: os.PathLike) -> None:
    """
    Function Details
    ================
    Checks directory path exists.

    Parameters
    ----------
    dir_path: string
        Path to directory.

    Returns
    -------
    None

    See Also
    --------
    None

    Notes
    -----
    If directory does not exist, make one.

    Example
    -------
    None

    ----------------------------------------------------------------------------
    Update History
    ==============

    01/03/2024
    ----------
    Updated documentation.

    """
    if os.path.isdir(dir_path) is False:
        os.mkdir(dir_path)


class ExperimentalConfiguration:
    """
    Class Details
    =============
    Store experiment paths and metadata used by file-processing workflows.

    Functions
    ---------
    __init__
    get_measurement_paths
    get_info_dates

    Attributes
    ----------
    root_path: Path
        Root directory for the experiment.
    data_path: Path
        Directory containing measurement data.
    results_path: Path
        Directory for processed results.
    measurement_type: str
        Measurement mode used to select measurement directories.
    chip_type: str
        Chip type associated with the experiment.
    measurement_paths: list[Path]
        Measurement directories discovered by ``get_measurement_paths``.
    info_lookup: dict[str, list[str | Path]]
        Mapping built by ``get_info_dates`` from measurement directory names.

    Notes
    -----
    The supplied path values are normalized to ``Path`` objects and the
    metadata values are normalized to strings. The default YAML configuration
    is loaded during initialization.

    Side Effects
    ------------
    Stores the configuration values as instance attributes and emits
    ``INFO`` log records through the ``FileIO`` logger.
    -----
    Call ``get_measurement_paths`` before ``get_info_dates``.

    ---------------------------------------------------------------------------
    Update History
    ==============

    19/08/2026
    ----------
    - Initial implementation.

    """

    root_path: Path
    data_path: Path
    results_path: Path
    measurement_type: str
    chip_type: str
    default_path: Path
    default_config: UserConfigModel
    measurement_paths: list[Path]
    info_lookup: dict[str, list[str | Path]]

    def __init__(
            self,
            parameters: Mapping[str, Path | str]
        ) -> None:
        """
        Function Details
        ================
        Initialize an experiment configuration from a parameter mapping.

        Parameters
        ----------
        parameters: Mapping[str, Path | str]
            Configuration values with the keys ``Root Path``,
            ``Experiment Path``, ``Results Path``, ``Measurement Type``, and
            ``Chip Type``.

        Returns
        -------
        None

        Raises
        ------
        KeyError: If a required configuration key is missing.
        FileNotFoundError: If either configuration file is missing.
        OSError: If a configuration file cannot be read.
        ValidationError: If the default YAML does not match UserConfigModel.

        Notes
        -----

        -----------------------------------------------------------------------
        Update History
        ==============

        19/08/2026
        ----------
        - Initial implementation.

        """
        self.root_path = Path(parameters["Root Path"])
        self.data_path = Path(parameters["Experiment Path"])
        self.results_path = Path(parameters["Results Path"])
        logger.info(
            'Configuration - Root Path: %s, Data Path: %s, Results Path: %s',
            self.root_path,
            self.data_path,
            self.results_path
        )
        self.measurement_type = str(parameters["Measurement Type"])
        self.chip_type = str(parameters["Chip Type"])
        logger.info(
            'Configuration - Measurement Type: %s, Chip Type: %s',
            self.measurement_type,
            self.chip_type
        )
        self.default_path = Path(
            self.root_path,
            'Config',
            'DEFAULT.yml'
        )
        self.default_config = load_user_config(file_path=self.default_path)
        logger.info(
            'Default Path: %s, Default Config: %s',
            self.default_path,
            self.default_config
        )

    def get_measurement_paths(self) -> list[Path]:
        """
        Function Details
        ================
        Find measurement directories for time-based experiments.

        Parameters
        ----------
        None.

        Returns
        -------
        measurement_paths: list[Path]
            Directories found under ``data_path`` for a ``Time`` measurement.
            Returns an empty list for other measurement types.

        Raises
        ------
        FileNotFoundError: If ``data_path`` does not exist.
        NotADirectoryError: If ``data_path`` is not a directory.
        PermissionError: If access to ``data_path`` is denied.

        Side Effects
        ------------
        Stores the discovered directories in ``self.measurement_paths`` and
        logs the search and result.

        Notes
        -----

        -----------------------------------------------------------------------
        Update History
        ==============

        19/08/2026
        ----------
        - Initial implementation.

        """
        logger.info(f'Looking for measurements in {self.data_path}')

        if self.measurement_type == "Time":
            measurement_paths = [
                directory
                for directory in self.data_path.iterdir()
                if directory.is_dir()
            ]
        else:
            measurement_paths = []
        logger.info(f'Found paths: {measurement_paths}')
        self.measurement_paths = measurement_paths
        return measurement_paths

    def get_info_dates(self) -> dict[str, list[str | Path]]:
        """
        Function Details
        ================
        Build a lookup of measurement information and dates.

        Parameters
        ----------
        None.

        Returns
        -------
        info_lookup: dict[str, list[str | Path]]
            Mapping from the information prefix in each measurement directory
            name to a ``[date, path]`` list.

        Raises
        ------
        AttributeError: If ``get_measurement_paths`` has not been called.

        Side Effects
        ------------
        Stores the lookup in ``self.info_lookup`` and logs the result.

        Notes
        -----
        Directory names must contain two or three underscore-separated parts.
        Other names are ignored, and duplicate information keys are overwritten
        by later entries.
        """
        infos, dates = [], []
        for file in self.measurement_paths:
            parts = file.stem.split('_')
            if len(parts) == 2:
                infos.append(parts[0])
                dates.append(parts[1])
            if len(parts) == 3:
                infos.append('_'.join(parts[:-1]))
                dates.append(parts[-1])
        info_lookup = {
            info: [date, path]
            for info, date, path
            in zip(infos, dates, self.measurement_paths)
        }
        self.info_lookup = info_lookup
        logger.info(f'Sample database: {info_lookup}')
        return info_lookup


class ChemicalStabilityConfiguration:
    """
    Class Details
    =============
    Build directory tree, measurement paths, and sample paths for chemical
    stability testing.

    Functions
    ---------
    __init__
    get_measurement_paths
    get_info_dates

    Attributes
    ----------
    root_path: Path
        Root directory for the experiment.
    data_path: Path
        Directory containing chemical-stability data.
    results_path: Path
        Directory for processed results.
    measurement_type: str
        Measurement mode used by the workflow.
    configuration_filename: str
        Name of the experiment-specific JSON configuration file.
    chip_type: str
        Chip type associated with the experiment.
    configuration_file: dict
        Experiment-specific settings loaded from the JSON configuration.
    default_path: Path
        Path to the chemical-stability YAML defaults.
    default_config: UserConfigModel
        Validated default configuration loaded from ``default_path``.
    measurement_paths: list[Path]
        Measurement directories discovered by ``get_measurement_paths``.
    info_lookup: dict[str, list[str | Path]]
        Mapping built by ``get_info_dates`` from measurement directory names.

    Notes
    -----
    Configuration values use the same normalization rules as
    ``ExperimentalConfiguration``. The JSON and YAML configuration files are
    loaded during initialization, so missing or invalid files fail early.

    ---------------------------------------------------------------------------
    Update History
    ==============

    03/06/2025
    ----------
    - Initial creation of the class and its methods.

    10/09/2026
    ----------
    - Updated to match ExperimentalConfiguration class structure and logging.

    """

    root_path: Path
    data_path: Path
    results_path: Path
    measurement_type: str
    configuration_filename: str
    chip_type: str
    configuration_file: dict
    default_path: Path
    default_config: UserConfigModel
    measurement_paths: list[Path]
    info_lookup: dict[str, list[str | Path]]

    def __init__(
            self,
            parameters: Mapping[str, Path | str]
    ) -> None:
        """
        Function Details
        ================
        Initialize a chemical stability configuration from a parameter mapping.

        Parameters
        ----------
        parameters: Mapping[str, Path | str]
            Configuration values with the keys ``Root Path``,
            ``Experiment Path``, ``Results Path``, ``Measurement Type``,
            ``Configuration Filename``, and ``Chip Type``.

        Returns
        -------
        None

        Raises
        ------
        KeyError: If a required configuration key is missing.
        FileNotFoundError: If either configuration file is missing.
        OSError: If a configuration file cannot be read.
        ValidationError: If the default YAML does not match UserConfigModel.

        Notes
        -----

        -----------------------------------------------------------------------
        Update History
        ==============

        10/09/2026
        ----------
        - Initial implementation.

        """
        self.root_path = Path(parameters["Root Path"])
        self.data_path = Path(parameters["Experiment Path"])
        self.results_path = Path(parameters["Results Path"])
        logger.info(
            'Configuration - Root Path: %s, Data Path: %s, Results Path: %s',
            self.root_path,
            self.data_path,
            self.results_path
        )
        self.measurement_type = str(parameters["Measurement Type"])
        self.configuration_filename = str(parameters["Configuration Filename"])
        self.chip_type = str(parameters["Chip Type"])
        logger.info(
            'Configuration - Measurement Type: %s, Chip Type: %s, '
            'Configuration Filename: %s',
            self.measurement_type,
            self.chip_type,
            self.configuration_filename
        )
        self.configuration_file = load_json(
            file_path=Path(
                self.data_path,
                self.configuration_filename
            )
        )
        self.default_path = Path(
            self.root_path,
            'Config',
            'ChemicalStability.yml'
        )
        self.default_config = load_user_config(file_path=self.default_path)
        logger.info(
            'Default Path: %s, Default Config: %s',
            self.default_path,
            self.default_config
        )

    def get_measurement_paths(self) -> list[Path]:
        """
        Return and store child directories containing measurements.

        Returns
        -------
        list[Path]
            Child directories below ``data_path``.

        Raises
        ------
        FileNotFoundError: If ``data_path`` does not exist.
        NotADirectoryError: If ``data_path`` is not a directory.
        PermissionError: If access to ``data_path`` is denied.

        Side Effects
        ------------
        Stores the result on ``measurement_paths`` and logs the search.
        """
        logger.info('Looking for measurements in %s', self.data_path)
        measurement_paths = [
            directory
            for directory in self.data_path.iterdir()
            if directory.is_dir()
        ]
        self.measurement_paths = measurement_paths
        logger.info('Found paths: %s', measurement_paths)
        return measurement_paths

    def get_info_dates(self) -> dict[str, list[str | Path]]:
        """
        Return a lookup built from underscore-separated directory names.

        Returns
        -------
        dict[str, list[str | Path]]
            Mapping from each information prefix to ``[date, path]``.

        Raises
        ------
        AttributeError
            If ``get_measurement_paths`` has not been called.

        Side Effects
        ------------
        Stores the result on ``info_lookup`` and ignores names that do not
        contain two or three underscore-separated parts.
        """
        infos, dates = [], []
        for directory in self.measurement_paths:
            parts = directory.stem.split('_')
            if len(parts) == 2:
                infos.append(parts[0])
                dates.append(parts[1])
            elif len(parts) == 3:
                infos.append('_'.join(parts[:-1]))
                dates.append(parts[-1])
        info_lookup = {
            info: [date, path]
            for info, date, path
            in zip(infos, dates, self.measurement_paths)
        }
        self.info_lookup = info_lookup
        logger.info('Sample database: %s', info_lookup)
        return info_lookup


class ROIFileBuilder:
    """
    Class Details
    =============
    Build ROI files for each sample in a GMR experiment.

    Functions
    ---------
    __init__
    build_ROIs
    save_ROIs
    plot_ROIs
    get_ROI_labels
    save_ROI_labels

    Attributes
    ----------
    out_path: Path
        Path to the JSON ROI file.
    results_path: Path
        Directory for the ROI preview image.
    configuration: UserConfigModel
        Validated image configuration.
    chip_features: dict
        Chip geometry used by the ROI locator.
    first_file: Path
        First image selected from the metadata file.
    image: np.ndarray | None
        Image loaded for ROI detection or plotting.
    rois: dict | None
        ROI locations and image angle.
    roi_labels: list[str]
        Labels extracted from the ROI dictionary.

    Notes
    -----
    Existing ROI JSON and preview files are reused. New ROI selections are
    saved beside the source image and preview images are saved below
    ``results_path``.

    ---------------------------------------------------------------------------
    Update History
    ==============

    16/09/2026
    ----------
    - Initial creation of the class and its methods.

    """

    image_path: Path
    config_path: Path
    results_path: Path
    ID_number: str
    image_name: str
    out_path: Path
    configuration: UserConfigModel
    chip_features: dict
    first_file: Path
    image: np.ndarray | None
    rois: dict | None
    roi_labels: list[str]

    def __init__(
            self,
            image_path: Path,
            config_path: Path,
            results_path: Path,
            ID_number: str,
            image_name: str
    ) -> None:
        """
        Function Details
        ================
        Initialize ROI file builder with paths and identifiers.

        Parameters
        ----------
        image_path, config_path, results_path: Path
            Image directory, repository configuration directory, and directory
            used to save ROI figures.
        ID_number, image_name: str
            Identification string for ROI file. Image name used for config
            file.

        Returns
        -------
        None.

        Notes
        -----
        The image-specific YAML and metadata JSON must already exist.

        Raises
        ------
        FileNotFoundError: If the image configuration or metadata is missing.
        OSError: If the ROI results directory cannot be created or accessed.
        ValidationError: If the image YAML fails UserConfigModel validation.

        -----------------------------------------------------------------------
        Update History
        ==============

        16/09/2026
        ----------
        - Initial implementation.

        """
        self.out_path = Path(image_path, f'ROI_SU{ID_number}.json')
        self.results_path = results_path
        check_dir_exists(dir_path=self.results_path)
        logger.info(
            'Output path for ROI file: %s, Results path: %s',
            self.out_path,
            self.results_path
        )
        self.image_name = image_name
        self.image = None
        self.rois = None
        self.roi_labels = []
        self.configuration = load_user_config(
            file_path=Path(
                image_path,
                f'{self.image_name}.yml'
            )
        )
        self.chip_features = get_chip_features(
            configuration=self.configuration,
            config_path=config_path
        )
        logger.info(
            'Loaded configuration %s and chip features %s for image %s',
            self.configuration,
            self.chip_features,
            self.image_name
        )
        try:
            self.first_file = get_first_file(
                image_path=Path(image_path, 'Pos0'),
                image_metadata_name=f'image_metadata_SU{ID_number}.json'
            )
        except (FileNotFoundError, TypeError):
            self.first_file = get_first_file(
                image_path=Path(image_path, 'Default'),
                image_metadata_name=f'image_metadata_SU{ID_number}.json'
            )
        logger.info(
            'First file for ROI processing: %s',
            self.first_file
        )

    def build_ROIs(self) -> None:
        """
        Function Details
        ================
        Build ROI file.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        None.
        
        Notes
        -----
        None.
        
        -----------------------------------------------------------------------
        Update History
        ==============
        
        03/06/2026
        ----------
        Copied and documented.
        
        03/06/2025
        ----------
        Merged with class.

        """
        if self.out_path.is_file():
            logger.warning(f'ROIs already selected for {self.image_name}')
            self.image = iu.load_image_data(file_path=self.first_file)
            self.rois = load_json(file_path=self.out_path)
        else:
            logger.info(f'Getting ROIs for {self.image_name}')
            self.image, self.rois = iu.get_image_ROIs(
                chip_features=self.chip_features,
                image_path=self.first_file
            )
            self.save_ROIs()
        if Path(self.results_path, f'{self.image_name}.png').is_file():
            logger.warning(f'ROIs plotted for {self.image_name}')
            return
        else:
            self.plot_ROIs()

    def save_ROIs(self) -> None:
        """
        Function Details
        ================
        Save ROI data out to dictionary.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        -----------------------------------------------------------------------
        Update History
        ==============

        03/06/2025
        ----------
        Created.

        """
        if self.rois is None:
            raise RuntimeError('ROI data has not been built')
        save_json_dicts(
            out_path=self.out_path,
            dictionary=self.rois
        )

    def plot_ROIs(self) -> None:
        """
        Function Details
        ================
        Plot ROIs dictionary data with highlighted regions of interest.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        -----------------------------------------------------------------------
        Updated History
        ===============

        03/06/2025
        ----------
        Created.

        """
        if self.image is None or self.rois is None:
            raise RuntimeError('ROI data has not been built')
        plot.check_plot_ROIs(
            ROIs=self.rois,
            image=self.image,
            image_name=self.image_name,
            out_path=Path(self.results_path, f'{self.image_name}.png')
        )

    def get_ROI_labels(self) -> list[str]:
        """
        Function Details
        ================
        Get ROI labels from roi_file dictionary.

        Parameters
        ----------
        None.

        Returns
        -------
        list[str]
            Unique ROI label prefixes in their source order.

        ---------------------------------------------------------------------------
        Update History
        ==============

        02/05/2025
        ----------
        Created.

        """
        if self.rois is None:
            raise RuntimeError('ROI data has not been built')
        self.roi_labels = []
        for key, value in self.rois.items():
            if key != "image_angle":
                label = value["label"].split('_')[0]
                if label not in self.roi_labels:
                    self.roi_labels.append(label)
        return self.roi_labels

    def save_ROI_labels(self,
                        date: str,
                        sensor_labels: dict) -> dict:
        """
        Function Details
        ================
        Save ROI labels to results file.

        Parameters
        ----------
        date: str
            Measurement-date keys for the results dictionary.
        sensor_labels: dict
            Existing sensor-label mapping to update.

        Returns
        -------
        sensor_labels: dict
            Updated sensor_labels dictionary.

        ---------------------------------------------------------------------------
        Update History
        ==============

        02/05/2025
        ----------
        Created.

        """
        sample_label = []
        for label in self.roi_labels:
            if label not in sample_label:
                sample_label.append(label)
        if date not in sensor_labels:
            sensor_labels[date] = sample_label
        return sensor_labels


class ResultsExtractor:
    """
    Class Details
    =============
    Functions
    ---------
    Attributes
    ----------
    Notes
    -----
    ---------------------------------------------------------------------------
    Update History
    ==============

    17/06/2025
    ----------
    Created.

    16/09/2026
    ----------
    Updated functionality.

    """

    def __init__(
            self,
            images_dictionary: dict,
            image_config,
            output_path: Path,
            file_name: str
    ) -> None:
        """
        Function Details
        ================
        Initialize results extractor.

        Parameters
        ----------
        images_dictionary: dict
            Dictionary containing image data and results.
        image_config: object
            Image configuration object containing paths and settings.
        output_path: Path
            Path to save output results.
        file_name: str
            Name of the output file to save results.

        Returns
        -------
        None.

        Notes
        -----
        None.

        -----------------------------------------------------------------------
        Update History
        ==============

        17/06/2026
        ----------
        Created.

        """
        self.images_dictionary = images_dictionary
        self.image_config = image_config
        self.output_path = output_path
        self.file_name = file_name
        check_dir_exists(dir_path=self.output_path)
        logger.info(f'Output path set to: {self.output_path}')

        self.csv_dict = {
            "ID": [],
            "ROI": [],
            "ROI_label": [],
            "Image_brightness": [],
            "Image_contrast": [],
            "Analysis": [],
            "Filepath": []
        }

        self.analysis_method = self.image_config.ANALYSIS_METHOD.value

        self.gaussian_dict = {
            'Amplitude': [], 'Amplitude-std': [], 'Amplitude-lq': [],
            'Amplitude-uq': [], 'Amplitude-median': [], 'Amplitude-max': [],
            'Position': [], 'Position-std': [], 'Position-lq': [],
            'Position-uq': [], 'Position-median': [], 'Position-max': [],
            'Sigma': [], 'Sigma-std': [], 'Sigma-lq': [], 'Sigma-uq': [],
            'Sigma-median': [], 'Sigma-max': [],
            'Offset': [], 'Offset-std': [], 'Offset-lq': [], 'Offset-uq': [],
            'Offset-median': [], 'Offset-max': [],
            'Error': [], 'Error-std': [], 'Error-lq': [], 'Error-uq': [],
            'Error-median': [], 'Error-max': []
        }
        self.fano_dict = {
            'Amplitude': [], 'Amplitude-std': [], 'Amplitude-lq': [],
            'Amplitude-uq': [], 'Amplitude-median': [], 'Amplitude-max': [],
            'Asymmetry': [], 'Asymmetry-std': [], 'Asymmetry-lq': [],
            'Asymmetry-uq': [], 'Asymmetry-median': [], 'Asymmetry-max': [],
            'Resonance': [], 'Resonance-std': [], 'Resonance-lq': [],
            'Resonance-uq': [], 'Resonance-median': [], 'Resonance-max': [],
            'Gamma': [], 'Gamma-std': [], 'Gamma-lq': [], 'Gamma-uq': [],
            'Gamma-median': [], 'Gamma-max': [],
            'Offset': [], 'Offset-std': [], 'Offset-lq': [], 'Offset-uq': [],
            'Offset-median': [], 'Offset-max': [],
            'Error': [], 'Error-std': [], 'Error-lq': [], 'Error-uq': [],
            'Error-median': [], 'Error-max': []
        }
        self.hybrid_dict = {
            'Gauss-Amplitude': [], 'Gauss-Amplitude-std': [],
            'Gauss-Amplitude-lq': [], 'Gauss-Amplitude-uq': [],
            'Gauss-Amplitude-median': [], 'Gauss-Amplitude-max': [],
            'Gauss-Position': [], 'Gauss-Position-std': [],
            'Gauss-Position-lq': [], 'Gauss-Position-uq': [],
            'Gauss-Position-median': [], 'Gauss-Position-max': [],
            'Gauss-Sigma': [], 'Gauss-Sigma-std': [], 'Gauss-Sigma-lq': [],
            'Gauss-Sigma-uq': [], 'Gauss-Sigma-median': [],
            'Gauss-Sigma-max': [],
            'Gauss-Offset': [], 'Gauss-Offset-std': [], 'Gauss-Offset-lq': [],
            'Gauss-Offset-uq': [], 'Gauss-Offset-median': [],
            'Gauss-Offset-max': [],
            'Gauss-Error': [], 'Gauss-Error-std': [], 'Gauss-Error-lq': [],
            'Gauss-Error-uq': [], 'Gauss-Error-median': [],
            'Gauss-Error-max': [],
            'Fano-Amplitude': [], 'Fano-Amplitude-std': [],
            'Fano-Amplitude-lq': [], 'Fano-Amplitude-uq': [],
            'Fano-Amplitude-median': [], 'Fano-Amplitude-max': [],
            'Fano-Asymmetry': [], 'Fano-Asymmetry-std': [],
            'Fano-Asymmetry-lq': [], 'Fano-Asymmetry-uq': [],
            'Fano-Asymmetry-median': [], 'Fano-Asymmetry-max': [],
            'Fano-Resonance': [], 'Fano-Resonance-std': [],
            'Fano-Resonance-lq': [], 'Fano-Resonance-uq': [],
            'Fano-Resonance-median': [], 'Fano-Resonance-max': [],
            'Fano-Gamma': [], 'Fano-Gamma-std': [], 'Fano-Gamma-lq': [],
            'Fano-Gamma-uq': [], 'Fano-Gamma-median': [], 'Fano-Gamma-max': [],
            'Fano-Offset': [], 'Fano-Offset-std': [], 'Fano-Offset-lq': [],
            'Fano-Offset-uq': [], 'Fano-Offset-median': [],
            'Fano-Offset-max': [],
            'Fano-Error': [], 'Fano-Error-std': [], 'Fano-Error-lq': [],
            'Fano-Error-uq': [], 'Fano-Error-median': [], 'Fano-Error-max': []
        }

        logger.info(
            'Results Extractor Initialized:',
            f'Images Dictionary: {self.images_dictionary}',
            f'Image Config: {self.image_config}',
            f'Output Path: {self.output_path}',
            f'File Name: {self.file_name}',
            f'CSV Dictionary: {self.csv_dict}',
            f'Analysis Method: {self.analysis_method}',
            f'Gaussian Dictionary: {self.gaussian_dict}',
            f'Fano Dict: {self.fano_dict}',
            f'Hybrid Dict: {self.hybrid_dict}'
        )

    def _extracts_gaussians(
            self,
            ROI_key: Mapping[str, Mapping[str, float]]
    ) -> None:
        """
        Function Details
        ================
        Extract results to Gaussian dictionary.

        Parameters
        ----------
        ROI_key: Mapping[str, Mapping[str, float]]
            Gaussian results for one region of interest. It must contain
            ``amplitude``, ``mu``, ``sigma``, ``offset``, and ``error``
            mappings, each with ``Mean``, ``STD``, ``LQ``, ``UQ``,
            ``Median``, and ``Max`` values.

        Returns
        -------
        None
            Appends the extracted values to ``self.gaussian_dict``.

        Raises
        ------
        KeyError
            If a Gaussian result field or statistic is missing.

        -----------------------------------------------------------------------
        Update History
        ==============

        17/06/2025
        ----------
        Created.

        """
        result_fields = {
            'amplitude': 'Amplitude',
            'mu': 'Position',
            'sigma': 'Sigma',
            'offset': 'Offset',
            'error': 'Error'
        }
        statistic_fields = {
            'Mean': '',
            'STD': '-std',
            'LQ': '-lq',
            'UQ': '-uq',
            'Median': '-median',
            'Max': '-max'
        }

        for result_key, output_key in result_fields.items():
            result = ROI_key[result_key]
            for statistic, suffix in statistic_fields.items():
                self.gaussian_dict[f'{output_key}{suffix}'].append(
                    result[statistic]
                )

    def _extracts_fano(
            self,
            ROI_key: Mapping[str, Any]
    ) -> None:
        """
        Extract Fano results into ``self.fano_dict``.

        Parameters
        ----------
        ROI_key: Mapping[str, Any]
            Fano results containing ``amplitude``, ``asymmetry``,
            ``resonance``, ``gamma``, ``offset``, and ``error`` mappings.
            Each mapping must contain ``Mean``, ``STD``, ``LQ``, ``UQ``,
            ``Median``, and ``Max`` values.

        Returns
        -------
        None
            Appends the extracted values to ``self.fano_dict``.

        Raises
        ------
        KeyError
            If a Fano result field or statistic is missing.

        -----------------------------------------------------------------------
        Update History
        ==============

        16/09/2026
        ----------
        - Initial implementation.

        """
        result_fields = {
            'amplitude': 'Amplitude',
            'asymmetry': 'Asymmetry',
            'resonance': 'Resonance',
            'gamma': 'Gamma',
            'offset': 'Offset',
            'error': 'Error'
        }
        statistic_fields = {
            'Mean': '',
            'STD': '-std',
            'LQ': '-lq',
            'UQ': '-uq',
            'Median': '-median',
            'Max': '-max'
        }

        for result_key, output_key in result_fields.items():
            result = ROI_key[result_key]
            for statistic, suffix in statistic_fields.items():
                self.fano_dict[f'{output_key}{suffix}'].append(
                    result[statistic]
                )

    def _extracts_hybrid(
            self,
            ROI_key: Mapping[str, Any]
    ) -> None:
        """
        Extract hybrid Gaussian and Fano results into ``self.hybrid_dict``.

        Parameters
        ----------
        ROI_key: Mapping[str, Any]
            Hybrid results containing ``gaussian_amplitude``,
            ``gaussian_mu``, ``gaussian_sigma``, ``gaussian_offset``,
            ``gaussian_error``, ``fano_amplitude``, ``fano_asymmetry``,
            ``fano_resonance``, ``fano_gamma``, ``fano_offset``, and
            ``fano_error`` mappings. Each mapping must contain ``Mean``,
            ``STD``, ``LQ``, ``UQ``, ``Median``, and ``Max`` values.

        Returns
        -------
        None
            Appends the extracted values to ``self.hybrid_dict``.

        Raises
        ------
        KeyError
            If a hybrid result field or statistic is missing.

        -----------------------------------------------------------------------
        Update History
        ==============

        16/09/2026
        ----------
        - Initial implementation.

        """
        result_fields = {
            'gaussian_amplitude': 'Gauss-Amplitude',
            'gaussian_mu': 'Gauss-Position',
            'gaussian_sigma': 'Gauss-Sigma',
            'gaussian_offset': 'Gauss-Offset',
            'gaussian_error': 'Gauss-Error',
            'fano_amplitude': 'Fano-Amplitude',
            'fano_asymmetry': 'Fano-Asymmetry',
            'fano_resonance': 'Fano-Resonance',
            'fano_gamma': 'Fano-Gamma',
            'fano_offset': 'Fano-Offset',
            'fano_error': 'Fano-Error'
        }
        statistic_fields = {
            'Mean': '',
            'STD': '-std',
            'LQ': '-lq',
            'UQ': '-uq',
            'Median': '-median',
            'Max': '-max'
        }

        for result_key, output_key in result_fields.items():
            result = ROI_key[result_key]
            for statistic, suffix in statistic_fields.items():
                self.hybrid_dict[f'{output_key}{suffix}'].append(
                    result[statistic]
                )

    def dict_to_csv(
            self,
            output_dictionary: dict
    ) -> None:
        """
        Function Details
        ================
        Convert results dictionary to CSV file.

        Parameters
        ----------
        output_dictionary: dict
            Dictionary containing results to save.

        Returns
        -------
        None.

        -----------------------------------------------------------------------
        Update History
        ==============

        17/06/2025
        ----------
        Created.

        """
        csv_df = pd.DataFrame(data=output_dictionary)
        col_list = csv_df.columns.tolist()
        csv_df = csv_df[col_list]
        csv_df.to_csv(
            Path(
                self.output_path,
                self.file_name
            ),
            index=False
        )

    def extract_results(self) -> None:
        """
        Function Details
        ================
        Extract results from images dictionary and save to output file.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        Side Effects
        ------------
        Appends image and ROI metadata to ``csv_dict``, appends analysis
        statistics to the selected result dictionary, assigns ``output_dict``,
        and writes the resulting CSV file with ``index=False``. The analysis
        methods ``gaussian``, ``fano``, and ``fit_hybrid`` dispatch to their
        corresponding extraction methods and output dictionaries.

        Raises
        ------
        KeyError
            If required image, ROI, or analysis result fields are missing.
        OSError
            If the output CSV cannot be written.
        ValueError
            If pandas cannot construct a consistent output table.

        -----------------------------------------------------------------------
        Update History
        ==============

        17/06/2025
        ----------
        Created.

        """
        for key1, value1 in self.images_dictionary.items():
            if not value1["Processed"]:
                logger.info(f'{key1} not yet processed')
            logger.info(f'Processing {key1}')
            ID = key1

            try:
                image_brightness = value1["Brightness"]
            except KeyError:
                image_brightness = 'None'

            try:
                image_contrast = value1["Contrast"]
            except KeyError:
                image_contrast = 'None'

            filepath = Path(
                value1["Root Path"],
                value1["File Path"]
            )

            analysis_methods = {
                'gaussian': self._extracts_gaussians,
                'fano': self._extracts_fano,
                'fit_hybrid': self._extracts_hybrid
            }

            for key2, value2 in value1["Results"].items():
                ROI = key2
                ROI_label = value2["ROI_label"]
                self.csv_dict['ID'].append(ID)
                self.csv_dict['ROI'].append(ROI)
                self.csv_dict['ROI_label'].append(ROI_label)
                self.csv_dict['Analysis'].append(self.analysis_method)
                self.csv_dict['Image_brightness'].append(image_brightness)
                self.csv_dict['Image_contrast'].append(image_contrast)
                self.csv_dict['Filepath'].append(f'{filepath}')

                if self.analysis_method in analysis_methods:
                    method = analysis_methods[self.analysis_method]
                    method(ROI_key=value2)

                else:
                    logger.error(
                        f'Analysis method {self.analysis_method} '
                        f'not found for {key2}'
                    )

        result_dictionaries = {
            'gaussian': self.gaussian_dict,
            'fano': self.fano_dict,
            'fit_hybrid': self.hybrid_dict
        }
        method_dictionary = result_dictionaries.get(self.analysis_method, {})

        self.output_dict = dict(self.csv_dict, **method_dictionary)
        logger.info(f'Output dictionary: {self.output_dict}')
        self.dict_to_csv(output_dictionary=self.output_dict)
