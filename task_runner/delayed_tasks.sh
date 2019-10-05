#!/usr/bin/env bash

#*/30 * * * * /home/ubuntu/teamwork/task_runner/delayed_tasks.sh

source /home/ubuntu/teamwork/twenv/bin/activate
cd /home/ubuntu/teamwork/
export DB_PASSWORD="$1"
./manage.py get_delayed_tasks