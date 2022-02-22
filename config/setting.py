import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

# 日志目录
LOG_DIR = os.path.join(BASE_DIR, "logs")
# 接口测试的上传文件目录
updateFiles_DIR_apiTest = os.path.join(BASE_DIR, "updateFiles/apiTest")
# 提测申请管理的上传文件目录
updateFiles_DIR_submittedTests = os.path.join(BASE_DIR, "updateFiles/submittedTests")
# redis配置
REDIS = {
    'HOST': '127.0.0.1',
    'PORT': 6379,
    'PASSWD': '',
    'DB': 0,
    "EXPIRE": 60000
}
# token
SECRET_KEY = 'shangshanbudalaohu'
EXPIRES_IN = 999999
