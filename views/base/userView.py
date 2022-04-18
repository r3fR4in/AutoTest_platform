import ast

from flask import Blueprint, jsonify, request
from utils.extensions import db
from models.baseModel import User
from models.baseModel import DataDictionary
from models.baseModel import UserProject
from models.projectModel import Project
from utils import token_util, redis_util
from config import setting
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import and_
import hashlib

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


"""添加用户"""
@user.route('/saveUser', methods=['POST'])
@token_util.login_required()
def add_user():
    # 从post请求拿参数
    data = request.get_json()
    param_username = data['username']
    param_nickname = data['nickname']
    param_role = data['role_code']
    param_phone = data['phone']
    param_email = data['email']
    try:
        user1 = User(username=param_username, password='a123456', nickname=param_nickname, email=param_email, phone=param_phone, status='1', role=param_role)
        db.session.add(user1)
        db.session.commit()
        output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '保存失败', 'exception': e, 'success': False}

    return jsonify(output)


"""修改用户"""
@user.route('/saveUser', methods=['put'])
@token_util.login_required()
def edit_user():
    # 从pput请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_username = data['username']
    param_nickname = data['nickname']
    param_role = data['role_code']
    param_phone = data['phone']
    param_email = data['email']
    try:
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
@user.route('/changeUserStatus', methods=['put'])
@token_util.login_required()
def change_user_status():
    # 从put请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_status = data['status']
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
    # 从delete请求拿参数
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
@user.route('/resetPwd', methods=['put'])
@token_util.login_required()
def reset_pwd():
    # 从put请求拿参数
    data = request.get_json()
    param_id = data['id']
    try:
        user1 = User.query.get(param_id)
        pwd = 'a123456'
        m = hashlib.md5()
        b = pwd.encode('utf-8')
        m.update(b)
        str_md5 = m.hexdigest()
        user1.password = str_md5
        db.session.commit()
        output = {'code': 1, 'msg': '重置成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '重置失败', 'exception': e, 'success': False}

    return jsonify(output)


"""返回项目权限分配列表"""
@user.route('/projectPermissionsList', methods=['GET'])
@token_util.login_required()
def list_project_permissions():
    # 从get请求拿参数
    param_id = request.args.get('id')
    try:
        # userProjects = User.query.filter(User.id == param_id).join(user_project).join(Project).with_entities(User.id, Project.id, Project.projectName).all()
        userProjects = Project.query.outerjoin(UserProject, and_(UserProject.project_id == Project.id, UserProject.user_id == param_id)).with_entities(Project.id, Project.projectName, UserProject.user_id).all()
        # 封装字典并转成json返回前端
        output = {'code': 1, 'msg': None, 'success': True}
        key_list = ['project_id', 'projectName', 'user_id']
        userProjectList = []
        for userProject in userProjects:
            dic = dict(zip(key_list, list(userProject)))
            userProjectList.append(dic)
        output['data'] = userProjectList
    except Exception as e:
        output = {'code': 0, 'msg': '获取项目权限分配列表失败', 'exception': e, 'success': False}

    return jsonify(output)


"""保存项目权限分配"""
@user.route('/projectPermissionsSave', methods=['POST'])
@token_util.login_required()
def save_project_permissions():
    # 从post请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_list = data['list']
    try:
        UserProject.query.filter(UserProject.user_id == param_id).delete(synchronize_session=False)
        if param_list is not None and param_list != []:
            userProject_list = []
            for item in param_list:
                userProject = UserProject(user_id=param_id, project_id=item['project_id'])
                userProject_list.append(userProject)
            db.session.add_all(userProject_list)
        db.session.commit()
        output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '获取项目权限分配列表失败', 'exception': e, 'success': False}

    return jsonify(output)


"""修改密码"""
@user.route('/modifyPwd', methods=['POST'])
@token_util.login_required()
def modify_pwd():
    try:
        # 从post请求拿参数
        data = request.get_json()
        param_old_password = data['old_password']
        param_new_password = data['new_password']
        param_confirm_password = data['confirm_password']
        if param_new_password != param_confirm_password:
            output = {'code': 0, 'msg': '确认密码与新密码不一致', 'exception': None, 'success': False}
            return jsonify(output)
        # 在请求头上拿到token
        token = request.headers["Authorization"]
        s = Serializer(setting.SECRET_KEY)
        user = s.loads(token)
        user1 = User.query.get(user["id"])
        if user1.password != param_old_password:
            output = {'code': 0, 'msg': '原密码错误', 'exception': None, 'success': False}
            return jsonify(output)
        user1.password = param_confirm_password
        db.session.commit()
        output = {'code': 1, 'msg': '修改密码成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '获取项目权限分配列表失败', 'exception': e, 'success': False}

    return jsonify(output)
