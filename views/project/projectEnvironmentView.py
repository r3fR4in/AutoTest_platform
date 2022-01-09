from flask import Blueprint, jsonify, request
from utils.extensions import db
from models.project.projectEnvironmentModel import ProjectEnvironment
from models.project.projectModel import Project
from models.apiTest.apiModel import Api
from models.apiTest.apiTestcaseModel import ApiTestcase
from models.apiTest.apiModuleModel import ApiModule
import datetime
from utils import token_util

projectEnvironment = Blueprint('projectEnvironment', __name__)

"""获取项目环境配置列表"""
@projectEnvironment.route('/projectEnvironmentList', methods=['get'])
@token_util.login_required()
def list_projectEnvironment():
    try:
        # 从get请求获取参数
        param_currentPage = request.args.get('currentPage')
        param_pageSize = request.args.get('pageSize')
        param_projectName = request.args.get('projectName')
        # 判断param_projectName是否为空，为空代表用户未输入搜索框查询，默认显示所有数据
        if param_projectName != '':
            # 根据projectName找到project
            project = Project.query.filter(Project.projectName == param_projectName).first()
            if project is not None:
                # 根据project的id找到projectEnvironment
                projectEnvironments = ProjectEnvironment.query.filter(ProjectEnvironment.project_id == project.id).paginate(int(param_currentPage), int(param_pageSize)).items
                num = ProjectEnvironment.query.filter(ProjectEnvironment.project_id == project.id).count()
            else:
                output = {'code': 1, 'msg': None, 'count': 0, 'success': True, 'data': ''}
                return jsonify(output)
        else:
            # 有风险，如果做项目的权限控制则需要修改
            projectEnvironments = ProjectEnvironment.query.paginate(int(param_currentPage), int(param_pageSize)).items
            num = ProjectEnvironment.query.count()

        # 封装字典并转成json返回前端
        output = {'code': 1, 'msg': None, 'count': num, 'success': True}
        list = []
        for projectEnvironment in projectEnvironments:
            # 获取关联的projectName，并加入字典中
            p_name = projectEnvironment.project.projectName
            dict = projectEnvironment.to_json()
            dict['projectName'] = p_name
            # 删除字典中的project对象，否则转json会报错
            del dict['project']
            list.append(dict)
        output['data'] = list
    except Exception as e:
        output = {'code': 0, 'msg': '获取项目环境配置列表失败', 'count': 0, 'success': False, 'errorMsg': e}

    return jsonify(output)


"""获取所有项目数据"""
@projectEnvironment.route('/getAllProject', methods=['get'])
@token_util.login_required()
def load_all_project():
    projects = Project.query.all()
    projectList = []
    for project in projects:
        # 先转成dict
        p_list = project.to_json()
        # 把projectName单独拿出来拼一个dict
        dic = {'value': p_list['projectName']}
        projectList.append(dic)

    return jsonify(projectList)


"""添加或修改环境配置"""
@projectEnvironment.route('/saveProjectEnvironment', methods=['post'])
def save_projectEnvironment():
    # 从post请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_p_name = data['p_name']
    param_e_name = data['e_name']
    param_url = data['url']
    param_e_description = data['e_description']
    param_create_time = datetime.datetime.now()
    # 根据id判断新增或编辑，id为空则是新增，否则为编辑
    try:
        if param_id == '':
            # 根据项目名称获取项目id
            project1 = Project.query.filter(Project.projectName == param_p_name).first()
            if None is project1:
                output = {'code': 0, 'msg': '保存失败，请输入存在的项目名称', 'exception': None, 'success': False}
            else:
                project1_dict = project1.to_json()
                projectEnvironment1 = ProjectEnvironment(project_id=project1_dict['id'], e_name=param_e_name, url=param_url, e_description=param_e_description, create_time=param_create_time)
                db.session.add(projectEnvironment1)
                db.session.commit()
                output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
        else:
            # 三表关联找到该环境下所有testcase
            api_testcases = db.session.query(ApiTestcase)\
                .join(Api, Api.id == ApiTestcase.api_id)\
                .join(ApiModule, ApiModule.id == Api.apiModule_id)\
                .filter(ApiModule.projectEnvironment_id == param_id).all()
            projectEnvironment_url = db.session.query(ProjectEnvironment.url).filter(ProjectEnvironment.id == param_id).first()
            # 遍历并将url替换成新url
            for api_testcase in api_testcases:
                api_testcase_url = api_testcase.url
                new_url = api_testcase_url.replace(projectEnvironment_url[0], param_url)
                api_testcase.url = new_url
            db.session.commit()

            projectEnvironment1 = ProjectEnvironment.query.get(param_id)
            projectEnvironment1.e_name = param_e_name
            projectEnvironment1.url = param_url
            projectEnvironment1.e_description = param_e_description
            db.session.commit()
            output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '保存失败', 'exception': e.args[0], 'success': False}

    return jsonify(output)


