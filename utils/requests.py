import requests
from utils import log
from utils import time


class SendRequests():
    """发送请求数据"""

    def __init__(self, method, url, log):
        self.method = method
        self.url = url
        self.log = log

    def request(self, **kwargs):
        """发送请求"""
        try:
            url = self.url
            dic = {}
            for key in kwargs:
                if kwargs != '':
                    dic[key] = kwargs[key]
            re = requests.request(self.method, url, **dic)
            return re
        except Exception as e:
            self.log.error(e)

