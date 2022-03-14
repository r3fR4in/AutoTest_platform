#!/bin/bash
nohup celery -A app:celery worker -l INFO -P threads > celery.log 2>&1 &
python app.py > app.log 2>&1
