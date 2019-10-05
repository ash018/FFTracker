#!/usr/bin/env bash

#0 10-17/2 * * * /home/ubuntu/teamwork/task_runner/send_offline.sh

source /home/ubuntu/teamwork/twenv/bin/activate
cd /home/ubuntu/teamwork/
export DB_PASSWORD="$1"
./manage.py send_offline