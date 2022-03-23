from flask import Blueprint, jsonify, request

from utils.extensions import db
from models.apiTestModel import EnvironmentVariable
from utils import token_util

environmentVariable = Blueprint('environmentVariable', __name__)

"""获取环境变量数据"""
@environmentVariable.route('/getEnvironmentVariable', methods=['get'])
@token_util.login_required()
def list_environmentVariable():
    try:
        # 从get请求获取参数
        param_currentPage = request.args.get('currentPage')
        param_pageSize = request.args.get('pageSize')
        param_e_id = request.args.get('e_id')
        if param_e_id == '':
            output = {'code': 0, 'msg': '未选择项目环境查询', 'count': 0, 'success': False}
            return jsonify(output)
        # 根据e_id获取环境变量
        environmentVariables = EnvironmentVariable.query.filter(EnvironmentVariable.e_id == param_e_id).paginate(int(param_currentPage), int(param_pageSize)).items
        environmentVariableNum = EnvironmentVariable.query.filter(EnvironmentVariable.e_id == param_e_id).count()

        # 封装字典并转成json返回前端
        output = {'code': 1, 'msg': None, 'count': environmentVariableNum, 'success': True}
        environmentVariableList = []
        for ev in environmentVariables:
            environmentVariableList.append(ev.to_json())
        output['data'] = environmentVariableList
    except Exception as e:
        output = {'code': 0, 'msg': '获取环境变量失败', 'count': 0, 'success': False, 'errorMsg': e}

    return jsonify(output)


"""保存环境变量"""
@environmentVariable.route('/saveEnvironmentVariable', methods=['post'])
@token_util.login_required()
def save_environmentVariable():
    try:
        # 从post请求拿参数
        data = request.get_json()
        param_id = data['id']
        param_e_id = data['e_id']
        param_name = data['name']
        param_value = data['value']

        # 先判断变量名是否重复
        name_list = EnvironmentVariable.query.filter(EnvironmentVariable.e_id == param_e_id, EnvironmentVariable.name == param_name).all()
        if name_list:
            output = {'code': 0, 'msg': '同一环境下变量名重复', 'count': 0, 'success': False}
        else:
            # 根据id判断新增或编辑，id为空则是新增，否则为编辑
            if param_id == '':
                environmentVariable1 = EnvironmentVariable(e_id=param_e_id, name=param_name, value=param_value)
                db.session.add(environmentVariable1)
                db.session.commit()
                output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
            else:
                environmentVariable1 = EnvironmentVariable.query.get(param_id)
                environmentVariable1.e_id = param_e_id
                environmentVariable1.name = param_name
                environmentVariable1.value = param_value
                db.session.commit()
                output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '获取环境变量失败', 'count': 0, 'success': False, 'errorMsg': e}

    return jsonify(output)


"""删除环境变量"""
@environmentVariable.route('/deleteEnvironmentVariable', methods=['delete'])
@token_util.login_required()
def delete_environmentVariable():
    # 从delete请求拿参数
    param_id = request.args.get('id')
    try:
        environmentVariable1 = EnvironmentVariable.query.get(param_id)
        db.session.delete(environmentVariable1)
        db.session.commit()
        output = {'code': 1, 'msg': '删除成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '删除失败', 'exception': e, 'success': False}

    return jsonify(output)
