from flask import Blueprint, jsonify, request
from utils.extensions import db
from models.apiTestModel import Api
from models.projectModel import ProjectEnvironment
from models.projectModel import Project
from models.projectModel import ProjectModule
import datetime
from utils import token_util

projectModule = Blueprint('projectModule', __name__)

"""根据项目环境id获取api模块"""
@projectModule.route('/projectModuleList', methods=['get'])
@token_util.login_required('admin_role', 'test_role')
def list_projectModule():
    try:
        # 从get请求获取参数
        param_projectEnvironment_id = request.args.get('projectEnvironment_id')
        # 根据param_projectEnvironment_id判断是否有选择项目环境名称，如果没有，返回提示
        if param_projectEnvironment_id != '':
            sql = """
            WITH RECURSIVE cte AS
            (SELECT * FROM project_module WHERE projectEnvironment_id = :projectEnvironment_id
            UNION ALL
            SELECT project_module.* FROM project_module INNER JOIN cte ON project_module.parent_id = cte.id)
            SELECT distinct * FROM cte;
            """
            rets = db.session.execute(sql, {'projectEnvironment_id': param_projectEnvironment_id})
            rets = list(rets)
            rets_list = []
            # 查询结果集格式调整为符合json的格式
            for ret in rets:
                # 取出结果集中的列明和值，将tuple类型转为list类型，再把冒烟测试通过率的decimal类型转成保留两位小数的float类型，并添加进result_list中
                column = list(ret._fields)
                row = list(ret._data)
                dic = dict(zip(column, row))
                rets_list.append(dic)
            # # 将数据格式处理为前端el-tree的格式
            # result_dict = {}
            # for l in rets_list:
            #     l["parent_id"] = l["parent_id"] if l["parent_id"] else 0
            #     result_dict.setdefault(l['id'], l).update(l)
            #     result_dict.setdefault(l['parent_id'], {}).setdefault('children', []).append(result_dict.get(l['id'], l))
            # result_list = result_dict[0]['children']
            output = {'code': 1, 'msg': None, 'success': True, 'data': rets_list}
        else:
            output = {'code': 0, 'msg': '未选择项目环境名称', 'count': 0, 'success': False, 'data': ''}
            return jsonify(output)
    except Exception as e:
        output = {'code': 0, 'msg': '获取模块列表失败', 'count': 0, 'success': False, 'errorMsg': e}

    return jsonify(output)


"""添加功能模块"""
@projectModule.route('/saveProjectModule', methods=['post'])
@token_util.login_required('admin_role', 'test_role')
def add_projectModule():
    # 从post请求拿参数
    data = request.get_json()
    param_e_id = data['e_id']
    param_parent_id = data['parent_id'] if data['parent_id'] != '' else 0
    param_m_name = data['m_name']
    param_m_description = data['m_description']
    param_create_time = datetime.datetime.now()
    try:
        if param_e_id == '':
            output = {'code': 0, 'msg': '请选择项目环境并查询', 'exception': None, 'success': False}
            return jsonify(output)
        projectModule1 = ProjectModule(projectEnvironment_id=param_e_id, parent_id=param_parent_id, module_name=param_m_name, module_description=param_m_description, create_time=param_create_time)
        db.session.add(projectModule1)
        db.session.commit()
        output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '保存失败', 'exception': e.args[0], 'success': False}

    return jsonify(output)


"""修改功能模块"""
@projectModule.route('/saveProjectModule', methods=['put'])
@token_util.login_required('admin_role', 'test_role')
def edit_projectModule():
    # 从pput请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_e_id = data['e_id']
    param_parent_id = data['parent_id'] if data['parent_id'] != '' else 0
    param_m_name = data['m_name']
    param_m_description = data['m_description']
    try:
        if param_e_id == '':
            output = {'code': 0, 'msg': '请选择项目环境并查询', 'exception': None, 'success': False}
            return jsonify(output)
        if param_parent_id == param_id:
            output = {'code': 0, 'msg': '父模块不能选择自己', 'exception': None, 'success': False}
            return jsonify(output)
        projectModule1 = ProjectModule.query.get(param_id)
        projectModule1.projectEnvironment_id = param_e_id
        projectModule1.parent_id = param_parent_id
        projectModule1.module_name = param_m_name
        projectModule1.module_description = param_m_description
        db.session.commit()
        output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '保存失败', 'exception': e.args[0], 'success': False}

    return jsonify(output)


"""删除api模块"""
@projectModule.route('/deleteProjectModule', methods=['delete'])
@token_util.login_required('admin_role', 'test_role')
def delete_projectModule():
    # 从delete请求拿参数
    param_id = request.args.get('id')
    try:
        if param_id == '':
            output = {'code': 0, 'msg': '请选择模块', 'exception': None, 'success': False}
            return jsonify(output)
        api_num = Api.query.filter(Api.apiModule_id == param_id).count()
        if api_num != 0:
            output = {'code': 0, 'msg': '该模块下存在接口，不能删除', 'exception': None, 'success': False}
            return jsonify(output)
        projectModule_num = ProjectModule.query.filter(ProjectModule.parent_id == param_id).count()
        if projectModule_num != 0:
            output = {'code': 0, 'msg': '该模块下存在其他模块，不能删除', 'exception': None, 'success': False}
            return jsonify(output)
        projectModule1 = ProjectModule.query.get(param_id)
        db.session.delete(projectModule1)
        db.session.commit()
        output = {'code': 1, 'msg': '删除成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '删除失败', 'exception': e, 'success': False}

    return jsonify(output)


"""根据项目名称获取项目环境"""
@projectModule.route('/getAllProjectEnvironment', methods=['get'])
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
