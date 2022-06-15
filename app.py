import os

from flask import render_template, send_from_directory
from werkzeug.exceptions import HTTPException

from __init__ import create_app
from utils.extensions import db, celery
from utils.errorHandler import APIException
from utils import errorCode
from utils.log import Log
import traceback

app = create_app()
db.init_app(app)
# 创建表用的
# with app.app_context():
#     db.create_all()
celery.init_app(app)

# 全局异常捕捉
@app.errorhandler(Exception)
def framework_error(e):
    log = Log('log')
    # 判断异常是不是APIException
    if isinstance(e, APIException):
        return e
    # 判断异常是不是HTTPException
    if isinstance(e, HTTPException):
        log.error(e)
        code = e.code
        # 获取具体的响应错误信息
        msg = e.description
        error_code = 1007
        return APIException(code=code, msg=msg, error_code=error_code)
    # 异常肯定是Exception
    else:
        log.error(traceback.format_exc())
        return errorCode.ServerError()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    # app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
