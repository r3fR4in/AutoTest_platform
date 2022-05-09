from flask import request
from werkzeug.exceptions import HTTPException
import json

class APIException(HTTPException):
    """
    继承HTTPException
    1.重写get_body用于返回特定body信息
    2.重写get_headers用于指定返回类型
    """
    code = 500
    msg = "系统错误"
    error_code = 9999

    def __init__(self, msg=None, code=None, error_code=None, error=None):
        if code:
            self.code = code
        if msg:
            self.msg = msg
        if error_code:
            self.error_code = error_code
        self.success = False
        super().__init__(msg, None)

    def get_body(self, environ=None):
        body = dict(
            error_code=self.error_code,
            msg=self.msg,
            request=request.method + ' ' + self.get_url_no_parm(),
            success=self.success
        )
        text = json.dumps(body, sort_keys=False, ensure_ascii=False)
        return text

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_parm():
        full_path = str(request.path)
        return full_path
