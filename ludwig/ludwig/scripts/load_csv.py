#!/usr/bin/env python3
"""
Script: import_csv.py
Description:
    Loads selected columns from a tab-separated file (located in the scripts/datasets folder)
    into the PostgreSQL database via Django’s ORM.
    Only rows where the HARM_NUMBER field can be converted to an int are inserted.
Usage:
    python import_csv.py your_file.csv
"""

import os
import sys
import argparse
from decimal import Decimal

import django
from django.db import connection

# Make sure Django can locate the settings.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ludwig.settings")
django.setup()

from ludwig.models import HarmData 

# Define the required CSV columns for plotting.
REQUIRED_COLUMNS = [
    'HARM_NUMBER',
    'P_HARM_TOTAL',
    'I_PREVAIL_MAG_1', 'I_PREVAIL_ANG_1', 'V_PREVAIL_MAG_1', 'V_PREVAIL_ANG_1',
    'I_PREVAIL_MAG_2', 'I_PREVAIL_ANG_2', 'V_PREVAIL_MAG_2', 'V_PREVAIL_ANG_2',
    'I_PREVAIL_MAG_3', 'I_PREVAIL_ANG_3', 'V_PREVAIL_MAG_3', 'V_PREVAIL_ANG_3'
]


def list_db_tables():
    """
    List all tables in the current database.
    
    Returns:
        list: A list of table names.
    """
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names(cursor)
    return tables


def load_csv_to_db(csv_path):
    """
    Loads the CSV file into the database.
    
    Args:
        csv_path (str): The full path to the CSV file.
    
    Raises:
        AssertionError: If required columns are missing, if CSV cannot be read,
                        or if the expected database table is missing.
    """
    # Open the file as plain text.
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            # Read header and split by tab.
            header_line = f.readline().strip()
            if not header_line:
                raise AssertionError("CSV file is empty or missing a header.")
            header_fields = header_line.split("\t")
    except Exception as e:
        raise AssertionError(f"Failed to read CSV header at {csv_path}: {e}")
    
    # Ensure all required columns are present.
    available_columns = header_fields
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in available_columns]
    assert not missing_columns, (
        f"Missing required columns: {missing_columns}. "
        f"Available columns: {available_columns}"
    )
    
    records = []
    line_num = 1  # header is line 1
    # Process each subsequent line.
    with open(csv_path, "r", encoding="utf-8") as f:
        # Skip header
        next(f)
        for line in f:
            line_num += 1
            line = line.strip()
            if not line:
                continue  # skip empty lines
            parts = line.split("\t")
            # If number of parts doesn't match header, skip this line.
            if len(parts) != len(header_fields):
                print(f"Warning: Line {line_num} has {len(parts)} fields; expected {len(header_fields)}. Skipping.")
                continue
            row_dict = dict(zip(header_fields, parts))
            # Try converting HARM_NUMBER to int; if it fails, skip this row.
            try:
                harm_number = int(row_dict['HARM_NUMBER'])
            except Exception:
                print(f"Warning: Line {line_num} HARM_NUMBER '{row_dict['HARM_NUMBER']}' is not an integer. Skipping.")
                continue

            # Attempt to convert required fields.
            try:
                p_harm_total = float(row_dict['P_HARM_TOTAL'])
                i_prevail_mag_1 = float(row_dict['I_PREVAIL_MAG_1'])
                i_prevail_ang_1 = float(row_dict['I_PREVAIL_ANG_1'])
                v_prevail_mag_1 = float(row_dict['V_PREVAIL_MAG_1'])
                v_prevail_ang_1 = float(row_dict['V_PREVAIL_ANG_1'])
                i_prevail_mag_2 = float(row_dict['I_PREVAIL_MAG_2'])
                i_prevail_ang_2 = float(row_dict['I_PREVAIL_ANG_2'])
                v_prevail_mag_2 = float(row_dict['V_PREVAIL_MAG_2'])
                v_prevail_ang_2 = float(row_dict['V_PREVAIL_ANG_2'])
                i_prevail_mag_3 = float(row_dict['I_PREVAIL_MAG_3'])
                i_prevail_ang_3 = float(row_dict['I_PREVAIL_ANG_3'])
                v_prevail_mag_3 = float(row_dict['V_PREVAIL_MAG_3'])
                v_prevail_ang_3 = float(row_dict['V_PREVAIL_ANG_3'])
            except Exception as e:
                print(f"Warning: Line {line_num} conversion error: {e}. Skipping.")
                continue

            try:
                record = HarmData(
                    harm_number=harm_number,
                    p_harm_total=p_harm_total,
                    i_prevail_mag_1=i_prevail_mag_1,
                    i_prevail_ang_1=i_prevail_ang_1,
                    v_prevail_mag_1=v_prevail_mag_1,
                    v_prevail_ang_1=v_prevail_ang_1,
                    i_prevail_mag_2=i_prevail_mag_2,
                    i_prevail_ang_2=i_prevail_ang_2,
                    v_prevail_mag_2=v_prevail_mag_2,
                    v_prevail_ang_2=v_prevail_ang_2,
                    i_prevail_mag_3=i_prevail_mag_3,
                    i_prevail_ang_3=i_prevail_ang_3,
                    v_prevail_mag_3=v_prevail_mag_3,
                    v_prevail_ang_3=v_prevail_ang_3
                )
            except Exception as e:
                print(f"Warning: Line {line_num} failed to create HarmData object: {e}. Skipping.")
                continue
            records.append(record)
    
    # Verify that the expected database table exists.
    expected_table = HarmData._meta.db_table
    tables = list_db_tables()
    assert expected_table in tables, (
        f"Expected table '{expected_table}' not found in the database. "
        f"Available tables: {tables}"
    )

    # Bulk create records.
    try:
        created = HarmData.objects.bulk_create(records)
    except Exception as e:
        raise AssertionError(f"Bulk creation of records failed: {e}")
    
    assert len(created) == len(records), (
        f"Not all records were inserted. Expected {len(records)} but inserted {len(created)}."
    )
    print(f"Successfully loaded {len(created)} records into the database.")


def main():
    """Parse arguments and load the CSV data into the DB."""
    parser = argparse.ArgumentParser(
        description="Load tab-separated CSV file data into the database."
    )
    parser.add_argument(
        "csv_file",
        help="The name of the CSV file (located in the scripts/datasets folder)."
    )
    args = parser.parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "datasets", args.csv_file)
    assert os.path.exists(csv_path), f"CSV file not found at {csv_path}"
    load_csv_to_db(csv_path)


if __name__ == "__main__":
    main()
