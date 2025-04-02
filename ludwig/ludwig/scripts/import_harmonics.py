#!/usr/bin/env python
import os
import sys
import argparse
import django

# Maximum number of rows to process (fixed upper bound for all loops)
MAX_ROWS = 100000


def setup_django():
    """
    Setup the Django environment.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ludwig.settings')

    django.setup()
    from django.conf import settings  # noqa: F401
    assert os.environ.get('DJANGO_SETTINGS_MODULE') is not None, "DJANGO_SETTINGS_MODULE must be defined"


def read_csv(csv_path, max_rows=MAX_ROWS):
    """
    Manually read a tab-delimited file where each line may be surrounded by quotes.
    Only rows with a valid integer HARM_NUMBER are converted to records.
    """
    assert csv_path, "csv_path must be provided"
    valid_records = []
    with open(csv_path, encoding='utf-8-sig') as f:
        lines = f.read().splitlines()

    if not lines:
        raise AssertionError("CSV file is empty.")

    # Process header: remove surrounding quotes if present, then split on tab.
    header_line = lines[0].strip()
    if header_line.startswith('"') and header_line.endswith('"'):
        header_line = header_line[1:-1]
    headers = header_line.split("\t")
    print(f"DEBUG: Found headers: {headers}")

    required_headers = {
        'ROW_ID',
        'HARM_NUMBER',
        'V_PREVAIL_ANG_1',
        'V_PREVAIL_ANG_2',
        'V_PREVAIL_ANG_3',
        'V_PREVAIL_ANG_4',
        'V_PREVAIL_MAG_1',
        'V_PREVAIL_MAG_2',
        'V_PREVAIL_MAG_3',
        'V_PREVAIL_MAG_4',
        'I_PREVAIL_ANG_1',
        'I_PREVAIL_ANG_2',
        'I_PREVAIL_ANG_3',
        'I_PREVAIL_ANG_4',
        'I_PREVAIL_MAG_1',
        'I_PREVAIL_MAG_2',
        'I_PREVAIL_MAG_3',
        'I_PREVAIL_MAG_4',
    }
    found_headers = set(headers)
    if not required_headers.issubset(found_headers):
        missing = required_headers - found_headers
        raise AssertionError(
            f"CSV header missing required columns. Found columns: {found_headers}. Missing: {missing}"
        )

    total_lines = len(lines) - 1
    print(f"DEBUG: Total data lines: {total_lines}")

    rows_processed = 0
    for idx, line in enumerate(lines[1:]):
        if rows_processed >= max_rows:
            break
        line = line.strip()
        if not line:
            continue
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        fields = line.split("\t")
        if len(fields) != len(headers):
            print(f"DEBUG: Line {idx+1} has {len(fields)} fields; expected {len(headers)}. Skipping.")
            continue
        row = dict(zip(headers, fields))
        if idx < 5:
            print(f"DEBUG: Row {idx+1} parsed: {row}")

        harmonic_field = row.get('HARM_NUMBER')
        if harmonic_field is None or not harmonic_field.strip():
            print(f"DEBUG: Row {idx+1} skipped due to missing HARM_NUMBER.")
            continue
        try:
            harmonic_val = float(harmonic_field.strip())
        except ValueError:
            print(f"DEBUG: Row {idx+1} invalid HARM_NUMBER: {harmonic_field}.")
            continue

        if not harmonic_val.is_integer():
            print(f"DEBUG: Row {idx+1} skipped: HARM_NUMBER {harmonic_val} is not an integer.")
            continue

        row_id_field = row.get('ROW_ID')
        if row_id_field is None or not row_id_field.strip():
            print(f"DEBUG: Row {idx+1} skipped due to missing ROW_ID.")
            continue
        try:
            row_id_val = int(row_id_field.strip())
        except ValueError:
            print(f"DEBUG: Row {idx+1} invalid ROW_ID: {row_id_field}.")
            continue

        def safe_float(field_name):
            value = row.get(field_name)
            if value is None or not value.strip():
                return None
            try:
                return float(value.strip())
            except ValueError:
                return None

        record = {
            'row_id': row_id_val,  # For debugging purposes.
            'harmonic_number': int(harmonic_val),
            'v_prevail_ang1': safe_float('V_PREVAIL_ANG_1'),
            'v_prevail_ang2': safe_float('V_PREVAIL_ANG_2'),
            'v_prevail_ang3': safe_float('V_PREVAIL_ANG_3'),
            'v_prevail_ang4': safe_float('V_PREVAIL_ANG_4'),
            'v_prevail_mag1': safe_float('V_PREVAIL_MAG_1'),
            'v_prevail_mag2': safe_float('V_PREVAIL_MAG_2'),
            'v_prevail_mag3': safe_float('V_PREVAIL_MAG_3'),
            'v_prevail_mag4': safe_float('V_PREVAIL_MAG_4'),
            'I_prevail_ang1': safe_float('I_PREVAIL_ANG_1'),
            'I_prevail_ang2': safe_float('I_PREVAIL_ANG_2'),
            'I_prevail_ang3': safe_float('I_PREVAIL_ANG_3'),
            'I_prevail_ang4': safe_float('I_PREVAIL_ANG_4'),
            'I_prevail_mag1': safe_float('I_PREVAIL_MAG_1'),
            'I_prevail_mag2': safe_float('I_PREVAIL_MAG_2'),
            'I_prevail_mag3': safe_float('I_PREVAIL_MAG_3'),
            'I_prevail_mag4': safe_float('I_PREVAIL_MAG_4'),
        }
        if idx < 5:
            print(f"DEBUG: Row {idx+1} accepted as record: {record}")
        valid_records.append(record)
        rows_processed += 1

    print(f"DEBUG: Total lines processed: {rows_processed}. Valid records found: {len(valid_records)}")
    return valid_records


def import_records(records):
    """
    Insert records into the database using Django ORM.
    Note: The row_id field is omitted since the model doesn't include it.
    """
    from ludwig.models import HarmonicRecord

    inserted_count = 0
    for rec in records:
        # Create the model instance without the row_id field.
        instance = HarmonicRecord(
            harmonic_number=rec['harmonic_number'],
            v_prevail_ang1=rec['v_prevail_ang1'],
            v_prevail_ang2=rec['v_prevail_ang2'],
            v_prevail_ang3=rec['v_prevail_ang3'],
            v_prevail_ang4=rec['v_prevail_ang4'],
            v_prevail_mag1=rec['v_prevail_mag1'],
            v_prevail_mag2=rec['v_prevail_mag2'],
            v_prevail_mag3=rec['v_prevail_mag3'],
            v_prevail_mag4=rec['v_prevail_mag4'],
            I_prevail_ang1=rec['I_prevail_ang1'],
            I_prevail_ang2=rec['I_prevail_ang2'],
            I_prevail_ang3=rec['I_prevail_ang3'],
            I_prevail_ang4=rec['I_prevail_ang4'],
            I_prevail_mag1=rec['I_prevail_mag1'],
            I_prevail_mag2=rec['I_prevail_mag2'],
            I_prevail_mag3=rec['I_prevail_mag3'],
            I_prevail_mag4=rec['I_prevail_mag4'],
        )
        instance.save()
        inserted_count += 1

    print(f"DEBUG: Total records inserted: {inserted_count}")
    return inserted_count


def main():
    """
    Main entry point for the import script.
    """
    parser = argparse.ArgumentParser(
        description="Import harmonic CSV data into a PostgreSQL database using Django ORM."
    )
    parser.add_argument('--csv', required=True, help='Path to CSV file with harmonic data')
    args = parser.parse_args()

    csv_path = args.csv
    assert os.path.exists(csv_path), f"CSV file does not exist: {csv_path}"

    setup_django()
    records = read_csv(csv_path)
    inserted = import_records(records)
    print(f"Inserted {inserted} records.")


if __name__ == '__main__':
    main()
