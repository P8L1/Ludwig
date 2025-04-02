#!/usr/bin/env python
"""
Script to generate polar scatter plots for each harmonic number.
For each distinct harmonic number, the script queries all HarmonicRecord
entries and produces two separate plots:
  1. A plot for the v_prevail_* fields:
       - Measured (Angle, Magnitude) pairs: (v_prevail_ang1, v_prevail_mag1) ... (v_prevail_ang4, v_prevail_mag4)
       - Magnitude-only points plotted at fixed angles:
         channel 1 at 0 rad, channel 2 at π/2, channel 3 at π, channel 4 at 3π/2.
       Legend labels are "Prevail Ang X" and "Prevail Mag X".
  2. A plot for the I_prevail_* fields:
       - Measured (Angle, Magnitude) pairs: (I_prevail_ang1, I_prevail_mag1) ... (I_prevail_ang4, I_prevail_mag4)
       - Magnitude-only points at fixed angles as above.
       Legend labels are "I Prevail Ang X" and "I Prevail Mag X".
All legend text is rendered in the custom Goudy Old Style font (loaded from the local fonts folder).
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

def create_polar_plot_for_group(harmonic, records, prefix, legend_ang, legend_mag, title_suffix):
    """
    Create a polar scatter plot for the given harmonic number and a given group of fields.
    
    Parameters:
      harmonic     : the harmonic number.
      records      : a list of HarmonicRecord objects.
      prefix       : the prefix string to use for field names (e.g. "v_prevail_" or "I_prevail_").
      legend_ang   : the label base for the measured angle data (e.g. "Prevail Ang" or "I Prevail Ang").
      legend_mag   : the label base for the magnitude data (e.g. "Prevail Mag" or "I Prevail Mag").
      title_suffix : a string appended to the plot title (e.g. "v_prevail" or "I_prevail").
    
    The function extracts for channels 1 to 4:
      - Measured angles (converted from degrees to radians) from field {prefix}angX.
      - Magnitudes from field {prefix}magX.
    It plots:
      1. The (angle, magnitude) pairs.
      2. The magnitude-only points, plotted at fixed angles:
         channel 1 at 0, channel 2 at π/2, channel 3 at π, channel 4 at 3π/2.
    Unique colors are assigned per channel.
    The plot title and legend use the custom Goudy Old Style font.
    Angular tick labels are removed.
    The plot is saved in a 'plots' folder.
    """
    # Prepare data for measured (Angle, Magnitude) pairs.
    series_data = {i: {"theta": [], "radius": []} for i in range(1, 5)}
    # Prepare data for magnitude-only series.
    mag_series_data = {i: [] for i in range(1, 5)}
    for record in records:
        for i in range(1, 5):
            ang_field = f"{prefix}ang{i}"
            mag_field = f"{prefix}mag{i}"
            angle_val = getattr(record, ang_field, None)
            mag_val = getattr(record, mag_field, None)
            if angle_val is not None and mag_val is not None:
                theta = np.deg2rad(angle_val)
                series_data[i]["theta"].append(theta)
                series_data[i]["radius"].append(mag_val)
            if mag_val is not None:
                mag_series_data[i].append(mag_val)
                
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

    # Define unique colors for channels 1-4.
    colors = {
        1: {"angle": "#FF0000", "mag": "#FF00FF"},  # Red and Magenta
        2: {"angle": "#00FF00", "mag": "#00FFFF"},  # Green and Cyan
        3: {"angle": "#0000FF", "mag": "#FFA500"},  # Blue and Orange
        4: {"angle": "#FFFF00", "mag": "#800080"},  # Yellow and Purple
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
                label=f"{legend_ang} {i}"
            )

    # Fixed angles for magnitude-only series.
    fixed_angles = {1: 0, 2: np.pi/2, 3: np.pi, 4: 3*np.pi/2}
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
                label=f"{legend_mag} {i}"
            )

    # Load custom font from the local fonts folder.
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "GoudyOldStyle.ttf")
    myfont = FontProperties(fname=font_path, size=10)
    ax.set_title(f"Plot For Harmonic number {harmonic} - {title_suffix}", fontproperties=myfont, fontsize=10)

    # Remove angular tick labels.
    ax.set_xticklabels([])

    # Create legend with custom font.
    legend_font = FontProperties(fname=font_path, size=7)
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1), markerscale=0.3, prop=legend_font)

    # Save the plot.
    plots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    plot_file = os.path.join(plots_dir, f"harmonic_{harmonic}_{title_suffix}_plot.png")
    fig.savefig(plot_file, bbox_inches="tight")
    plt.close(fig)
    return plot_file

def main():
    """
    Main entry point: query the database, and for each harmonic number,
    generate two plots – one for the v_prevail_* fields and one for the I_prevail_* fields.
    """
    parser = argparse.ArgumentParser(
        description="Generate polar scatter plots for each harmonic number in the DB."
    )
    args = parser.parse_args()
    setup_django()
    grouped_records = get_records_grouped_by_harmonic()
    harmonic_count = 0
    for harmonic, records in grouped_records.items():
        print(f"DEBUG: Generating plots for harmonic {harmonic} with {len(records)} records.")
        # Generate plot for v_prevail_* fields.
        plot_vprevail = create_polar_plot_for_group(
            harmonic, records, prefix="v_prevail_",
            legend_ang="Prevail Ang", legend_mag="Prevail Mag",
            title_suffix="v_prevail"
        )
        print(f"DEBUG: v_prevail plot saved to {plot_vprevail}.")
        # Generate plot for I_prevail_* fields.
        plot_Iprevail = create_polar_plot_for_group(
            harmonic, records, prefix="I_prevail_",
            legend_ang="I Prevail Ang", legend_mag="I Prevail Mag",
            title_suffix="I_prevail"
        )
        print(f"DEBUG: I_prevail plot saved to {plot_Iprevail}.")
        harmonic_count += 1
    print(f"Generated plots for {harmonic_count} harmonic numbers.")

if __name__ == "__main__":
    main()
