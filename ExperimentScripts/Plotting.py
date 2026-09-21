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
import math
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import GeneralUtils.FileIO as io

from pathlib import Path
from matplotlib.ticker import AutoMinorLocator

# Set up logging
logger = logging.getLogger(name=Path(__file__).stem)


def cm_to_inches(cm: float) -> float:
    """
    Function Details
    ================
    Returns centimeters as inches.

    Parameters
    ----------
    cm: float
        Dimensions in cm.

    Returns
    -------
    inches: float
        Dimensions in inches.

    Raises
    ------
    None.

    Notes
    -----
    Uses the conversion rate to convert a value given in centimeters to inches.
    Useful for matplotlib plotting.

    ---------------------------------------------------------------------------
    Update History
    ==============

    21/08/2026
    ----------
    - Initial implementation.

    """
    return round(cm * 0.393701, 2)


def plot_time(
        results_dict: dict,
        plot_parameters: dict
):
    """
    Function Details
    ================
    Parameters
    ----------
    Returns
    -------
    Notes
    -----
    ---------------------------------------------------------------------------
    Update History
    ==============

    17/09/2026
    ----------
    - Initial implementation.

    """
    metrics = [
        {
            "col": "Separation",
            "err": "Separation Error",
            "ylabel": "Bar Position [px]",
            "xlabel": plot_parameters.get("x-label", "Timestamp")
        },
        {
            "col": "Effective Index",
            "err": "Effective Index Error",
            "ylabel": "Effective Index [RIU]",
            "xlabel": plot_parameters.get("x-label", "Timestamp")
        }
    ]

    n_plots = len(metrics)
    ncols = 2 if n_plots > 1 else 1
    nrows = math.ceil(n_plots / ncols)

    fig_w = cm_to_inches(cm=plot_parameters["figsize"][0]) * ncols
    fig_h = cm_to_inches(cm=plot_parameters["figsize"][1]) * nrows

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=n_plots,
        figsize=[fig_w, fig_h],
    )
    axes = np.atleast_1d(axes).flatten()

    for ax in axes[n_plots:]:
        ax.set_visible(False)

    legend_handles, legend_labels = [], []

    if plot_parameters.get("fit-line", False):
        results_dict.setdefault("fits", {})

    for i, (key, values) in enumerate(list(results_dict["Results"].items())):
        if key == "fits":
            continue

        raw_data = (
            values["data"]
            if isinstance(values, dict) and "data" in values
            else values
        )
        df = pd.DataFrame(raw_data).sort_values(by="Timestamp")
        color = plot_parameters.get("err-color", f"C{i}")

        for ax, m in zip(axes, metrics):
            eb = ax.errorbar(
                x=df["Timestamp"],
                y=df[m["col"]],
                xerr=df["Timestamp Error"],
                yerr=df[m["err"]],
                fmt="o",
                ecolor=color,
                color=color,
                capsize=plot_parameters.get("err-capsize", 3),
                elinewidth=plot_parameters.get("err-width", 1),
                alpha=1,
                label=key,
            )

            if ax == axes[0]:
                legend_handles.append(eb)
                legend_labels.append(key)

            valids = df.dropna(subset=["Timestamp", m["col"]])
            if plot_parameters.get("fit-line", False) and len(valids) > 2:
                m_coef, c_coef = np.polyfit(
                    valids["Timestamp"],
                    valids[m["col"]],
                    plot_parameters.get("polyfit-order", 1),
                )
                x_fit = np.linspace(
                    valids["Timestamp"].min(), valids["Timestamp"].max(), 100
                )
                ax.plot(
                    x_fit,
                    m_coef * x_fit + c_coef,
                    color=color,
                    linestyle="--",
                    alpha=0.7,
                )

                if abs(m_coef) < 1e-2 or abs(m_coef) > 1e3:
                    eq_str = f"y = {m_coef:.2e}x + {c_coef:.2e}"
                else:
                    eq_str = f"y = {m_coef:.3f}x + {c_coef:.3f}"

                results_dict["fits"].setdefault(key, {})[m["col"]] = {
                    "slope": m_coef,
                    "intercept": c_coef,
                    "equation": eq_str,
                }

    for ax, m in zip(axes, metrics):
        ax.set_xlabel(
            m["xlabel"],
            fontsize=plot_parameters["axis-fontsize"],
            fontweight="bold",
        )
        ax.set_ylabel(
            m["ylabel"],
            fontsize=plot_parameters["axis-fontsize"],
            fontweight="bold",
        )
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.tick_params(
            axis="both", which="major", labelsize=plot_parameters["label-size"]
        )

    fig.legend(
        legend_handles,
        legend_labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.98),
        ncol=min(len(legend_labels), 5),
        prop={"size": plot_parameters["legend-size"]},
        frameon=True,
    )

    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.92))
    plt.savefig(
        plot_parameters["out-path"],
        bbox_inches="tight",
        dpi=plot_parameters.get("dpi", 600),
    )
    fig.clf()
    plt.cla()
    plt.close(fig)
    json_path = plot_parameters["out-path"].with_suffix('')
    json_out = json_path.with_suffix('.json')
    io.save_json_dicts(
        out_path=Path(json_out),
        dictionary=results_dict
    )
