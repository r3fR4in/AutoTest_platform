# dockerhub仓库：r3fr41n/autotest_platform
# 1.打包镜像
# docker build -t autotest_platform:1.0.0 .
# 2.导出镜像
# docker save -o autotest_platform_1.1.6.tar autotest_platform:1.1.6
# 4.把文件传到服务器上
# sudo rz -y
# 5.把镜像导入至服务器docker上
# docker load < autotest_platform_1.1.6.tar
# 6.启动镜像
# docker run -p 5000:5000 -d --name autotest_platform autotest_platform:1.1.6

FROM python:3.7.5-slim-stretch
#FROM python:3.7.5-windowsservercore-1809
WORKDIR /AutoTest_platform

COPY requirements.txt ./

RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update && apt-get install -y tzdata
ENV TZ=Asia/Shanghai
#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN echo $TZ > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

RUN pip install --upgrade pip==22.0.3 -i https://pypi.tuna.tsinghua.edu.cn/simple\
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 端口
EXPOSE 5000

COPY . .

ENTRYPOINT ["./entrypoint.sh"]
