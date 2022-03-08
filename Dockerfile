FROM python:3.7.5-slim-stretch
WORKDIR /AutoTest_platform

COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 端口
EXPOSE 5001

# CMD ["gunicorn", "start:app", "-c", "./gunicorn.conf.py"]
# CMD ["python", "./app.py"]
# CMD ["celery", "-A", "app:celery", "worker", "-l", "INFO", "-P", "threads"]

CMD nohup python ./app.py && celery -A app:celery worker -l INFO -P threads