#!/usr/bin/env bash

db_name="$1"
if [ ${#db_name} -le 3 ]; then echo "DB name not provided!" ; exit
fi
echo "Deleting data from "$1" ........."
psql -U postgres -h 127.0.0.1 -d "$1" -c 'DELETE FROM location_location;'
echo "Finished"