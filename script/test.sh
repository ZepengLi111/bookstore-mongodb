#!/bin/sh
export PATHONPATH=`pwd`
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest -v --ignore=fe/data,be/app.py,be/auto_cancel.py
coverage combine
coverage report
coverage html
