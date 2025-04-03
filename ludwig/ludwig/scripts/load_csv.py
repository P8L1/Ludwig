#!/usr/bin/env python3
"""
Script: load_csv.py
Description:
    Loads selected columns from a CSV file into the PostgreSQL database via Django’s ORM.
    Only the columns necessary for plotting are imported.
Usage:
    python load_csv.py --csv_path /path/to/your/file.csv
"""

import os
import sys
import argparse
import pandas as pd
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ludwig.settings")
django.setup()

from ludwig.models import HarmData  # noqa: E402

# Define the required CSV columns for plotting.
REQUIRED_COLUMNS = [
    'HARM_NUMBER',
    'P_HARM_TOTAL',
    'I_PREVAIL_MAG_1', 'I_PREVAIL_ANG_1', 'V_PREVAIL_MAG_1', 'V_PREVAIL_ANG_1',
    'I_PREVAIL_MAG_2', 'I_PREVAIL_ANG_2', 'V_PREVAIL_MAG_2', 'V_PREVAIL_ANG_2',
    'I_PREVAIL_MAG_3', 'I_PREVAIL_ANG_3', 'V_PREVAIL_MAG_3', 'V_PREVAIL_ANG_3'
]


def load_csv_to_db(csv_path):
    """
    Loads the CSV file into the database.
    
    Args:
        csv_path (str): The full path to the CSV file.
    
    Raises:
        AssertionError: If required columns are missing.
    """
    # Read CSV file into a DataFrame.
    df = pd.read_csv(csv_path)
    assert not df.empty, "CSV file is empty."
    
    # Validate that all required columns are present.
    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Missing required column: {col}"
    
    # Subset DataFrame to necessary columns.
    df = df[REQUIRED_COLUMNS]
    records = []
    
    # Convert DataFrame rows to HarmData objects.
    for index, row in df.iterrows():
        record = HarmData(
            harm_number=int(row['HARM_NUMBER']),
            p_harm_total=float(row['P_HARM_TOTAL']),
            i_prevail_mag_1=float(row['I_PREVAIL_MAG_1']),
            i_prevail_ang_1=float(row['I_PREVAIL_ANG_1']),
            v_prevail_mag_1=float(row['V_PREVAIL_MAG_1']),
            v_prevail_ang_1=float(row['V_PREVAIL_ANG_1']),
            i_prevail_mag_2=float(row['I_PREVAIL_MAG_2']),
            i_prevail_ang_2=float(row['I_PREVAIL_ANG_2']),
            v_prevail_mag_2=float(row['V_PREVAIL_MAG_2']),
            v_prevail_ang_2=float(row['V_PREVAIL_ANG_2']),
            i_prevail_mag_3=float(row['I_PREVAIL_MAG_3']),
            i_prevail_ang_3=float(row['I_PREVAIL_ANG_3']),
            v_prevail_mag_3=float(row['V_PREVAIL_MAG_3']),
            v_prevail_ang_3=float(row['V_PREVAIL_ANG_3'])
        )
        records.append(record)
    
    # Bulk create records.
    created = HarmData.objects.bulk_create(records)
    assert len(created) == len(records), "Not all records were inserted."
    print(f"Successfully loaded {len(created)} records into the database.")


def main():
    """Parse arguments and load the CSV data into the DB."""
    parser = argparse.ArgumentParser(
        description="Load CSV file data into the database."
    )
    parser.add_argument(
        "--csv_path",
        required=True,
        help="The path to the CSV file containing the harmonic data."
    )
    args = parser.parse_args()
    load_csv_to_db(args.csv_path)


if __name__ == "__main__":
    main()
