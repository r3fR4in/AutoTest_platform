import ast

from flask import Blueprint, jsonify, request
from utils.extensions import db
from models.baseModel import User
from models.baseModel import DataDictionary
from utils import token_util, redis_util
from config import setting
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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
    data = {'token': token, 'nickname': user.nickname, 'role': user.role}
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
            menu = DataDictionary.query.filter(DataDictionary.key == role).first()
            output = {'code': 1, 'data': ast.literal_eval(menu.value), 'success': True}
            return jsonify(output)
        else:
            output = {'code': 0, 'msg': '認證失敗'}
            return jsonify(output)
    except Exception as e:
        output = {'code': 0, 'msg': '獲取菜單失敗', 'exception': e}
        return jsonify(output)


"""获取用户列表"""
@user.route('/userList', methods=['GET'])
@token_util.login_required()
def list_user():
    try:
        # 从get请求拿参数
        param_currentPage = request.args.get('currentPage')
        param_pageSize = request.args.get('pageSize')
        param_nickname = request.args.get('nickname')
        # 获取用户列表和用户数
        users = User.query.filter(User.nickname.like("%" + str(param_nickname) + "%")).paginate(int(param_currentPage), int(param_pageSize)).items
        userNum = User.query.filter(User.nickname.like("%" + str(param_nickname) + "%")).count()
        # 封装字典并转成json返回前端
        output = {'code': 1, 'msg': None, 'count': userNum, 'success': True}
        userList = []
        for p in users:
            userList.append(p.to_json())
        output['data'] = userList
    except Exception as e:
        output = {'code': 0, 'msg': '获取用户列表失败', 'count': 0, 'success': False, 'exception': e}

    return jsonify(output)


"""获取角色权限选项"""
@user.route('/getRoleCode', methods=['GET'])
@token_util.login_required()
def get_role_code():
    try:
        role_option = DataDictionary.query.filter(DataDictionary.key == 'role_option').first()
        output = {'code': 1, 'data': ast.literal_eval(role_option.value), 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '获取角色权限选项失败', 'success': False, 'exception': e}

    return jsonify(output)


"""添加或修改用户"""
@user.route('/saveUser', methods=['POST'])
@token_util.login_required()
def save_user():
    # 从post请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_username = data['username']
    param_nickname = data['nickname']
    param_role = data['role_code']
    param_phone = data['phone']
    param_email = data['email']
    # 根据id判断新增或编辑，id为空则是新增，否则为编辑
    try:
        if param_id == '':
            user1 = User(username=param_username, password='a123456', nickname=param_nickname, email=param_email, phone=param_phone, status='1', role=param_role)
            db.session.add(user1)
            db.session.commit()
            output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
        else:
            user1 = User.query.get(param_id)
            user1.username = param_username
            user1.nickname = param_nickname
            user1.email = param_email
            user1.phone = param_phone
            user1.role = param_role
            db.session.commit()
            output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '保存失败', 'exception': e, 'success': False}

    return jsonify(output)


"""用户状态变更"""
@user.route('/changeUserStatus', methods=['GET'])
@token_util.login_required()
def change_user_status():
    # 从get请求拿参数
    param_id = request.args.get('id')
    param_status = request.args.get('status')
    try:
        user1 = User.query.get(param_id)
        user1.status = param_status
        db.session.commit()
        output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '保存失败', 'exception': e, 'success': False}

    return jsonify(output)


"""删除用户"""
@user.route('/deleteUser', methods=['DELETE'])
@token_util.login_required()
def delete_user():
    # 从get请求拿参数
    param_id = request.args.get('id')
    try:
        # 检查是否删除自己账号，不允许删除自己
        # 在请求头上拿到token
        token = request.headers["Authorization"]
        s = Serializer(setting.SECRET_KEY)
        user = s.loads(token)
        if str(user["id"]) == param_id:
            output = {'code': 0, 'msg': '不允许删除自身账号', 'exception': None, 'success': False}
        else:
            user1 = User.query.get(param_id)
            db.session.delete(user1)
            db.session.commit()
            output = {'code': 1, 'msg': '删除成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '删除失败', 'exception': e, 'success': False}

    return jsonify(output)


"""重置用户名密码"""
@user.route('/resetPwd', methods=['GET'])
@token_util.login_required()
def reset_pwd():
    # 从get请求拿参数
    param_id = request.args.get('id')
    try:
        user1 = User.query.get(param_id)
        user1.password = 'a123456'
        db.session.commit()
        output = {'code': 1, 'msg': '重置成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '重置失败', 'exception': e, 'success': False}

    return jsonify(output)


# """返回项目权限分配列表"""
# @user.route('/projectPermissionsList', methods=['GET'])
# @token_util.login_required()
# def list_project_permissions():
#     # 从get请求拿参数
#     param_id = request.args.get('id')
#     try:
#         userProjects = UserProject.query.filter(UserProject.user_id == param_id).all()
#
#     except Exception as e:
#         output = {'code': 0, 'msg': '获取项目权限分配列表失败', 'exception': e, 'success': False}
#
#     return jsonify(output)
