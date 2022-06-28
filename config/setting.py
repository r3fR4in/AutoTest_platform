import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

# 日志目录
LOG_DIR = os.path.join(BASE_DIR, "logs")
# 文件上传远程服务器信息
# host = '172.30.21.53'
# port = '22'
# username = 'Administrator'
# password = 'Abcd1234'
host = '172.30.22.33'
port = '22'
username = 'chandao'
password = 'Chandao@0756'
# 接口测试的docker镜像本地上传文件目录
updateFiles_DIR_apiTest = os.path.join(BASE_DIR, "updateFiles/apiTest")
# 接口测试的服务器文件目录
# remote_updateFiles_DIR_apiTest = 'D:/PycharmProjects/at_platform_file/apiTest'
remote_updateFiles_DIR_apiTest = '/home/chandao/autotest_platform/at_platform_file/apiTest'
# 提测申请管理的docker镜像本地上传文件目录
updateFiles_DIR_submittedTests = os.path.join(BASE_DIR, "updateFiles/submittedTests")
# 提测申请管理的服务器文件目录
# remote_updateFiles_DIR_submittedTests = 'D:/PycharmProjects/at_platform_file/submittedTests'
remote_updateFiles_DIR_submittedTests = '/home/chandao/autotest_platform/at_platform_file/submittedTests'
# redis配置
# REDIS = {
#     'HOST': '127.0.0.1',
#     'PORT': 6379,
#     'PASSWD': '',
#     'DB': 0,
#     "EXPIRE": 60000
# }
REDIS = {
    'HOST': '172.30.21.53',
    'PORT': 6379,
    'PASSWD': '',
    'DB': 0,
    "EXPIRE": 60000
}
# token
SECRET_KEY = 'shangshanbudalaohu'
EXPIRES_IN = 999999
# celery配置
broker_url = 'redis://172.30.21.53:6379/1'
result_backend = 'redis://172.30.21.53:6379/2'
worker_redirects_stdouts_level = 'INFO'
worker_redirect_stdouts = 'Disable'
