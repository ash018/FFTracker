#!/usr/bin/env bash

source /home/ubuntu/teamwork/twenv/bin/activate
cd /home/ubuntu/teamwork/
export DB_PASSWORD="$1"
./manage.py process_tasks --duration 1620