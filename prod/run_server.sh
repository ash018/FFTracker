#!/usr/bin/env bash

conf=$PWD"/prod/gnconf.ini.py"
wsgi="conf.wsgi"

gunicorn -c $conf $wsgi
sudo service nginx restart