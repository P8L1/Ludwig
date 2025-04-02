#!/usr/bin/env python
"""
Script to generate polar scatter plots for each harmonic number.
For each distinct harmonic number, the script queries all HarmonicRecord
entries and plots four series corresponding to the (v_prevail_angN, v_prevail_magN)
pairs. Each series is plotted as colored circles with a fixed marker size and
alpha transparency. The legend labels each series (e.g. "v_prevail_ang1") and
its marker size is reduced via the markerscale parameter.
The plot title is set to "Plot For Harmonic number X" using the "Goudy Old Style" font,
and angular tick labels are removed.
Each plot is saved as a PNG file in a 'plots' folder.
"""

import os
import sys
import argparse
import django
import numpy as np
import matplotlib.pyplot as plt

# Maximum number of records to process per harmonic (fixed upper bound)
MAX_RECORDS_PER_HARMONIC = 100000


def setup_django():
    """
    Setup the Django environment so that the ORM can be used.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ludwig.settings")
    django.setup()
    from django.conf import settings  # noqa: F401

    assert (
        os.environ.get("DJANGO_SETTINGS_MODULE") is not None
    ), "DJANGO_SETTINGS_MODULE must be defined"


def get_records_grouped_by_harmonic():
    """
    Queries the database and returns a dictionary mapping each distinct
    harmonic number (an integer) to a list of HarmonicRecord objects.
    """
    from ludwig.models import HarmonicRecord

    distinct_numbers = HarmonicRecord.objects.values_list(
        "harmonic_number", flat=True
    ).distinct()
    grouped_records = {}
    for harmonic in distinct_numbers:
        if not isinstance(harmonic, int):
            continue
        records = list(
            HarmonicRecord.objects.filter(harmonic_number=harmonic)[
                :MAX_RECORDS_PER_HARMONIC
            ]
        )
        grouped_records[harmonic] = records
    return grouped_records


def create_polar_plot_for_harmonic(harmonic, records):
    """
    For the given harmonic number and its records, create a polar scatter plot.
    For each record, we plot four (angle, magnitude) pairs (v_prevail_ang1 through v_prevail_ang4).
    Each series is plotted using colored circles with a fixed marker size and alpha transparency.
    A legend labels each series with its corresponding field name.
    The title is set to "Plot For Harmonic number X" using the 'Goudy Old Style' font.
    Angular tick labels are removed.

    The legend marker size is adjusted via the markerscale parameter (e.g., markerscale=0.5).
    The plot is saved as a PNG file in a 'plots' folder.
    """
    # Prepare separate lists for each series (1 through 4).
    series_data = {i: {"theta": [], "radius": []} for i in range(1, 5)}
    for record in records:
        for i in range(1, 5):
            angle_val = getattr(record, f"v_prevail_ang{i}", None)
            mag_val = getattr(record, f"v_prevail_mag{i}", None)
            if angle_val is not None and mag_val is not None:
                # Convert angle from degrees to radians.
                theta = np.deg2rad(angle_val)
                series_data[i]["theta"].append(theta)
                series_data[i]["radius"].append(mag_val)

    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

    # Define bright highlighter-like colors (adjust as desired).
    colors = {1: "#04ffc8", 2: "#2400ff", 3: "#fb07f4", 4: "#1fff04"}
    marker_size = 100
    alpha_val = 0.50

    for i in range(1, 5):
        theta_vals = series_data[i]["theta"]
        radius_vals = series_data[i]["radius"]
        if theta_vals and radius_vals:
            ax.scatter(
                theta_vals,
                radius_vals,
                marker="o",
                color=colors[i],
                s=marker_size,
                alpha=alpha_val,
                label=f"v_prevail_ang{i}",
            )

    from matplotlib.font_manager import FontProperties

    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "GoudyOldStyle.ttf")
    myfont = FontProperties(fname=font_path, size=10)
    ax.set_title(f"Plot For Harmonic number {harmonic}", fontproperties=myfont, fontsize=10)
    # Remove angular tick labels.
    ax.set_xticklabels([])

    # Adjust legend marker size. (markerscale controls the relative size of the legend markers.)
    ax.legend(
        loc="upper right", bbox_to_anchor=(1.2, 1.1), markerscale=0.3, prop={"size": 7}
    )

    # Save the plot.
    plots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    plot_file = os.path.join(plots_dir, f"harmonic_{harmonic}_plot.png")
    fig.savefig(plot_file, bbox_inches="tight")
    plt.close(fig)
    return plot_file


def main():
    """
    Main entry point: query the database, generate and save a plot for each harmonic number.
    """
    parser = argparse.ArgumentParser(
        description="Generate polar scatter plots for each harmonic number in the DB."
    )
    args = parser.parse_args()
    setup_django()
    grouped_records = get_records_grouped_by_harmonic()
    harmonic_count = 0
    for harmonic, records in grouped_records.items():
        print(
            f"DEBUG: Generating plot for harmonic {harmonic} with {len(records)} records."
        )
        plot_path = create_polar_plot_for_harmonic(harmonic, records)
        print(f"DEBUG: Plot saved to {plot_path}.")
        harmonic_count += 1
    print(f"Generated plots for {harmonic_count} harmonic numbers.")


if __name__ == "__main__":
    main()
