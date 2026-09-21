###############################################################################
###############################################################################
#                               Data Processing                               #
#                             Author: Joshua Male                             #
#                               Date: 06/05/2025                              #
#                   Description: Data processing for images                   #
#                           Project: Phorest Analysis                         #
#                                                                             #
#                         Script Designed for Python 3                        #
#           © Copyright Christopher Reardon, Josh Male, PhorestDX             #
#                                                                             #
#                   Software Release: Unreleased/Prototype                    #
###############################################################################
###############################################################################

# Imports
import logging
import numpy as np
import pandas as pd

from pathlib import Path
from datetime import datetime

# Set up logging
logger = logging.getLogger(name=Path(__file__).stem)


class ProcessData:
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

    17/09/2026
    ----------
    - Initial implementation.

    """

    def __init__(
            self,
            results_dataframe: pd.DataFrame,
            analysis_method: str,
            chip_features: dict,
            results_dictionary: dict
    ) -> None:
        """
        Function Details
        ================
        Parameters
        ----------
        results_dataframe: pd.DataFrame
            Pandas dataframe from results csv.
        analysis_method: str
            Peak analysis technique.
        chip_features, results_dictionary: dict
            Chip features dictionary. Image results output dictionary.

        Returns
        -------
        None.

        Notes
        -----
        None.

        -----------------------------------------------------------------------
        Update History
        ==============

        17/09/2026
        ----------
        - Initial implementation.

        """
        self.results = results_dataframe
        self.analysis_method = analysis_method
        logger.info(
            f'Data Processing %s with analysis method %s',
            self.results,
            self.analysis_method
        )
        self.chip_features = chip_features
        self.results_dictionary = results_dictionary
        logger.info(
            f'Chip features %s, results dictionary %s',
            self.chip_features,
            self.results_dictionary
        )

    def process_max_intensity(self) -> None:
        """
        Function Details
        ================
        Parameters
        ----------
        Returns
        -------
        Notes
        -----
        -----------------------------------------------------------------------
        Update History
        ==============

        17/09/2026
        ----------
        - Initial implementation.

        """
        raise NotImplementedError('Subclasses to implement locate_gratings()')

    def process_centre(self) -> None:
        """
        Function Details
        ================
        Parameters
        ----------
        Returns
        -------
        Notes
        -----
        -----------------------------------------------------------------------
        Update History
        ==============

        17/09/2026
        ----------
        - Initial implementation.

        """
        raise NotImplementedError('Subclasses to implement locate_gratings()')

    def process_gaussian(self) -> None:
        """
        Function Details
        ================
        Parameters
        ----------
        Returns
        -------
        Notes
        -----
        -----------------------------------------------------------------------
        Update History
        ==============

        17/09/2026
        ----------
        - Initial implementation.

        """
        raise NotImplementedError('Subclasses to implement locate_gratings()')

    def process_fano(self) -> None:
        """
        Function Details
        ================
        Parameters
        ----------
        Returns
        -------
        Notes
        -----
        -----------------------------------------------------------------------
        Update History
        ==============

        17/09/2026
        ----------
        - Initial implementation.

        """
        raise NotImplementedError('Subclasses to implement locate_gratings()')

    def process_hybrid(
            self,
            roi_A_data: pd.DataFrame,
            roi_B_data: pd.DataFrame,
            sensor_label: str
    ) -> dict:
        """
        Function Details
        ================
        Process data fitted with hybrid function.

        Parameters
        ----------
        roi_A_data, roi_B_data: pd.DataFrame
            ROI A and B data frames.
        sensor_label: str
            Grating label as a string.

        Returns
        -------
        results: dict
            Results dictionary.

        Notes
        -----
        Change output here, it's not great.

        -----------------------------------------------------------------------
        Update History
        ==============

        17/09/2026
        ----------
        - Initial implementation.

        """
        # Image Brightness
        image_brightness_A = roi_A_data.iloc[0]['Image_brightness']
        image_brightness_B = roi_B_data.iloc[0]['Image_brightness']
        average_brightness = (image_brightness_A + image_brightness_B) / 2

        #Image contrast
        image_contrast_A = roi_A_data.iloc[0]['Image_contrast']
        image_contrast_B = roi_B_data.iloc[0]['Image_contrast']
        average_contrast = (image_contrast_A + image_contrast_B) / 2

        # Amplitude
        peak_amplitude_A = roi_A_data.iloc[0]['Gauss-Amplitude']
        peak_amplitude_B = roi_B_data.iloc[0]['Gauss-Amplitude']

        # Position
        central_position_A = roi_A_data.iloc[0]['Gauss-Position']
        central_position_B = roi_B_data.iloc[0]['Gauss-Position']

        # FWHM
        peak_fwhm_A = roi_A_data.iloc[0]['Gauss-Sigma']
        peak_fwhm_B = roi_B_data.iloc[0]['Gauss-Sigma']

        # DC Offset
        """ Fill out later """

        # Error
        error_A = roi_A_data.iloc[0]['Gauss-Error']
        error_B = roi_B_data.iloc[0]['Gauss-Error']

        # Paired Sum
        paired_sum, paired_error = self._paired_sum(
            position_A=central_position_A,
            position_B=central_position_B,
            error_A=error_A,
            error_B=error_B
        )

        # Effective index calculation
        effective_index, effective_index_error = self._effective_index(
            separation=paired_sum,
            separation_error=paired_error,
            grating_size=self.chip_features["Width"],
            um_to_pixel=self.chip_features["Micron to Pixel"],
            period_range=(
                self.chip_features["Grating Periods"][sensor_label]
            ),
            wavelength=self.chip_features["Wavelength"]
        )

        # Results
        results = {
            "Separation": paired_sum,
            "Separation Error": paired_error,
            "Effective Index": effective_index,
            "Effective Index Error": effective_index_error
        }
        return results

    def _paired_sum(
            self,
            position_A: float,
            position_B: float,
            error_A: float,
            error_B: float
    ) -> tuple[float, float]:
        """
        Function Details
        ================
        Calculate pixel distance between peaks.

        Parameters
        ----------

        Returns
        -------

        Notes
        -----

        -----------------------------------------------------------------------
        Update History
        ==============

        17/09/2026
        ----------
        - Initial implementation.

        """
        if position_A <= 0 or position_B <= 0:
            logger.warning('Negative data found, setting to 0')
            peak_A, peak_B = 0, 0
            err_A, err_B = 0, 0
        else:
            peak_A, peak_B = position_A, position_B
            err_A, err_B = error_A, error_B
        paired_sum = peak_A + peak_B
        paired_error = np.sqrt((err_A ** 2) + (err_B ** 2))
        return paired_sum, paired_error

    def _effective_index(
            self,
            separation: float,
            separation_error: float,
            grating_size: float,
            um_to_pixel: float,
            period_range: list,
            wavelength: float
    ) -> tuple[float, float]:
        """
        Function Details
        ================
        Calculate effective index of GMR mode.

        Parameters
        ----------

        Returns
        -------

        Notes
        -----

        -----------------------------------------------------------------------
        Update History
        ==============

        01/10/2025
        ----------
        Created.

        """
        error = separation_error / separation
        half_separation = separation / 2
        if half_separation > grating_size:
            logger.warning(
                f'Half separation {half_separation} greater than '
                f'grating size {grating_size}, setting to 0'
            )
            return 0, 0
        else:
            grating_position = half_separation / um_to_pixel
            period_factor = grating_position / grating_size
            period = (
                period_range[0] +
                ((period_range[1] - period_range[0]) * period_factor)
            )
            effective_index = wavelength / period
            effective_index_error = effective_index * error
            return effective_index, effective_index_error

    def process_data(
            self,
            roi_A: str,
            roi_B: str,
            sensor_label: str,
            timestamp: float,
            timestamp_error: float
        ):
        """
        Function Details
        ================
        Parameters
        ----------
        roi_A, roi_B, sensor_label, timestamp: str
            ROI labels. Grating label as a string. Date or timestamp.

        Returns
        -------
        Notes
        -----
        -----------------------------------------------------------------------
        Update History
        ==============

        17/09/2026
        ----------
        - Initial implementation.

        """
        analysis = {
            'max_intensity': self.process_max_intensity,
            'centre': self.process_centre,
            'gaussian': self.process_gaussian,
            'fano': self.process_fano,
            'fit_hybrid': self.process_hybrid
        }
        roi_A_data, roi_B_data = (
            self.results[self.results['ROI'] == roi_A],
            self.results[self.results['ROI'] == roi_B]
        )
        if not roi_A_data.empty and not roi_B_data.empty:
            logger.info('Both ROIs found in the data frame')
            calculated_results = analysis[self.analysis_method](
                roi_A_data,
                roi_B_data,
                sensor_label
            )
            results = self.results_dictionary["Results"]
            if sensor_label in results.keys():
                logger.info(f'{sensor_label} already in results')
                current_results = results[sensor_label]
                if timestamp not in current_results["Timestamp"]:
                    current_results["Timestamp"].append(
                        timestamp
                    )
                    current_results["Timestamp Error"].append(
                        timestamp_error
                    )
                    for key, value in calculated_results.items():
                        current_results[key].append(value)
                else:
                    logger.info(f'{timestamp} already exists')
            else:
                logger.info(f'Adding {sensor_label} to results')
                results[sensor_label] = {
                    'Timestamp': [timestamp],
                    'Timestamp Error': [timestamp_error]
                }
                for key, value in calculated_results.items():
                    results[sensor_label].update({key: [value]})
            return results
        else:
            logger.error('One ROIs missing data')
            exit(69)
