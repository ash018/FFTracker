#!/usr/bin/env bash

db_name="$1"
if [ ${#db_name} -le 3 ]; then echo "DB name not provided!" ; exit
fi
echo "Deleting old data from "$1" ........."
psql -U postgres -h 127.0.0.1 -d "$1" -c 'DROP SCHEMA public CASCADE;'
psql -U postgres -h 127.0.0.1 -d "$1" -c 'CREATE SCHEMA public;'
psql -U postgres -h 127.0.0.1 -d "$1" -c 'GRANT ALL ON SCHEMA public TO postgres;'
psql -U postgres -h 127.0.0.1 -d "$1" -c 'GRANT ALL ON SCHEMA public TO public'
echo "Uploading initial data to "$1"........."
pg_restore -U postgres -h 127.0.0.1 -d "$1" -1 db_ops/seed_data.sql
echo "Finished"