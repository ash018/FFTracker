#!/usr/bin/env bash

kill -9 `cat $PWD"/prod/gunicorn.pid"`