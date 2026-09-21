###############################################################################
###############################################################################
#                               Image Utilities                               #
#                             Author: Joshua Male                             #
#                              Date: 30/04/2025                               #
#                     Description: Image utility functions                    #
#                            Project: GMRProcessor                            #
#                                                                             #
#                         Script designed for Python 3                        #
#                           © Copyright Joshua Male                           #
#                                                                             #
#                            Software release: 0.1                            #
###############################################################################
###############################################################################

# Imports
import cv2
import logging
import numpy as np
import GeneralUtils.FileIO as io
import GeneralUtils.Plotting as plot

from pathlib import Path
from typing import Any, List, Tuple, Union, cast
from numpy.typing import NDArray
from ImageUtils.ROILocator import IMEC_ROI_Locator
from ImageUtils.AnalysisMethods import (
    max_intensity,
    centre,
    gaussian,
    fano,
    fit_hybrid
)

# Set up logging
logger = logging.getLogger(name=Path(__file__).stem)


def load_image_data(file_path: Path) -> NDArray:
    """
    Function Details
    ================
    Loads image data.

    Parameters
    ----------
    file_path: Path
        Path to image.

    Returns
    -------
    NDArray
        2D array containing pixel values.

    ---------------------------------------------------------------------------
    Update History
    ==============

    16/10/2024
    ----------
    Created function.

    """
    image = cv2.imread(str(file_path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"Unable to load image: {file_path}")

    image_array = np.asarray(image, dtype=np.float32)
    image_min = np.min(image_array)
    image_max = np.max(image_array)
    if image_max == image_min:
        normalized_image = np.zeros(image_array.shape, dtype=np.uint8)
    else:
        normalized_image = (
            (image_array - image_min) * 255.0 / (image_max - image_min)
        ).astype(np.uint8)
    return normalized_image


def get_image_ROIs(
        chip_features: dict,
        image_path: Path
    ) -> tuple:
    """
    Function Details
    ================
    Load image and regions of interest.

    Parameters
    ----------
    chip_features: dict
        Chip features dictionary.
    image_path: Path
        Path to image to find ROI.

    Returns
    -------
    image: matrix
        Matrix values for image.
    ROIs: dict
        Regions of interest dictionary.

    Notes
    -----
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    30/04/2025
    ----------
    Copied and documented.

    26/05/2026
    ----------
    Updated to chip type ROI locator.

    16/09/2026
    ----------
    Refactor.

    """
    try:
        sensor_type = chip_features["Sensor Type"]
        if 'IMEC' in sensor_type:
            logger.info(f'Processing {sensor_type}')
            roi_locator = IMEC_ROI_Locator(chip_features=chip_features)
            image = load_image_data(file_path=image_path)
            ROIs = roi_locator.find_ROIs(image=image)
            return image, ROIs
        else:
            logger.error(f'Chip Type not in use')
            exit(69)
    except FileNotFoundError:
        logger.error(f'File not found: {image_path}')
        exit(69)


def resize_image(
        image: NDArray[Any],
        new_width: int,
        new_height: int
    ) -> NDArray[Any]:
    """
    Function Details
    ================
    Resizes input image to the passed in dimensions.

    Parameters
    ----------
    image: NDArray[Any]
        Image to be rotated.
    new_width: int
        Width of image to be returned.
    new_height: int
        Height of image to be returned.

    Returns
    -------
    new_image: NDArray[Any]
        New resized image.

    ---------------------------------------------------------------------------
    Update History
    ==============

    07/08/2024
    ----------
    Created function. CR

    """
    return cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_LINEAR
    )


def split_into_subROIs(
        image: NDArray[Any],
        subROIs: int
    ) -> NDArray[Any]:
    """
    Function Details
    ================
    Splits array into smaller sub-arrays.  First the original array is sliced
    according to how many subROIs are required.  Each slice is then averaged
    along the vertical axis (i.e. the array/images height). These subROI 1D
    arrays are then returned as a 2D array.

    Parameters
    ----------
    image: NDArray[Any]
        Image to be split into subROIs.
    subROIs: int
        Number of sub-ROIs required.

    Returns
    -------
    subROIArray: NDArray[Any]
        2D array, each row representing one sub-ROI.

    ---------------------------------------------------------------------------
    Update History
    ==============

    07/08/2024
    ----------
    Created function. CR

    """
    _, width = image.shape
    return resize_image(image, width, subROIs)


