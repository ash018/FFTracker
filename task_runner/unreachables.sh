#!/usr/bin/env bash

### Convert sh file to executable
#echo $PWD
#sudo nano /etc/nginx/sites-available/dgfi.nginx
#sudo ln -s /etc/nginx/sites-available/dgfi.nginx /etc/nginx/sites-enabled

#*/15 * * * * /home/ubuntu/teamwork/task_runner/unreachables.sh

source /home/ubuntu/teamwork/twenv/bin/activate
cd /home/ubuntu/teamwork/
export DB_PASSWORD="$1"
./manage.py get_unreachables
