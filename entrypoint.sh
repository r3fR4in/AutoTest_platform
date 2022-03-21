#!/bin/bash
nohup celery -A app:celery worker -l INFO -P threads > celery.log 2>&1 &
gunicorn app:app -c gunicorn.conf.py