def crop_image(
        image: NDArray[Any],
        coords: Union[List[List[int]], None] = None,
        show_data: bool = False
    ) -> NDArray[Any]:
    """
    Function Details
    ================
    Crops an image according to two coordinates, top-right and bottom-left,
    which define the bounding rectangle of the cropped area.
    - If coordinates are not supplied to the function, 'get_mouse_locations'
    is called so that the user can select two coordinates directly.

    Parameters
    ----------
    image: NDArray[Any]
        Image to be cropped.
    coords: List[List[int]] = None
        Optional coordinates (top-right, bottom-left) of area to be cropped.
    show_data: bool = False
        Optional flag to display the cropped image.

    Returns
    -------
    cropped_image: NDArray[Any]
        Resulting cropped image.

    ---------------------------------------------------------------------------
    Update History
    ==============

    07/08/2024
    ----------
    Created function. CR

    """
    if coords is None:
        coords = cast(
            List[List[int]],
            get_mouse_locations(
                image,
                2,
                'Select the top-right and bottom-left crop coordinates'
            )
        )

    if coords is None:
        raise ValueError("No crop coordinates were provided or selected")

    x = (coords[0][0], coords[1][0])
    y = (coords[0][1], coords[1][1])
    cropped_image = image[y[0]:y[1], x[0]:x[1]]

    if show_data:
        cv2.imshow('Cropped Image', cropped_image)
        cv2.waitKey(0)
        cv2.destroyWindow('Cropped Image')

    return cropped_image


def auto_brightness(image: NDArray[Any]) -> NDArray[np.uint16]:
    """
    Function Details
    ================
    Performs a simple brightness and contrast adjustment so that maximum pixel
    value from the original image becomes maximum allowed value.

    Parameters
    ----------
    image: NDArray[Any]
        Image to be brightness/contrast corrected.

    Returns
    -------
    corrected_image: NDArray[np.uint16]
        Corrected image.

    ---------------------------------------------------------------------------
    Update History
    ==============

    07/08/2024
    ----------
    Created function. CR
    """
    min_val, max_val = np.min(image), np.max(image)
    try:
        max_bit_value = np.finfo(image.dtype).max
    except ValueError:
        max_bit_value = np.iinfo(image.dtype).max
    normalized_image = (image - min_val) / (max_val - min_val) * max_bit_value
    return normalized_image.astype(image.dtype)


def get_mouse_locations(
        image: NDArray[Any],
        pts: int,
        message: str,
        display_res: Tuple[int, int] = (1280, 720)
    ) -> Union[List[int], List[List[int]]]:
    """
    Function Details
    ============================================================================
    Displays an image to the user and returns a list of coordinates according
    to where the user selects.
    - Once the coordinates have been selected pressing <Enter> causes the
    function to return.
    - If not enough coordinates have been selected when <Enter> is pressed a
    message is displayed to the user at the terminal.
    - Pressing <Esc> causes the function to return no coordinates, i.e. an
    empty list is returned.

    Parameters
    ----------
    image: NDArray[Any]
        Image to display to the user for selecting points.
    pts: int
        The number of coordinates required.
    message: str
        The message to display on the displayed image.

    Returns
    -------
    coords: Union[List[int], List[List[int]]]
        Returns either a list containing two integers. Or if more than one
        point is required, returns a list of lists containing two integers.

    Examples
    --------
    X, Y = get_mouse_locations(image, 1, 'Select 1 point')

    ----------------------------------------------------------------------------
    Update History
    ==============

    07 / 08 / 2024
    ----------
        Created function. CR
    """
    prev_coords: List[List[int]] = []
    coords: List[List[int]] = []


    def mouse_callback(
            event: int,
            x: int,
            y: int,
            flags: int,
            pts: Any | None
        ) -> None:
        nonlocal coords
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(coords) == pts:
                coords = [[x, y]]
            else:
                coords.append([x, y])


    cv2.namedWindow(f'Select {pts} point(s)')
    cv2.setMouseCallback(
        f'Select {pts} point(s)',
        mouse_callback,
        pts
    )
    # click_image = image.copy()
    click_image = resize_image(image, display_res[0], display_res[1])
    click_image = _draw_text(click_image, message)
    while True:
        if coords != prev_coords:
            click_image = resize_image(
                image,
                display_res[0],
                display_res[1]
            )
            click_image = _draw_text(click_image, message)
            for c in coords:
                click_image = _draw_cross(click_image, c)
        cv2.imshow(f'Select {pts} point(s)', click_image)
        key = cv2.waitKey(1)  # & 0xFF
        if key == 27:  # <Esc> key to exit
            coords = None # type: ignore
            break
        elif key == 13:  # <Enter> key to return coordinates
            if len(coords) < pts:
                print(f'Please select {pts} point(s)')
                print(f'You have only selected {len(coords)} points')
                continue
            break
        elif key == 32:  # <space> key to return an empty list
            coords = []
            break
    cv2.destroyAllWindows()
    if coords:
        h, w = image.shape
        for coord in coords:
            coord[0] = int(coord[0] * (w/display_res[0]))
            coord[1] = int(coord[1] * (h/display_res[1]))
    if coords and pts == 1:
        return coords[0]
    else:
        return coords


