# 1.先将容器的文件夹拷贝至本地
# docker cp autotest_platform:/AutoTest_platform/logs D:\PycharmProjects
# docker cp autotest_platform:/AutoTest_platform/updateFiles D:\PycharmProjects
# 2.打包镜像
# docker build -t autotest_platform:1.0.0 .
# 3.启动镜像后，把拷出来的文件放到容器中
# docker cp D:\PycharmProjects\logs autotest_platform:/AutoTest_platform/
# docker cp D:\PycharmProjects\updateFiles autotest_platform:/AutoTest_platform/

FROM python:3.7.5-slim-stretch
#FROM python:3.7.5-windowsservercore-1809
WORKDIR /AutoTest_platform

COPY requirements.txt ./

RUN pip install --upgrade pip==22.0.3 -i https://pypi.tuna.tsinghua.edu.cn/simple\
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
#    && apt-get update\
#    && apt-get install -y dos2unix\
#    && dos2unix entrypoint.sh
#RUN python -m pip install --upgrade pip==22.0.3 -i https://pypi.tuna.tsinghua.edu.cn/simple\
#    && python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 端口
EXPOSE 5000

COPY . .
# CMD ["gunicorn", "start:app", "-c", "./gunicorn.conf.py"]
# CMD ["python", "./app.py"]
# CMD ["celery", "-A", "app:celery", "worker", "-l", "INFO", "-P", "threads"]

#CMD python app.py
#CMD nohup python app.py > app.log 2>&1 & && nohup celery -A app:celery worker -l INFO -P threads > celery.log 2>&1 &
#CMD nohup python app.py > app.log 2>&1 & ; nohup celery -A app:celery worker -l INFO -P threads > celery.log 2>&1 &
ENTRYPOINT ["./entrypoint.sh"]