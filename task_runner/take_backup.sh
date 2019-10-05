#!/usr/bin/env bash

source /home/ubuntu/teamwork/twenv/bin/activate
cd /home/ubuntu/teamwork/
export PGPASSWORD="$1"
./db_ops/take_backup.sh teamwork_dh