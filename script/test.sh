#!/bin/sh
export PATHONPATH=`pwd`
coverage run --timid --branch --source fe,be --concurrency=thread --omit=be/app.py,be/auto_cancel.py -m pytest -v --ignore=fe/data
coverage combine
coverage report
coverage html
