#!/usr/bin/env python
"""
Script to generate polar scatter plots for each harmonic number.
For each distinct harmonic number, the script queries all HarmonicRecord
entries and plots two sets of data:
  1. Measured (Angle, Magnitude) pairs for each channel: (v_prevail_ang1, v_prevail_mag1)
     through (v_prevail_ang4, v_prevail_mag4).
  2. Magnitude-only points: for each channel, plot the v_prevail_magX value at a fixed angle.
     The fixed angles are: channel 1 = 0 rad, channel 2 = π/2, channel 3 = π, channel 4 = 3π/2.
Each series is plotted as colored circles with fixed marker size and alpha transparency.
A legend labels each series with custom labels:
  - "Prevail Ang X" for the measured angle data,
  - "Prevail Mag X" for the magnitude-only data,
all rendered in Goudy Old Style.
Angular tick labels are removed.
Each plot is saved as a PNG file in a 'plots' folder.
"""

import os
import sys
import argparse
import django
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

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
    assert os.environ.get("DJANGO_SETTINGS_MODULE") is not None, "DJANGO_SETTINGS_MODULE must be defined"

def get_records_grouped_by_harmonic():
    """
    Queries the database and returns a dictionary mapping each distinct
    harmonic number (an integer) to a list of HarmonicRecord objects.
    """
    from ludwig.models import HarmonicRecord
    distinct_numbers = HarmonicRecord.objects.values_list("harmonic_number", flat=True).distinct()
    grouped_records = {}
    for harmonic in distinct_numbers:
        if not isinstance(harmonic, int):
            continue
        records = list(HarmonicRecord.objects.filter(harmonic_number=harmonic)[:MAX_RECORDS_PER_HARMONIC])
        grouped_records[harmonic] = records
    return grouped_records

def create_polar_plot_for_harmonic(harmonic, records):
    """
    For the given harmonic number and its records, create a polar scatter plot.
    The plot includes two sets of data:
      1. Measured (Angle, Magnitude) pairs using the v_prevail_angX and v_prevail_magX fields.
      2. Magnitude-only points: for each channel, plot the v_prevail_magX value at a fixed angle.
         Fixed angles are: channel 1 = 0 rad, channel 2 = π/2, channel 3 = π, channel 4 = 3π/2.
    Each series is plotted as colored circles with fixed marker size and alpha transparency.
    A legend labels each series with custom labels ("Prevail Ang X" and "Prevail Mag X")
    rendered in the custom Goudy Old Style font.
    Angular tick labels are removed.
    The plot is saved as a PNG file in a 'plots' folder.
    """
    # Prepare series for measured (Angle, Magnitude) pairs.
    series_data = {i: {"theta": [], "radius": []} for i in range(1, 5)}
    # Also prepare series for magnitude-only data.
    mag_series_data = {i: [] for i in range(1, 5)}
    for record in records:
        for i in range(1, 5):
            angle_val = getattr(record, f"v_prevail_ang{i}", None)
            mag_val = getattr(record, f"v_prevail_mag{i}", None)
            if angle_val is not None and mag_val is not None:
                theta = np.deg2rad(angle_val)  # convert measured angle to radians
                series_data[i]["theta"].append(theta)
                series_data[i]["radius"].append(mag_val)
            if mag_val is not None:
                mag_series_data[i].append(mag_val)

    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

    # Define unique colors for each channel.
    colors = {
        1: {"angle": "#FF0000", "mag": "#FF00FF"},  # Channel 1: Red for angle, Magenta for magnitude
        2: {"angle": "#00FF00", "mag": "#00FFFF"},  # Channel 2: Green for angle, Cyan for magnitude
        3: {"angle": "#0000FF", "mag": "#FFA500"},  # Channel 3: Blue for angle, Orange for magnitude
        4: {"angle": "#FFFF00", "mag": "#800080"},  # Channel 4: Yellow for angle, Purple for magnitude
    }
    
    marker_size = 100
    alpha_val = 0.50

    # Plot measured (Angle, Magnitude) pairs.
    for i in range(1, 5):
        theta_vals = series_data[i]["theta"]
        radius_vals = series_data[i]["radius"]
        if theta_vals and radius_vals:
            ax.scatter(
                theta_vals,
                radius_vals,
                marker="o",
                color=colors[i]["angle"],
                s=marker_size,
                alpha=alpha_val,
                label=f"Prevail Ang {i}"
            )

    # Define fixed angles for magnitude-only series.
    fixed_angles = {1: 0, 2: np.pi/2, 3: np.pi, 4: 3*np.pi/2}
    # Plot magnitude-only data at fixed angles.
    for i in range(1, 5):
        mags = mag_series_data[i]
        if mags:
            theta_fixed = np.full(len(mags), fixed_angles[i])
            ax.scatter(
                theta_fixed,
                mags,
                marker="o",
                color=colors[i]["mag"],
                s=marker_size,
                alpha=alpha_val,
                label=f"Prevail Mag {i}"
            )

    # Load custom font from local fonts folder.
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "GoudyOldStyle.ttf")
    myfont = FontProperties(fname=font_path, size=10)
    ax.set_title(f"Plot For Harmonic number {harmonic}", fontproperties=myfont, fontsize=10)

    # Remove angular tick labels.
    ax.set_xticklabels([])

    # Create a legend with custom font in the right corner.
    legend_font = FontProperties(fname=font_path, size=7)
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1), markerscale=0.3, prop=legend_font)

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
        print(f"DEBUG: Generating plot for harmonic {harmonic} with {len(records)} records.")
        plot_path = create_polar_plot_for_harmonic(harmonic, records)
        print(f"DEBUG: Plot saved to {plot_path}.")
        harmonic_count += 1
    print(f"Generated plots for {harmonic_count} harmonic numbers.")

if __name__ == "__main__":
    main()
