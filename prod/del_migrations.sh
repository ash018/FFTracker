#!/usr/bin/env bash

find ./apps/ -path "*/migrations/*.py" -not -name "__init__.py" -delete
find ./apps/ -path "*/migrations/*.pyc"  -delete

# git force add migrations
# git add --force --all */migrations/*.py