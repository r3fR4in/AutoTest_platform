from flask import Blueprint, jsonify, request
from utils.extensions import db
from models.projectModel import Project
from models.projectModel import ProjectEnvironment
import datetime
from utils import tokenUtil
from utils import errorCode

project = Blueprint('project', __name__)


"""获取项目列表"""
@project.route('/projectList', methods=['GET'])
@tokenUtil.login_required('admin_role', 'test_role')
def list_project():
    # 从get请求拿参数
    param_currentPage = request.args.get('currentPage')
    param_pageSize = request.args.get('pageSize')
    param_projectName = request.args.get('projectName')
    # 获取项目列表和项目数
    projects = Project.query.filter(Project.projectName.like("%" + str(param_projectName) + "%")).paginate(int(param_currentPage), int(param_pageSize)).items
    projectNum = Project.query.filter(Project.projectName.like("%" + str(param_projectName) + "%")).count()

    # 封装字典并转成json返回前端
    projects_output = {'code': 1000, 'msg': None, 'count': projectNum, 'success': True}
    projectList = []
    for p in projects:
        projectList.append(p.to_json())
    projects_output['data'] = projectList

    return jsonify(projects_output)


"""添加项目"""
@project.route('/saveProject', methods=['post'])
@tokenUtil.login_required('admin_role', 'test_role')
def add_project():
    # 从post请求拿参数
    data = request.get_json()
    param_projectName = data['projectName']
    param_projectDescription = data['projectDescription']
    param_create_time = datetime.datetime.now()
    # 根据id判断新增或编辑，id为空则是新增，否则为编辑
    try:
        project1 = Project(projectName=param_projectName, projectDescription=param_projectDescription, create_time=param_create_time)
        db.session.add(project1)
        db.session.commit()
        output = {'code': 1000, 'msg': '保存成功', 'exception': None, 'success': True}
        return jsonify(output)
    except Exception as e:
        if 'pymysql.err.IntegrityError' in e.args[0]:
            return errorCode.ExistSameProject()


"""修改项目"""
@project.route('/saveProject', methods=['put'])
@tokenUtil.login_required('admin_role', 'test_role')
def edit_project():
    # 从put请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_projectName = data['projectName']
    param_projectDescription = data['projectDescription']
    if not param_id:
        return errorCode.ValError()

    try:
        project1 = Project.query.get(param_id)
        project1.projectName = param_projectName
        project1.projectDescription = param_projectDescription
        db.session.commit()
        output = {'code': 1000, 'msg': '保存成功', 'exception': None, 'success': True}
        return jsonify(output)
    except Exception as e:
        if 'pymysql.err.IntegrityError' in e.args[0]:
            return errorCode.ExistSameProject()


"""删除项目"""
@project.route('/deleteProject', methods=['delete'])
@tokenUtil.login_required('admin_role', 'test_role')
def delete_project():
    # 从delete请求拿参数
    param_id = request.args.get('id')
    if not param_id:
        return errorCode.ValError()

    # 先找项目环境配置，如果有数据，则不允许删除
    projectEnvironment_num = ProjectEnvironment.query.filter(ProjectEnvironment.project_id == param_id).count()
    if projectEnvironment_num == 0:
        project1 = Project.query.get(param_id)
        db.session.delete(project1)
        db.session.commit()
        output = {'code': 1000, 'msg': '删除成功', 'exception': None, 'success': True}
    else:
        return errorCode.ExistAssociatedProjectEnv()

    return jsonify(output)
