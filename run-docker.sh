#!/bin/sh
. /opt/venv/bin/activate
#. ./run.sh start #<---- can't get this to work
unset PYTHONPATH && export PYTHONPATH="${PYTHONPATH}:$PWD" && python /app/src/app.py