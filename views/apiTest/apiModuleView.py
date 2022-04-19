from flask import Blueprint, jsonify, request
from utils.extensions import db
from models.projectModel import ProjectModule
from models.projectModel import ProjectEnvironment
from models.projectModel import Project
import datetime
from utils import token_util

apiModule = Blueprint('apiModule', __name__)


"""根据项目名称获取项目环境"""
@apiModule.route('/getAllProjectEnvironment', methods=['get'])
@token_util.login_required('admin_role', 'test_role')
def load_all_projectEnvironment():
    # 从get请求获取参数
    param_projectName = request.args.get('name')
    # 根据projectName找到project
    project = Project.query.filter(Project.projectName == param_projectName).first()
    output = []
    if project is not None:
        # 根据project的id找到projectEnvironment
        projectEnvironments = ProjectEnvironment.query.filter(ProjectEnvironment.project_id == project.id).all()
        for projectEnvironment in projectEnvironments:
            dic = {'value': projectEnvironment.id, 'label': projectEnvironment.e_name}
            output.append(dic)

    return jsonify(output)


"""根据项目环境id获取api模块"""
@apiModule.route('/apiModuleList', methods=['get'])
@token_util.login_required('admin_role', 'test_role')
def list_apiModule():
    try:
        # 从get请求获取参数
        param_currentPage = request.args.get('currentPage')
        param_pageSize = request.args.get('pageSize')
        param_projectEnvironment_id = request.args.get('projectEnvironment_id')
        # 根据param_projectEnvironment_id判断是否有选择项目环境名称，如果没有，返回提示
        if param_projectEnvironment_id != '':
            apiModules = ProjectModule.query.filter(ProjectModule.projectEnvironment_id == param_projectEnvironment_id).paginate(int(param_currentPage), int(param_pageSize)).items
            num = ProjectModule.query.filter(ProjectModule.projectEnvironment_id == param_projectEnvironment_id).count()
        else:
            output = {'code': 0, 'msg': '未选择项目环境名称', 'count': 0, 'success': False, 'data': ''}
            return jsonify(output)

        # 封装字典并转成json返回前端
        output = {'code': 0, 'msg': None, 'count': num, 'success': True}
        list = []
        for apiModule in apiModules:
            list.append(apiModule.to_json())
        output['data'] = list
    except Exception as e:
        output = {'code': 0, 'msg': '获取api模块列表失败', 'count': 0, 'success': False, 'errorMsg': e}

    return jsonify(output)


"""添加或修改功能模块"""
@apiModule.route('/saveApiModule', methods=['post'])
@token_util.login_required('admin_role', 'test_role')
def save_apiModule():
    # 从post请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_e_id = data['e_id']
    param_m_name = data['m_name']
    param_m_description = data['m_description']
    param_create_time = datetime.datetime.now()
    # 根据id判断新增或编辑，id为空则是新增，否则为编辑
    try:
        if param_id == '':
            apiModule1 = ProjectModule(projectEnvironment_id=param_e_id, module_name=param_m_name, module_description=param_m_description, create_time=param_create_time)
            db.session.add(apiModule1)
            db.session.commit()
            output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
        else:
            apiModule1 = ProjectModule.query.get(param_id)
            apiModule1.projectEnvironment_id = param_e_id
            apiModule1.module_name = param_m_name
            apiModule1.module_description = param_m_description
            db.session.commit()
            output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '保存失败', 'exception': e.args[0], 'success': False}

    return jsonify(output)


"""删除api模块"""
@apiModule.route('/deleteApiModule', methods=['delete'])
@token_util.login_required('admin_role', 'test_role')
def delete_apiModule():
    # 从delete请求拿参数
    param_id = request.args.get('id')
    # 删除项目环境配置
    try:
        apiModule1 = ProjectModule.query.get(param_id)
        db.session.delete(apiModule1)
        db.session.commit()
        output = {'code': 1, 'msg': '删除成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '删除失败', 'exception': e, 'success': False}

    return jsonify(output)