"""删除环境配置"""
@projectEnvironment.route('/deleteProjectEnvironment', methods=['delete'])
@token_util.login_required()
def delete_projectEnvironment():
    # 从delete请求拿参数
    param_id = request.args.get('id')
    # 删除项目环境配置
    try:
        apiModule1 = ApiModule.query.filter(ApiModule.projectEnvironment_id == param_id).first()
        if apiModule1 is None:
            projectEnvironment1 = ProjectEnvironment.query.get(param_id)
            db.session.delete(projectEnvironment1)
            db.session.commit()
            output = {'code': 1, 'msg': '删除成功', 'exception': None, 'success': True}
        else:
            output = {'code': 0, 'msg': '该环境下有数据，无法删除', 'exception': None, 'success': False}
    except Exception as e:
        output = {'code': 0, 'msg': '删除失败', 'exception': e, 'success': False}

    return jsonify(output)


"""复制环境配置"""
@projectEnvironment.route('/copyEnvironment', methods=['get'])
@token_util.login_required()
def copy_environment():
    # 从请求拿参数
    param_id = request.args.get('id')
    try:
        # 添加环境
        projectEnvironment1 = ProjectEnvironment.query.filter(ProjectEnvironment.id == param_id).first()
        projectEnvironment2 = ProjectEnvironment(project_id=projectEnvironment1.project_id, e_name=projectEnvironment1.e_name, url=projectEnvironment1.url
                                                 , e_description=projectEnvironment1.e_description, create_time=datetime.datetime.now())
        db.session.add(projectEnvironment2)
        # 添加模块
        apiModule1 = ApiModule.query.filter(ApiModule.projectEnvironment_id == param_id).all()
        for i in range(len(apiModule1)):
            apiModule2 = ApiModule(projectEnvironment_id=projectEnvironment2.id, module_name=apiModule1[i].module_name, module_description=apiModule1[i].module_description
                                   , create_time=datetime.datetime.now())
            db.session.add(apiModule2)
            # 添加api
            api1 = Api.query.filter(Api.apiModule_id == apiModule1[i].id).all()
            for j in range(len(api1)):
                api2 = Api(apiModule_id=apiModule2.id, request_method=api1[j].request_method, url=api1[j].url, summary=api1[j].summary, seq=api1[j].seq, status=api1[j].status
                           , independent=api1[j].independent)
                db.session.add(api2)
                # 添加api testcase
                apiTestcase1 = ApiTestcase.query.filter(ApiTestcase.api_id == api1[j].id).all()
                for k in range(len(apiTestcase1)):
                    apiTestcase2 = ApiTestcase(api_id=api2.id, title=apiTestcase1[k].title, request_method=apiTestcase1[k].request_method, request_header=apiTestcase1[k].request_header
                                   , request_body=apiTestcase1[k].request_body, request_param=apiTestcase1[k].request_param, encode=apiTestcase1[k].encode, verify=apiTestcase1[k].verify
                                   , url=apiTestcase1[k].url, is_assert=apiTestcase1[k].is_assert, assert_content=apiTestcase1[k].assert_content, is_post_processor=apiTestcase1[k].is_post_processor
                                   , post_processor_content=apiTestcase1[k].post_processor_content)
                    db.session.add(apiTestcase2)
        db.session.commit()
        output = {'code': 1, 'msg': '复制成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '复制失败', 'exception': e, 'success': False}

    return jsonify(output)