def _draw_cross(
        image: NDArray[Any],
        coord: List[int],
        colour: int = 65000,
        thickness: int = 2
    ) -> NDArray[Any]:
    """
    Function Details
    ============================================================================
    Displays a cross on an image at the supplied coordinates.

    Parameters
    ----------
    image: NDArray[Any]
        Image to display to the user for selecting points.
    coord: List[int, int]
        List of two coordinates required.

    Returns
    -------
    image: NDArray[Any]
        Returns an image with a cross.

    Examples
    --------
    image = draw_cross(image, [100, 100])

    ----------------------------------------------------------------------------
    Update History
    ==============

    07 / 08 / 2024
    ----------
        Created function. CR
    """
    length = 30
    pt = tuple(coord)
    cv2.line(
        image,
        (pt[0] - length, pt[1]),
        (pt[0] + length, pt[1]),
        colour,
        thickness
    )
    cv2.line(
        image,
        (pt[0], pt[1] - length),
        (pt[0], pt[1] + length),
        colour,
        thickness
    )
    return image


def _draw_text(
        image: NDArray[Any],
        text: str,
        thickness: int = 1,
        font_scale: float = 0.5
    ) -> NDArray[Any]:
    """
    Function Details
    ============================================================================
    Displays text at the bottom of the supplied image.

    Parameters
    ----------
    image: NDArray[Any]
        Image to display to the user for selecting points.
    text: str
        Text to display.

    Returns
    -------
    image: NDArray[Any]
        Returns an image with text.

    Examples
    --------
    image = draw_text(image, 'This is text on an image')

    ----------------------------------------------------------------------------
    Update History
    ==============

    07 / 08 / 2024
    ----------
        Created function. CR
    """
    fontFace = cv2.FONT_HERSHEY_SIMPLEX
    WHITE = 65000
    BLACK = 0
    # Calculate box dimensions with some padding
    (text_w, text_h), _ = cv2.getTextSize(
        text,
        fontFace,
        font_scale,
        thickness
    )
    box_padding = 10
    box_w = text_w + (2 * box_padding)
    box_h = text_h + (2 * box_padding)
    # Position the box at the bottom of the image
    image_height, image_width = image.shape
    box_x = int((image_width - box_w) / 2)  # Center the box horizontally
    box_y = image_height - box_h  # Position at the bottom
    # Center the text within the box
    text_x = box_x + int((box_w - text_w) / 2)
    text_y = box_y + int((box_h + text_h) / 2)
    cv2.rectangle(
        image,
        (box_x, box_y),
        (box_x + box_w, box_y + box_h),
        WHITE,
        cv2.FILLED
    )
    cv2.putText(
        image,
        text,
        (text_x, text_y),
        fontFace,
        font_scale,
        BLACK,
        thickness,
        cv2.LINE_AA
    )
    return image


