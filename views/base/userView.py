import ast

from flask import Blueprint, jsonify, request
from utils.extensions import db
from models.base.userModel import User
from models.base.dataDictionaryModel import dataDictionary
from utils import token_util, redis_util

user = Blueprint('user', __name__)

"""登錄"""
@user.route('/login', methods=["POST"])
def login():
    # 从post请求拿参数
    param_username = request.form.get('username')
    param_password = request.form.get('password')
    # 校驗用戶名密碼是否爲空
    if not all([param_username, param_password]):
        output = {'code': 0, 'msg': '用戶名和密碼不能爲空'}
        return jsonify(output)
    # 根據用戶名獲取用戶信息
    try:
        user = User.query.filter(User.username == param_username).first()
    except Exception as e:
        output = {'code': 0, 'msg': '獲取用戶信息失敗', 'exception': e}
        return jsonify(output)
    # 校驗用戶名密碼
    if user is None or user.password != param_password:
        output = {'code': 0, 'msg': '用戶名或密碼錯誤'}
        return jsonify(output)
    # 校驗用戶狀態
    if user.status == 2:
        output = {'code': 0, 'msg': '用戶名已被禁用'}
        return jsonify(output)

    token = token_util.create_token(user.id, user.username, user.role)
    data = {'token': token, 'nickname': user.nickname}
    try:
        redis = redis_util.Redis
        redis.write(f"token_{user.username}", token)
    except Exception as e:
        output = {'code': 0, 'msg': '登錄失敗', 'exception': e}
        return jsonify(output)

    if token:
        output = {'code': 0, 'msg': '登錄成功', 'data': data, 'success': True}
        return jsonify(output)
    else:
        output = {'code': 0, 'msg': '請求失敗', 'data': token}
        return jsonify(output)


"""注銷"""
@user.route('/logout', methods=["GET"])
def logout():
    try:
        token = request.headers['Authorization']
        user = token_util.verify_token(token)
        if user:
            key = f"token_{user.get('name')}"
            redis = redis_util.Redis
            redis_token = redis.read(key)
            if redis_token:
                redis.delete(key)
            output = {'code': 1, 'msg': '注銷成功', 'success': True}
            return jsonify(output)
        else:
            output = {'code': 0, 'msg': '認證失敗'}
            return jsonify(output)
    except Exception as e:
        output = {'code': 0, 'msg': '注銷失敗', 'exception': e}
        return jsonify(output)


"""根據用戶角色從數據字典獲取菜單"""
@user.route('/menu', methods=["GET"])
@token_util.login_required()
def menu():
    try:
        token = request.headers['Authorization']
        user = token_util.verify_token(token)
        if user:
            role = user['role']
            menu = dataDictionary.query.filter(dataDictionary.key == role).first()
            output = {'code': 1, 'data': ast.literal_eval(menu.value), 'success': True}
            return jsonify(output)
        else:
            output = {'code': 0, 'msg': '認證失敗'}
            return jsonify(output)
    except Exception as e:
        output = {'code': 0, 'msg': '獲取菜單失敗', 'exception': e}
        return jsonify(output)
