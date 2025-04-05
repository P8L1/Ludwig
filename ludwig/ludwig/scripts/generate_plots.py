#!/usr/bin/env python3
"""
Script: generate_plots.py
Description:
    Connects to the PostgreSQL database via Django’s ORM,
    retrieves the harmonic data, generates polar scatter plots using Gaussian KDE,
    and saves the resulting figure in the 'scripts/plots' directory.
Usage:
    Called in views never run it on its own.
"""

import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy.stats import gaussian_kde
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ludwig.settings")
django.setup()

from ludwig.models import HarmData

# Define the mapping of phase names to column suffixes.
PHASE_COLUMNS = {'Phase A': '_1', 'Phase B': '_2', 'Phase C': '_3'}

# Define output directory for plots.
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_font_properties():
    """
    Returns custom font properties loaded from the 'fonts' directory.

    Returns:
        matplotlib.font_manager.FontProperties: Font properties for plot titles.

    Raises:
        AssertionError: If the fonts directory or the font file is not found,
                        or if font properties creation fails.
    """
    fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
    assert os.path.isdir(fonts_dir), f"Fonts directory '{fonts_dir}' not found."
    font_file = os.path.join(fonts_dir, "GoudyOldStyle.ttf")
    assert os.path.exists(font_file), f"Font file '{font_file}' does not exist."
    font_props = fm.FontProperties(fname=font_file, size=9)
    assert font_props is not None, "Failed to create font properties."
    assert isinstance(font_props, fm.FontProperties), "Font properties is not a FontProperties instance."
    return font_props



def fetch_data(harm_number, night_mode, threshold_percentage):
    """
    Fetches data from the database filtered by the harmonic number and optional night mode threshold.

    Args:
        harm_number (int): The harmonic number to filter by.
        night_mode (bool): Whether to apply the night mode filter.
        threshold_percentage (float): The threshold percentage for filtering.

    Returns:
        pandas.DataFrame: The filtered data.

    Raises:
        AssertionError: If no data is found after filtering.
    """
    qs = HarmData.objects.filter(harm_number=harm_number)
    df = pd.DataFrame(list(qs.values()))
    assert df is not None, "DataFrame creation failed."
    assert not df.empty, "No data found for the specified harmonic number."

    if night_mode and threshold_percentage is not None:
        max_val = df['p_harm_total'].max()
        threshold = threshold_percentage / 100 * max_val
        df = df[df['p_harm_total'] > threshold]

    assert not df.empty and len(df) >= 2, "Insufficient data after filtering."
    return df


def generate_and_save_plots(df, phase, harm_number):
    """
    Generates polar scatter plots for current and voltage data and saves the figure.

    Args:
        df (pandas.DataFrame): The data for plotting.
        phase (str): The phase to use (e.g., 'Phase A', 'Phase B', 'Phase C').
        harm_number (int): The harmonic number used (for title labeling).
    """
    suffix = PHASE_COLUMNS.get(phase)
    assert suffix is not None, f"Invalid phase provided: {phase}"

    # Construct column names matching the model fields.
    i_mag_col = f'i_prevail_mag{suffix}'
    v_mag_col = f'v_prevail_mag{suffix}'
    i_ang_col = f'i_prevail_ang{suffix}'
    v_ang_col = f'v_prevail_ang{suffix}'

    # Verify that required columns exist in the DataFrame.
    for col in [i_mag_col, v_mag_col, i_ang_col, v_ang_col]:
        assert col in df.columns, f"Required column '{col}' not found in the data."

    # Clean data.
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(subset=[i_mag_col, v_mag_col, i_ang_col, v_ang_col], inplace=True)
    assert not df.empty, "Dataframe is empty after cleaning NaN and infinite values."

    # Create a figure with two polar subplots.
    fig, (ax1, ax2) = plt.subplots(1, 2, subplot_kw={'projection': 'polar'}, figsize=(10, 5))
    axes_info = [
        (ax1, i_mag_col, i_ang_col, "Current"),
        (ax2, v_mag_col, v_ang_col, "Voltage")
    ]

    # Generate plots.
    for ax, mag_col, ang_col, label in axes_info:
        r = df[mag_col]
        theta = df[ang_col] * np.pi / 180  # Convert degrees to radians.
        xy = np.vstack([theta, r])
        z = gaussian_kde(xy)(xy)
        idx = z.argsort()
        theta, r, z = theta[idx], r[idx], z[idx]
        ax.clear()
        ax.set_xticklabels([]) 
        ax.scatter(theta, r, c=z, s=20, cmap="inferno", alpha=0.75)
        ax.set_title(f"{label} Density Plot, {phase}", fontproperties=get_font_properties())
        assert ax.get_title() != "", f"Title not set for axis plotting {label}."

    # Save the figure.
    output_filename = f"polar_scatter_{phase.replace(' ', '_')}_{harm_number}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.tight_layout()
    plt.savefig(output_path)
