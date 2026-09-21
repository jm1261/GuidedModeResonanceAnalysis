###############################################################################
###############################################################################
#                          ROI Locator Parent Class                           #
#                             Author: Joshua Male                             #
#                               Date: 03/06/2026                              #
#                        Description: ROI Locator Class                       #
#                           Project: Phorest Analysis                         #
#                                                                             #
#                         Script Designed for Python 3                        #
#           © Copyright Christopher Reardon, Josh Male, PhorestDX             #
#                                                                             #
#                   Software Release: Unreleased/Prototype                    #
###############################################################################
###############################################################################

# Imports
import cv2
import logging
import numpy as np
import ImageUtils.ImageUtilities as iu

from typing import Any
from pathlib import Path
from numpy.typing import NDArray

# Set up logging
logger = logging.getLogger(name=Path(__file__).stem)


class ROI_locator:
    """
    Class Details
    =============
    Base function ROI locator class for finding the ROIs in an image.

    Functions
    ---------
    __init__
    find_ROIs
    calculate_angle
    locate_features
    locate_gratings
    locate_ROIs
    get_chip_type
    get_label_locations
    get_image_angle
    get_grating_locations
    get_ROI_locations

    Attributes
    ----------
    chip_type: str
        The type of chip being analyzed.
    features: dict
        A dictionary containing the locations of the features in the image.
    angle: float
        The angle of the image.
    grating_locs: dict
        A dictionary containing the locations of the gratings in the image.
    ROI_locations: dict
        A dictionary containing the locations of the ROIs in the image.

    Notes
    -----
    Base class.

    ---------------------------------------------------------------------------
    Update History
    ==============

    03/06/2026
    ----------
    - Initial development and testing.
    - Copied from Christopher Reardon's original implementation.

    """

    def __init__(self):
        """
        Function Details
        ================
        Initialization function for the ROILocator class.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        -----------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.
        - Copied from Christopher Reardon's original implementation.

        """
        self.chip_type = None
        self.features = None
        self.angle = None
        self.grating_locs = None
        self.ROI_locations = None

    def find_ROIs(self, image: NDArray[Any]) -> None:
        """
        Function Details
        ================
        Function to find the ROIs in the image.

        Parameters
        ----------
        image: NDArray[Any]
            The input image as a NumPy array.

        Returns
        -------
        None.

        -------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.
        - Copied from Christopher Reardon's original implementation.

        """
        self.calculate_angle(image=image)
        if self.angle is None:
            raise RuntimeError('calculate_angle() did not set an image angle')
        image_centre = (image.shape[0]//2, image.shape[1]//2)
        rotated_image = iu.rotate_image_lossy(
            image,
            image_centre,
            self.angle
        )
        self.locate_features(image=rotated_image)
        self.locate_gratings()
        self.locate_ROIs()
        if self.ROI_locations is None:
            raise RuntimeError('locate_ROIs() did not set ROI locations')
        self.ROI_locations['image_angle'] = self.angle
        return self.ROI_locations

    def calculate_angle(self, image: NDArray[Any]) -> None:
        """
        Function Details
        ================
        Function to calculate the angle of the image.

        Parameters
        ----------
        image: NDArray[Any]
            The input image as a NumPy array.

        Returns
        -------
        None.

        -------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.
        - Copied from Christopher Reardon's original implementation.

        """
        raise NotImplementedError('Subclasses to implement calculate_angle()')

    def locate_features(self, image: NDArray[Any]) -> None:
        """
        Function Details
        ================
        Function to locate the features in the image.

        Parameters
        ----------
        image: NDArray[Any]
            The input image as a NumPy array.

        Returns
        -------
        None.

        -------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.
        - Copied from Christopher Reardon's original implementation.

        """
        raise NotImplementedError('Subclasses to implement locate_features()')

    def locate_gratings(self):
        """
        Function Details
        ================
        Function to locate the gratings in the image.

        Parameters
        ----------
        image: NDArray[Any]
            The input image as a NumPy array.

        Returns
        -------
        None.

        -------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.
        - Copied from Christopher Reardon's original implementation.

        """
        raise NotImplementedError('Subclasses to implement locate_gratings()')

    def locate_ROIs(self):
        """
        Function Details
        ================
        Function to locate the ROIs in the image.

        Parameters
        ----------
        image: NDArray[Any]
            The input image as a NumPy array.

        Returns
        -------
        None.

        -------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.
        - Copied from Christopher Reardon's original implementation.

        """
        raise NotImplementedError('Subclasses to implement locate_ROIs()')

    def get_chip_type(self):
        """
        Function Details
        ================
        Function to get the chip type.
        
        Parameters
        ----------
        image: NDArray[Any]
            The input image as a NumPy array.

        Returns
        -------
        None.

        -------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.
        - Copied from Christopher Reardon's original implementation.

        """
        return self.chip_type

    def get_label_locations(self):
        """
        Function Details
        ================
        Function to get label locations.

        Parameters
        ----------
        image: NDArray[Any]
            The input image as a NumPy array.

        Returns
        -------
        None.

        -------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.
        - Copied from Christopher Reardon's original implementation.

        """
        return self.features

    def get_image_angle(self):
        """
        Function Details
        ================
        Function to get the image angle.

        Parameters
        ----------
        image: NDArray[Any]
            The input image as a NumPy array.

        Returns
        -------
        None.

        -------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.
        - Copied from Christopher Reardon's original implementation.

        """
        return self.angle

    def get_grating_locations(self):
        """
        Function Details
        ================
        Function to get grating locations.

        Parameters
        ----------
        image: NDArray[Any]
            The input image as a NumPy array.

        Returns
        -------
        None.

        -------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.
        - Copied from Christopher Reardon's original implementation.

        """
        return self.grating_locs

    def get_ROI_locations(self):
        """
        Function Details
        ================
        Function to get ROI locations.

        Parameters
        ----------
        image: NDArray[Any]
            The input image as a NumPy array.

        Returns
        -------
        None.

        -------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.
        - Copied from Christopher Reardon's original implementation.

        """
        return self.ROI_locations


class IMEC_ROI_Locator(ROI_locator):
    """
    Class Details
    =============
    ROI locator class for IMEC chips.

    Functions
    ---------
    __init__
    calculate_angle
    locate_features
    locate_gratings
    locate_ROIs

    Attributes
    ----------
    chip_type
    chip_features
    features
    angle
    size
    ROI_locations

    Notes
    -----

    ---------------------------------------------------------------------------
    Update History
    ==============

    03/06/2026
    ----------
    - Initial development and testing.
    - Copied from Christopher's original implementation.
    - Adjusted based on Joshua's testing and development.

    """

    chip_features: dict

    def __init__(
            self,
            chip_features: dict
    ) -> None:
        """
        Function Details
        ================
        Initialization function for the IMEC_ROI_Locator class.

        Parameters
        ----------
        chip_features: dict
            A dictionary containing the features of the chip.

        Returns
        -------
        None.

        -----------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.

        """
        self.chip_type = chip_features['Chip Type']
        self.chip_features = chip_features['Grating Periods']
        self.features = {}
        logger.info(
            'Finding ROIs for chip type %s with features %s',
            self.chip_type,
            self.chip_features
        )

    def calculate_angle(
            self,
            image: NDArray[Any]
        ) -> None:
        """
        Function Details
        ================
        Uses the coordinates of the features within the supplied dictionary to
        calculate the vertical angle. Optionally supplied with a filter
        character that allows feature keys to be ignore if required.

        Parameters
        ----------
        image: NDArray[Any]
            Image to be searched.

        Returns
        -------
        None

        -----------------------------------------------------------------------
        Update History
        ==============

        09/08/2024
        ----------
        - Created function, CR.

        """
        message = 'Select 2 vertical pts (upper-lower), then press <Enter>'
        coords = iu.get_mouse_locations(
            image=image,
            pts=2,
            message=message
        )
        # Normalize the returned coordinates so that each selected point is
        # indexed as a coordinate pair rather than as an integer.
        coords_array = np.asarray(coords)
        opp = (coords_array[0, 0] - coords_array[1, 0])
        adj = (coords_array[0, 1] - coords_array[1, 1])
        self.angle = (np.arctan(opp / adj) * 180) / np.pi

    def locate_features(
            self,
            image: NDArray[Any]
        ) -> None:
        """
        Function Details
        ================
        Using user selected coordinates, define the top-left coordinate of the
        grating and it's size.

        Parameters
        ----------
        image: NDArray[Any]
            Image to be searched.

        Returns
        -------
        None.

        -----------------------------------------------------------------------
        Update History
        ==============

        09/08/2024
        ----------
        - Created function, CR.

        26/09/2025
        ----------
        - Updated to use get_mouse_loc_chems to allow user to skip labels by
        pressing spacebar. JM.

        03/06/2026
        ----------
        - Removed get_mouse_loc_chems and made get_mouse_locations do the same
        thing.

        """
        self.size = {}
        remaining_labels = list(self.chip_features.keys())
        while remaining_labels:
            for idx in list(remaining_labels):
                message = (
                    f'Select label {idx}, upper-left - lower-right,'
                    f' then press <Enter>'
                )
                coords = iu.get_mouse_locations(
                    image=image,
                    pts=2,
                    message=message
                )
                if coords is None:
                    return
                elif len(coords) == 0:
                    continue
                self.features[f'{idx}'] = coords[0]
                self.size[f'{idx}'] = np.array(coords[1]) - np.array(coords[0])
                coords_array = np.asarray(coords, dtype=int)
                upper_left = (
                    int(coords_array[0][0]), int(coords_array[0][1])
                )
                lower_right = (
                    int(coords_array[1][0]), int(coords_array[1][1])
                )
                image = cv2.rectangle(
                    image, upper_left, lower_right, 255, 2
                )
                remaining_labels.remove(idx)

    def locate_gratings(self):
        """
        Function Details
        ================
        Using the location of the features, calculate the location of the
        gratings.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        -----------------------------------------------------------------------
        Update History
        ==============

        03/06/2026
        ----------
        - Initial development and testing.

        """
        pass

    def locate_ROIs(self):
        """
        Function Details
        ================
        Determine the location of the ROIs needed for processing the GMR
        resonance location. Taking the location from features dictionary and
        size of the gratings, two ROIs per grating are located and their
        coordinates and size returned in the form of a dictionary. Optionally
        supplied with a filter character that allows the feature keys to be
        ignored if required.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        -----------------------------------------------------------------------
        Update History
        ==============

        09/08/2024
        ----------
        - Created function, CR.

        """
        self.ROI_locations = {}
        idx = 0
        for k, v in self.features.items():
            self.ROI_locations[f'ROI_{idx}'] = {
                                'label': f'{k}_A',
                                'coords': (int(v[1]), int(v[0])),
                                'size': (
                                    int(self.size[k][1]),
                                    int(self.size[k][0]//2)
                                )
            }
            idx += 1
            self.ROI_locations[f'ROI_{idx}'] = {
                                'label': f'{k}_B',
                                'coords': (
                                    int(v[1]), int(v[0] +
                                    (self.size[k][0]//2))
                                ),
                                'size': (
                                    int(self.size[k][1]),
                                    int(self.size[k][0]//2)
                                )
            }
            idx += 1