def rotate_image_lossy(
        image: NDArray[Any],
        roi_centre: tuple,
        angle: float,
        show_data: bool = False
    ) -> NDArray[Any]:
    """
    Function Details
    ================
    Rotates image by specified angle.

    Parameters
    ----------
    image: NDArray[Any]
        Image data to be rotated.
    angle: float
        Angle, in degrees, through which to rotate image.
    show_data: bool = False
        Optional flag to display the rotated image.

    Returns
    -------
    rotated_image: NDArray[Any]
        Resulting rotated image.

    -----------------------------------------------------------------------
    Update History
    ==============

    07/08/2024
    ----------
    Created function.

    """
    h, w = image.shape
    if not roi_centre:
        roi_centre = (image.shape[1]//2, image.shape[0]//2)
    rotation_matrix = cv2.getRotationMatrix2D(roi_centre, -angle, 1.0)
    rotated_image = cv2.warpAffine(
        image,
        rotation_matrix,
        (w, h)
    )
    if show_data:
        cv2.imshow('Rotated Image', rotated_image)
        cv2.waitKey(0)  # Wait for any key to close cropped image
        cv2.destroyWindow('Rotated Image')
    return rotated_image


def process_roi(
        sensor: str,
        date: str,
        id_number: str,
        image_config: Any,
        measurement_path: Path,
        metapath: Path,
        images_dictionary: dict,
        roi_file: dict
    ) -> None:
    """
    Function Details
    ================
    Helper function to process sensor ROI data and extract output metrics to a
    CSV.

    Parameters
    ----------
    sensor, date, id_number: str
        Sensor name, date, and unique identifier for the image.
    image_config: object
        Image configuration objects.
    metapath: Path
        Path to the metadata directory.
    images_dictionary, roi_file: dict
        Dictionary containing the image metadata and ROI data for the sensor.

    Returns
    -------
    None.

    Notes
    -----

    ---------------------------------------------------------------------------
    Update History
    ==============

    29/05/2026
    ----------
    - Initial function development and testing.
    - Spawned from original process_sensors function.

    """
    output_data = Path(getattr(image_config, 'SAVE_PATH'), 'ROI_Data')
    io.check_dir_exists(dir_path=output_data)
    output_plot = Path(getattr(image_config, 'SAVE_PATH'), 'ROI_Processed')
    io.check_dir_exists(dir_path=output_plot)
    logger.info(f'Processing ROI for {sensor}_{date}')
    roi_processor = ROIProcessor(
        images_dictionary=images_dictionary,
        ROI_dictionary=roi_file,
        image_dictionary_path=Path(
            metapath,
            f'image_metadata_SU{id_number}'
        ),
        image_config=image_config,
        image_name=f'{sensor}_{date}',
        results_path=Path(output_data, measurement_path.stem),
        plot_path=Path(output_plot, measurement_path.stem)
    )
    results = roi_processor.process_images()
    logger.info(f'Extracting results for {sensor}_{date}')
    results_extractor = io.ResultsExtractor(
        images_dictionary=results,
        image_config=image_config,
        output_path=Path(output_data, measurement_path.stem),
        file_name=f'{sensor}_{date}.csv'
    )
    results_extractor.extract_results()


class ROIProcessor:
    """
    Class Details
    =============
    Process ROI data.
    
    Functions
    ---------
    __init__
    _checks_image_file_size
    get_brightness_contrast
    _extracts_roi_data_
    preprocess_roi_data
    postprocess_roi_results
    process_images
    
    Attributes
    ----------
    images_dictionary
    ROI_dictionary
    image_dictionary_path
    default_result
    rotates_image_lossy
    image_config
    image_name,
    out_path
    
    Notes
    -----
    
    ---------------------------------------------------------------------------
    Update History
    ==============
    
    03/06/2025
    ----------
    Created.
    
    """

    def __init__(
        self,
        images_dictionary: dict,
        ROI_dictionary: dict,
        image_dictionary_path: Path,
        image_config: Any,
        image_name: str,
        results_path: Path,
        plot_path: Path
    ):
        """
        Function Details
        ================
        Initialize ROI processor.

        Parameters
        ----------
        images_dictionary, ROI_dictionary: dict
            Image meta data dictionary. ROI selection dictionary.
        image_dictionary_path: Path
            Path to image meta data dictionary.
        image_config: yml
            Image configuration file.

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
        self.images_dictionary = images_dictionary
        self.ROI_dictionary = ROI_dictionary
        self.image_dictionary_path = image_dictionary_path
        self.default_result = {
            "Analysis-method": "gaussian",
            "amplitude": {
                "Values": [0],
                "Mean": 0, "STD": 0, "LQ": 0, "UQ": 0,
                "Median": 0, "Max": 0
            },
            "mu": {
                "Values": [0],
                "Mean": 0, "STD": 0, "LQ": 0, "UQ": 0,
                "Median": 0, "Max": 0
            },
            "sigma": {
                "Values": [0],
                "Mean": 0, "STD": 0, "LQ": 0, "UQ": 0,
                "Median": 0, "Max": 0
            },
            "offset": {
                "Values": [0],
                "Mean": 0, "STD": 0, "LQ": 0, "UQ": 0,
                "Median": 0, "Max": 0
            },
            "error": {
                "Values": [0],
                "Mean": 0, "STD": 0, "LQ": 0, "UQ": 0,
                "Median": 0, "Max": 0
            }
        }
        self.image_config = image_config
        self.image_name = image_name
        self.results_path = results_path
        self.plot_path = plot_path
        io.check_dir_exists(dir_path=self.results_path)
        io.check_dir_exists(dir_path=self.plot_path)
        logger.info(
            'ROI Processor:',
            f'Image Dictionary: {self.images_dictionary}',
            f'Image Dictionary Path: {image_dictionary_path}',
            f'ROI Dictionary: {self.ROI_dictionary}',
            f'Image Config: {self.image_config}',
            f'Image Name: {self.image_name}',
            f'Results Path: {self.results_path}'
        )

    def _checks_image_file_size(
            self,
            file_path: Path,
            size_threshold: float = 5_000_000
    ) -> bool:
        """
        Function Details
        ================
        Checks whether image file is 'correct'.

        Parameters
        ----------
        file_path: Path
            Path fo image file.
        size_threshold: float, optional
            Size threshold, default to 5000000 bits.

        Returns
        -------
        bool: bool
            True if above threshold.

        -----------------------------------------------------------------------
        Update History
        ==============

        16/10/2024
        ----------
        Created function.

        """
        return file_path.stat().st_size > size_threshold

    def get_brightness_contrast(
            self,
            data: np.ndarray
    ) -> Tuple[float, float]:
        """
        Function Details
        ================
        Get image brightness and contrast values.

        Parameters
        ----------
        data: NDArray
            Image data.

        Returns
        -------
        brightness, contrast: float
            Brightness and contrast values.

        -----------------------------------------------------------------------
        Update History
        ==============

        03/06/2025
        ----------
        Documented.

        """
        brightness = np.round(np.mean(data), 2)
        contrast = np.round(
            np.quantile(data, 0.95) -
            np.quantile(data, 0.05),
            2
        )
        return brightness, contrast

    def _extracts_roi_data_(
            self,
            data: NDArray,
            ID: str,
            ROIs: dict
    ) -> NDArray:
        """
        Function Details
        ================
        Use supplied metadata and ROIs dictionary, to return a slice of data
        that only includes the region of interest.

        Parameters
        ----------
        data: NDArray
            2D image array.
        ID: str
            String containing the key for retrieving the appropriate record
            from the ROI dictionary.
        ROIs: dict
            Dictionary containing all ROI metadata.

        Returns
        -------
        ROI_data: NDArray
            2D array containing pixel values of the region of interest.

        -----------------------------------------------------------------------
        Update History
        ==============

        16/10/2024
        ----------
        Created function.

        03/06/2025
        ----------
        Added flip data for region of interest A.

        16/09/2026
        ----------
        Removed aforementioned flip for data in region of interest.

        17/09/2026
        ----------
        Added flip data back in, do not remove, change plotting instead.

        """
        try:
            start_coord = ROIs[ID]['coords']
            end_coord = [
                x + y
                for x, y in
                zip(ROIs[ID]['coords'], ROIs[ID]['size'])
            ]
            selected_data = data[
                start_coord[0]:end_coord[0],
                start_coord[1]:end_coord[1]
            ]
        except KeyError as e:
            logger.error(f'An error occurred when reading ROI metadata - {e}')
            exit(69)

        ID_label = ROIs[ID]['label']
        if 'A' in ID_label:
            ROI_data = np.fliplr(selected_data)
        else:
            ROI_data = selected_data
        ROI_data = selected_data

        return ROI_data

    def rotates_image_lossy(
        self,
        image: NDArray[Any],
        roi_centre: tuple,
        angle: float,
        show_data: bool = False
    ) -> NDArray[Any]:
        """
        Function Details
        ================
        Rotates image by specified angle.

        Parameters
        ----------
        image: NDArray[Any]
            Image data to be rotated.
        angle: float
            Angle, in degrees, through which to rotate image.
        show_data: bool = False
            Optional flag to display the rotated image.

        Returns
        -------
        rotated_image: NDArray[Any]
            Resulting rotated image.

        -----------------------------------------------------------------------
        Update History
        ==============

        07/08/2024
        ----------
        Created function.

        """
        h, w = image.shape
        if not roi_centre:
            roi_centre = (image.shape[1]//2, image.shape[0]//2)
        rotation_matrix = cv2.getRotationMatrix2D(roi_centre, -angle, 1.0)
        rotated_image = cv2.warpAffine(
            image,
            rotation_matrix,
            (w, h)
        )
        if show_data:
            cv2.imshow('Rotated Image', rotated_image)
            cv2.waitKey(0)  # Wait for any key to close cropped image
            cv2.destroyWindow('Rotated Image')
        return rotated_image

    def preprocess_roi_data(
            self,
            data: NDArray,
            sub_rois: int
    ) -> NDArray:
        """
        Function Details
        ================
        Used to reduce the input ROI data so that it contains subROI data.

        Parameters
        ----------
        data: NDArray
            2D array representing an ROI of an image.
        sub_rois: int
            Number of sub-rois the ROI is to be split into, 0 indicates no
            sub-rois and to process the whole ROI row-by-row.

        Returns
        -------
        -: NDArray
            Array containing pixel values of the reduced region of interest.

        -----------------------------------------------------------------------
        Update History
        ==============

        16/10/2024
        ----------
        Created function.

        """
        if sub_rois == 0:
            return data
        else:
            _, width = data.shape
            return cv2.resize(
                data,
                (width, sub_rois),
                interpolation=cv2.INTER_LINEAR
            )

    def analyse_roidata(
            self,
            data: NDArray,
            analysis_method: str
    ) -> dict:
        """
        Function Details
        ================
        Analyses ROI data according the method passed to the function.

        Parameters
        ----------
        data: NDArray
            2D array representing an ROI of an image.
        analysis_method: str
            Method required for analysis.

        Returns
        -------
        results: dict
            Dictionary containing the analysis_method and the resulting
            analysis values.

        -----------------------------------------------------------------------
        Update History
        ==============

        16/10/2025
        ----------
        Created function.

        """
        analysis = {
            'max_intensity': max_intensity,
            'centre':        centre,
            'gaussian':      gaussian,
            'fano':          fano,
            'fit_hybrid':    fit_hybrid
        }
        results = {}
        error_count = 0
        for idx, d in enumerate(data):
            d_std = np.std(d)
            print(f'[INFO] Row {idx}, STD {d_std}')
            if d_std < 0.1:
                logger.warning(f'Row {idx}, peak contrast too low')
                print(f'[WARNING] Row {idx}, peak contrast too low')
                error_count += 1
                continue
            result_dict = analysis[analysis_method](d)
            if not bool(result_dict):
                logger.warning(f'Row {idx}, fitting function failed')
                print(f'[WARNING] Row {idx}, fitting function failed')
                error_count += 1
                continue
            for key, value in result_dict.items():
                if key not in results:
                    results['Analysis-method'] = analysis_method
                    results[key] = {'Values': []}
                if np.isnan(value):
                    continue
                results[key]['Values'].append(value)
        logger.info(
            f'{error_count} / {data.shape[0]} rows excluded from analysis'
        )
        return results

    def postprocess_roi_results(
            self,
            data: dict
    ) -> dict:
        """
        Function Details
        ================
        Analyses ROI data according to the method passed to the function.

        Parameters
        ----------
        data: dict
            Dictionary containing raw results from analyse_roidata().

        Returns
        -------
        results: dict
            Dictionary with statistical measurements added.

        -----------------------------------------------------------------------
        Updated History
        ===============

        16/10/2024
        ----------
        Created function.

        """
        dp = 3
        for key, value in data.items():
            if 'Analysis-method' in key:
                continue
            temp = np.array(value['Values'])
            data[key]['Mean'] = np.round(
                np.mean(temp),
                decimals=dp
            )
            data[key]['STD'] = np.round(
                np.std(temp),
                decimals=dp
            )
            data[key]['LQ'] = np.round(
                np.quantile(temp, 0.25),
                decimals=dp
            )
            data[key]['Median'] = np.round(
                np.quantile(temp, 0.50),
                decimals=dp
            )
            data[key]['UQ'] = np.round(
                np.quantile(temp, 0.75),
                decimals=dp
            )
            data[key]['Max'] = np.round(
                np.max(temp),
                decimals=dp
            )
        return data

    def process_images(self):
        """
        Function Details
        ================
        Loop images in images dictionary and process each ROI.

        Parameters
        ----------
        None.

        Returns
        -------
        self.images_dictionary: dict
            Modified images dictionary with results.

        -----------------------------------------------------------------------
        Update History
        ==============

        03/06/2025
        ----------
        Created.

        """
        for record_id in self.images_dictionary:
            logger.info(f'Processing image: {record_id}')
            image_record = self.images_dictionary[record_id]

            if image_record["Processed"] is True:
                logger.warning(f'Image {record_id} already processed, skip')
                continue

            image_filepath = Path(
                image_record["Root Path"],
                image_record["File Path"]
            )

            image_quality = self._checks_image_file_size(
                file_path=image_filepath
            )
            image_data = None
            if image_quality:
                logger.info(f'Image {image_filepath} above threshold quality')
                image_data = load_image_data(file_path=image_filepath)
            else:
                logger.error(f'Image does not match size: {image_filepath}')
                self.images_dictionary[record_id]["Error"] = " ".join(
                    [
                        self.images_dictionary[record_id]["Error"],
                        "Image incorrect size on disk"
                    ]
                )

            if image_data is None:
                logger.error(f'Error occurred opening image: {image_filepath}')
                self.images_dictionary[record_id]["Error"] = " ".join(
                    [
                        self.images_dictionary[record_id]["Error"],
                        "Image could not be loaded"
                    ]
                )

            if not image_quality or image_data is None:
                io.save_json_dicts(
                    out_path=self.image_dictionary_path,
                    dictionary=self.images_dictionary
                )
                continue

            brightness, contrast = self.get_brightness_contrast(
                data=image_data
            )
            image_record["Brightness"] = brightness
            image_record["Contrast"] = contrast

            rotated_image = self.rotates_image_lossy(
                image_data,
                (image_data.shape[1] // 2, image_data.shape[0] // 2),
                self.ROI_dictionary["image_angle"]
            )

            for ROI_ID in self.ROI_dictionary:
                if 'ROI' not in ROI_ID:
                    continue
                logger.info(f'Processing ROI: {ROI_ID}')

                ROI_data = self._extracts_roi_data_(
                    data=rotated_image,
                    ID=ROI_ID,
                    ROIs=self.ROI_dictionary
                )

                reduced_ROI_data = self.preprocess_roi_data(
                    data=ROI_data,
                    sub_rois=getattr(self.image_config, "NUMBER_SUB_ROIS")
                )

                result = self.analyse_roidata(
                    data=reduced_ROI_data,
                    analysis_method=self.image_config.ANALYSIS_METHOD.value
                )

                if not bool(result):
                    logger.warning(f'ROI {ROI_ID} - Resonance not visible')
                    result = self.default_result

                results = self.postprocess_roi_results(data=result)
                results["ROI_label"] = self.ROI_dictionary[ROI_ID]["label"]

                if 'Results' not in image_record:
                    image_record["Results"] = {}
                image_record["Results"].update({ROI_ID: result})
                image_record["Processed"] = True
                self.images_dictionary[record_id].update(image_record)
                io.save_json_dicts(
                    out_path=Path(f'{self.image_dictionary_path}.json'),
                    dictionary=self.images_dictionary
                )

                # Update ROI dictionary for plotting only
                if 'A' in self.ROI_dictionary[ROI_ID]["label"]:
                    try:
                        mean_position = (
                                self.ROI_dictionary[ROI_ID]['size'][1] -
                                results["mu"]["Mean"]
                            )
                    except KeyError:
                        mean_position = results["gaussian_mu"]["Mean"]
                else:
                    try:
                        mean_position = results["mu"]["Mean"]
                    except KeyError:
                        mean_position = results["gaussian_mu"]["Mean"]
                try:
                    sigma = results["sigma"]["Mean"]
                except KeyError:
                    sigma = results["gaussian_sigma"]["Mean"]
                self.ROI_dictionary[ROI_ID].update(
                    {
                        "Relative Position": mean_position,
                        "Relative Sigma": sigma
                    }
                )

            plot.plot_ROI_result(
                ROIs=self.ROI_dictionary,
                image=rotated_image,
                image_name=self.image_name,
                out_path=str(Path(self.plot_path, f'{self.image_name}.png'))
            )

        return self.images_dictionary
