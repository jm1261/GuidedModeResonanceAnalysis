###############################################################################
###############################################################################
#                                   Plotting                                  #
#                             Author: Joshua Male                             #
#                              Date: 02/05/2025                               #
#                       Functions for general plotting                        #
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
import matplotlib.pyplot as plt
import GeneralUtils.FileIO as gio
import matplotlib.patches as patches

from pathlib import Path
from scipy import ndimage
from numpy.typing import NDArray

# Set up logging
logger = logging.getLogger(name=Path(__file__).stem)


def check_plot_ROIs(ROIs: dict,
                    image: NDArray[np.uint16],
                    image_name: str,
                    out_path: Path) -> None:
    """
    Function Details
    ================
    Plot regions of interest.

    Parameters
    ----------
    ROIs: dict
        Dictionary for regions of interest.
    image: NDArray
        Image data.
    image_name, out_path: str
        Image name identifier, out path to save.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    03/06/2025
    ----------
    Created.

    """
    fig, ax = plt.subplots(
        nrows=1,
        ncols=1,
        figsize=[15, 9],
        dpi=600
    )
    rotated_image = ndimage.rotate(
        image,
        -ROIs["image_angle"],
        reshape=True,
        order=3
    )
    ax.imshow(
        rotated_image,
        cmap='viridis',
        interpolation='nearest'
    )
    for ROI, values in ROIs.items():
        if 'ROI' not in ROI:
            continue
        else:
            top_left_y, top_left_x = values["coords"]
            height, width = values["size"]
            label = values["label"]
            rect = patches.Rectangle(
                (top_left_x, top_left_y),
                width,
                height,
                linewidth=2,
                edgecolor='red',
                facecolor='none',
                linestyle='--'
            )
            ax.add_patch(rect)
            ax.text(
                top_left_x,
                top_left_y - 10,
                label,
                color='red',
                fontsize=12,
                ha='left',
                va='bottom'
            )
    ax.set_title(
        f'{image_name} Regions of Interest Selected',
        fontsize=14,
        fontweight='bold'
    )
    fig.tight_layout()
    plt.savefig(
        out_path,
        bbox_inches='tight'
    )
    plt.close(fig)


def plot_ROI_result(ROIs: dict,
                    image: NDArray[np.uint16],
                    image_name: str,
                    out_path: str) -> None:
    """
    Function Details
    ================
    Plot regions of interest results.

    Parameters
    ----------
    ROIs, results_dict: dict
        Dictionary for regions of interest.
    image: NDArray
        Image data.
    image_name, out_path: str
        Image name identifier, out path to save.

    Returns
    -------
    None.

    ---------------------------------------------------------------------------
    Update History
    ==============

    03/06/2025
    ----------
    Created.

    """
    fig, ax = plt.subplots(
        nrows=1,
        ncols=1,
        figsize=[15, 9],
        dpi=600
    )
    ax.imshow(image, cmap='viridis', interpolation='nearest')
    for ROI, values in ROIs.items():
        if 'ROI' not in ROI:
            continue
        else:
            top_left_y, top_left_x = values["coords"]
            height, width = values["size"]
            label = values["label"]
            relative_position = values["Relative Position"]
            relative_sigma = values["Relative Sigma"]
            rect = patches.Rectangle(
                (top_left_x, top_left_y),
                width,
                height,
                linewidth=2,
                edgecolor='red',
                facecolor='none',
                linestyle='--'
            )
            ax.add_patch(rect)
            ax.text(
                top_left_x,
                top_left_y - 10,
                label,
                color='red',
                fontsize=12,
                ha='left',
                va='bottom'
            )
            if relative_position is not None:
                line_absolute = top_left_x + relative_position
                ax.plot(
                    [line_absolute, line_absolute],
                    [top_left_y, top_left_y + height],
                    color='goldenrod',
                    linewidth=2,
                    linestyle='-'
                )
                ax.text(
                    line_absolute + 10,
                    top_left_y + height / 2,
                    f'{round(relative_position, 2)}',
                    color='goldenrod',
                    fontsize=20,
                    ha='left',
                    va='center',
                    rotation=90
                )
            if relative_sigma is not None:
                line_absolute = top_left_x + relative_position
                line_pos = line_absolute + (relative_sigma / 2)
                line_neg = line_absolute - (relative_sigma / 2)
                ax.plot(
                    [line_pos, line_pos],
                    [top_left_y, top_left_y + height],
                    color='goldenrod',
                    linewidth=1,
                    linestyle='--'
                )
                ax.plot(
                    [line_neg, line_neg],
                    [top_left_y, top_left_y + height],
                    color='goldenrod',
                    linewidth=1,
                    linestyle='--'
                )
    ax.set_title(
        f'{image_name} Regions of Interest Processed',
        fontsize=14,
        fontweight='bold'
    )
    fig.tight_layout()
    plt.savefig(
        out_path,
        bbox_inches='tight'
    )
    plt.close(fig)
