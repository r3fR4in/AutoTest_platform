import mimetypes
import os

import requests
import ast
from config import setting
from utils import sshConnect
from utils import log
from utils import time


class SendRequests():
    """发送请求数据"""

    def __init__(self, method, url, header, body, files, encode,  verify, log):
        self.method = method
        self.url = url
        self.header = header
        self.body = body
        self.files = files
        self.encode = encode
        self.verify = verify
        self.log = log

    def request(self):
        """发送请求"""
        global re
        try:
            if self.files:
                # filepath = os.path.join(setting.remote_updateFiles_DIR_apiTest, self.files[0]['realname'])
                # filepath = setting.remote_updateFiles_DIR_apiTest + '/' + self.files[0]['realname']
                # file = open(filepath, 'rb')
                ssh = sshConnect.SSH(setting.host, setting.port, setting.username, setting.password)
                file = ssh.open_file(setting.updateFiles_DIR_apiTest, setting.remote_updateFiles_DIR_apiTest, self.files[0]['realname'])
                if self.header == '':
                    self.header = {}
                # self.header["Content-Type"] = mimetypes.guess_type(filepath)[0]
                # re = requests.request(self.method, self.url, headers=self.header, data=file, verify=self.verify)
                files = {'file': file}
                re = requests.request(self.method, self.url, headers=self.header, files=files, verify=self.verify)
                ssh.close_connect()
                file.close()
            elif self.method == 'GET' or self.method == 'get':
                if self.body != '':
                    self.body = ast.literal_eval(str(self.body))
                re = requests.request(self.method, self.url, headers=self.header, params=self.body, verify=self.verify)
            # elif self.method == 'POST' or self.method == 'post':
            else:
                # 判斷content type
                if "application/x-www-form-urlencoded" in str(self.header):  # application/x-www-form-urlencoded需要處理一下body的數據格式才能發送請求
                    body = ast.literal_eval(self.body)
                    re = requests.request(self.method, self.url, headers=self.header, data=body, verify=self.verify)
                else:
                    re = requests.request(self.method, self.url, headers=self.header, data=self.body.encode(self.encode), verify=self.verify)
            return re
        except Exception as e:
            self.log.error(e)
            return e

