#!/usr/bin/env bash

#10 17 * * * /home/ubuntu/teamwork/task_runner/generate_attendance.sh pgpass

source /home/ubuntu/teamwork/twenv/bin/activate
cd /home/ubuntu/teamwork/
export DB_PASSWORD="$1"
./manage.py generate_attendance_report