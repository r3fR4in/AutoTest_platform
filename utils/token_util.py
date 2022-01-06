from config import setting
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from utils.log import Log
import functools
from flask import request, jsonify

def create_token(user_id, user_name, role_list):
    """生成token"""
    # 第一个参数是内部的私钥，这里写在共用的配置信息里了，如果只是测试可以写死
    # 第二个参数是有效期(秒)
    s = Serializer(setting.SECRET_KEY, expires_in=setting.EXPIRES_IN)
    # 接收用户id转换与编码
    token = None
    try:
        token = s.dumps({"id": user_id, "name": user_name, "role": role_list}).decode("ascii")
    except Exception as e:
        log = Log('log')
        log.error("获取token失败:{}".format(e))
    return token

def verify_token(token):
    """校驗token"""
    # 参数为私有秘钥，跟上面方法的秘钥保持一致
    s = Serializer(setting.SECRET_KEY)
    try:
        # 转换为字典
        data = s.loads(token)
        return data
    except Exception as e:
        log = Log('log')
        log.error(f"token转换失败:{e}")
        return None

def login_required(*role):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                # 在请求头上拿到token
                token = request.headers["Authorization"]
            except Exception as e:
                # 没接收的到token,给前端抛出错误
                return jsonify(code=401, msg='缺少参数token')
            s = Serializer(setting.SECRET_KEY)
            try:
                user = s.loads(token)
                if role:
                    # 获取token中的权限列表如果在参数列表中则表示有权限，否则就表示没有权限
                    user_role = user['role']
                    # result = [x for x in user_role if x in list(role)]
                    # if not result:
                    #     return jsonify(code=1, msg="权限不够")
                    if user_role not in list(role):
                        return jsonify(code=401, msg="权限不够")
            except Exception as e:
                return jsonify(code=401, msg="登录已过期")
            return func(*args, **kw)
        return wrapper
    return decorator
