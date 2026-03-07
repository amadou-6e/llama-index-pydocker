#!/bin/bash
set -e

DB_NAME="${POSTGRES_DB:-vectordb}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
SELECT format('CREATE DATABASE %I', '${DB_NAME}')
WHERE NOT EXISTS (
  SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'
)\gexec
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" <<-EOSQL
CREATE EXTENSION IF NOT EXISTS vector;
EOSQL
