#!/bin/bash

set -e  # Exit on error

# Check for psql
if ! command -v psql >/dev/null 2>&1; then
    echo "Error: psql command not found. Install PostgreSQL first."
    exit 1
fi

# Prompt for user
echo "This script will create the 'ludwig' DB and user with superuser privileges."
read -p "Enter PostgreSQL username [default: postgres]: " PGUSER
PGUSER=${PGUSER:-postgres}

# Run SQL commands
psql -U "$PGUSER" <<EOF
CREATE DATABASE ludwig;
CREATE USER ludwig WITH PASSWORD 'ludwig';
GRANT ALL PRIVILEGES ON DATABASE ludwig TO ludwig;
ALTER ROLE ludwig WITH SUPERUSER;
EOF

echo "✅ 'ludwig' database and superuser created successfully."
