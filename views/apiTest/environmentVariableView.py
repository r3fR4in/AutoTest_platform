from flask import Blueprint, jsonify, request

from utils.extensions import db
from models.apiTestModel import EnvironmentVariable
from utils import tokenUtil
from utils import errorCode

environmentVariable = Blueprint('environmentVariable', __name__)

"""获取环境变量数据"""
@environmentVariable.route('/getEnvironmentVariable', methods=['get'])
@tokenUtil.login_required('admin_role', 'test_role')
def list_environmentVariable():
    # 从get请求获取参数
    param_currentPage = request.args.get('currentPage')
    param_pageSize = request.args.get('pageSize')
    param_e_id = request.args.get('e_id')
    param_ev_name = request.args.get('ev_name')
    if param_e_id == '':
        return errorCode.DoesNotChooseProjectEnv()

    filterList = []

    if param_e_id is not None and param_e_id != '':
        filterList.append(EnvironmentVariable.e_id == param_e_id)
    if param_ev_name is not None and param_ev_name != '':
        filterList.append(EnvironmentVariable.name.like("%" + str(param_ev_name) + "%"))

    # 根据e_id获取环境变量
    environmentVariables = EnvironmentVariable.query.filter(*filterList).paginate(int(param_currentPage), int(param_pageSize)).items
    environmentVariableNum = EnvironmentVariable.query.filter(*filterList).count()

    # 封装字典并转成json返回前端
    output = {'code': 1000, 'msg': None, 'count': environmentVariableNum, 'success': True}
    environmentVariableList = []
    for ev in environmentVariables:
        environmentVariableList.append(ev.to_json())
    output['data'] = environmentVariableList

    return jsonify(output)


"""保存环境变量"""
@environmentVariable.route('/saveEnvironmentVariable', methods=['post'])
@tokenUtil.login_required('admin_role', 'test_role')
def add_environmentVariable():
    # 从post请求拿参数
    data = request.get_json()
    param_e_id = data['e_id']
    param_name = data['name']
    param_value = data['value']

    # 先判断变量名是否重复
    name_list = EnvironmentVariable.query.filter(EnvironmentVariable.e_id == param_e_id, EnvironmentVariable.name == param_name).all()
    if name_list:
        return errorCode.ExistSameEnvVar()
    else:
        environmentVariable1 = EnvironmentVariable(e_id=param_e_id, name=param_name, value=param_value)
        db.session.add(environmentVariable1)
        db.session.commit()
        output = {'code': 1000, 'msg': '保存成功', 'exception': None, 'success': True}

    return jsonify(output)


"""保存环境变量"""
@environmentVariable.route('/saveEnvironmentVariable', methods=['put'])
@tokenUtil.login_required('admin_role', 'test_role')
def edit_environmentVariable():
    # 从put请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_e_id = data['e_id']
    param_name = data['name']
    param_value = data['value']

    environmentVariable1 = EnvironmentVariable.query.get(param_id)
    environmentVariable1.e_id = param_e_id
    environmentVariable1.name = param_name
    environmentVariable1.value = param_value
    db.session.commit()
    output = {'code': 1000, 'msg': '保存成功', 'exception': None, 'success': True}

    return jsonify(output)


"""删除环境变量"""
@environmentVariable.route('/deleteEnvironmentVariable', methods=['delete'])
@tokenUtil.login_required('admin_role', 'test_role')
def delete_environmentVariable():
    # 从delete请求拿参数
    param_id = request.args.get('id')

    environmentVariable1 = EnvironmentVariable.query.get(param_id)
    db.session.delete(environmentVariable1)
    db.session.commit()
    output = {'code': 1000, 'msg': '删除成功', 'exception': None, 'success': True}

    return jsonify(output)
