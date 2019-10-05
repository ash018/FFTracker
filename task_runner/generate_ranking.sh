#!/usr/bin/env bash

#20 17 * * * /home/ubuntu/teamwork/task_runner/generate_ranking.sh

source /home/ubuntu/teamwork/twenv/bin/activate
cd /home/ubuntu/teamwork/
export DB_PASSWORD="$1"
./manage.py generate_ranking