#!/bin/sh
arg=$1

case $arg in
    "dep-uninstall")
        pip freeze | xargs pip uninstall -y;;
    "dep-install")
        pip install -r requirements.txt && pip install -r dev-requirements.txt;;
    "dep-outdated")
        pip list --outdated;;
    "dep-conflict")
        pipconflictchecker;;
    "test")
        pytest;;
    "start")
        unset PYTHONPATH && export PYTHONPATH="${PYTHONPATH}:$PWD" && python src/app.py;;
    "coverage")
        pytest --junitxml=junit/test-results.xml --cov=src --cov-report=xml --cov-report=html;;
    "lint")
        pylint -d R,C src;;
    "check")
        pylint -E src;;
    "type")
        mypy src;;
    "snyk")
        snyk test;;
    *) ;;
esac
