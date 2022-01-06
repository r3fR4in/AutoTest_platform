from flask import Blueprint, jsonify, request
from sqlalchemy import and_

from utils.extensions import db
from models.apiTest.apiModel import Api
from models.apiTest.apiTestcaseModel import ApiTestcase
from models.apiTest.apiModuleModel import ApiModule
from models.project.projectEnvironmentModel import ProjectEnvironment
from models.project.projectModel import Project
import datetime
from utils import token_util

api = Blueprint('api', __name__)


"""根据项目环境配置的id查找module"""
@api.route('/getAllApiModule', methods=['get'])
@token_util.login_required()
def load_all_apiModule():
    # 从get请求获取参数
    param_e_id = request.args.get('id')
    # 根据id找到module
    apiModules = ApiModule.query.filter(ApiModule.projectEnvironment_id == param_e_id).all()
    output = []
    if apiModules is not None:
        for apiModule in apiModules:
            dic = {'value': apiModule.module_name, 'id': apiModule.id}
            output.append(dic)

    return jsonify(output)


"""获取api列表"""
@api.route('/apiList', methods=['get'])
@token_util.login_required()
def list_api():
    try:
        # 从get请求获取参数
        param_currentPage = request.args.get('currentPage')
        param_pageSize = request.args.get('pageSize')
        param_projectEnvironmentId = request.args.get('projectEnvironmentId')
        param_apiModuleId = request.args.get('apiModuleId')
        param_apiModuleName = request.args.get('apiModuleName')
        # 判断有没有选项目环境
        if param_projectEnvironmentId == '':
            output = {'code': 0, 'msg': '未选择项目环境名称', 'count': 0, 'success': False}
            return jsonify(output)
        # 判断param_apiModuleName是否为空，为空代表用户未输入模块名查询，默认显示该环境下所有api
        if param_apiModuleName != '':
            # 根据apiModuleName和apiModuleId找到apiModule
            apiModule = ApiModule.query.filter(and_(ApiModule.module_name == param_apiModuleName, ApiModule.id == param_apiModuleId)).first()
            if apiModule is not None:
                apis = Api.query.filter(Api.apiModule_id == apiModule.id).order_by(Api.seq).paginate(int(param_currentPage), int(param_pageSize)).items
                num = Api.query.filter(Api.apiModule_id == apiModule.id).count()
            else:
                output = {'code': 1, 'msg': None, 'count': 0, 'success': True, 'data': ''}
                return jsonify(output)
            # 封装字典并转成json返回前端
            output = {'code': 1, 'msg': None, 'count': num, 'success': True}
            list = []
            for api in apis:
                dic = api.to_json()
                dic['module_name'] = param_apiModuleName
                list.append(dic)
            output['data'] = list
        else:
            # 根据projectEnvironmentId，将表api和api_module进行关联查询，找到该环境下所有api
            # results是一个list，里面一行数据是一个元组，元组包含一个Api和一个ApiModule的model
            results = db.session.query(Api, ApiModule) \
                .join(ApiModule, ApiModule.id == Api.apiModule_id) \
                .filter(ApiModule.projectEnvironment_id == param_projectEnvironmentId).order_by(Api.seq).paginate(int(param_currentPage), int(param_pageSize)).items
            num = db.session.query(Api, ApiModule) \
                .join(ApiModule, ApiModule.id == Api.apiModule_id) \
                .filter(ApiModule.projectEnvironment_id == param_projectEnvironmentId).count()
            # 遍历results
            data = []
            for result in results:
                dic = result[0].to_json()  # 将Api转成dict
                dic['module_name'] = result[1].to_json()['module_name']  # 将ApiModule的module_name拿出来放到dic里
                data.append(dic)
            # 封装字典并转成json返回前端
            output = {'code': 1, 'msg': None, 'count': num, 'success': True, 'data': data}

    except Exception as e:
        output = {'code': 0, 'msg': '获取项目环境配置列表失败', 'count': 0, 'success': False, 'errorMsg': e}

    return jsonify(output)


"""保存api"""
@api.route('/saveApi', methods=['post'])
@token_util.login_required()
def save_api():
    # 从post请求拿参数
    data = request.get_json()
    param_id = data['id']
    # param_module_name = request.form.get('module_name')
    param_module_id = data['module_id']
    param_request_method = data['request_method']
    param_api_name = data['api_name']
    param_url = data['url']
    param_summary = data['summary']
    param_seq = data['seq']
    param_independent = data['independent']
    # 根据id判断新增或编辑，id为空则是新增，否则为编辑
    try:
        if param_id == '':
            api1 = Api(apiModule_id=param_module_id, request_method=param_request_method, api_name=param_api_name, url=param_url, summary=param_summary, seq=param_seq, status=False, independent=param_independent)
            db.session.add(api1)
            db.session.commit()
            output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
        else:
            # 查询该api下所有testcase，并获取其url
            testcase = db.session.query(ApiTestcase).filter(ApiTestcase.api_id == param_id).first()
            if testcase is not None and testcase != '':
                # 替换新的url并批量更新testcase的url
                api_url = db.session.query(Api.url).filter(Api.id == param_id).first()
                new_url = testcase.url.replace(api_url[0], param_url)
                db.session.query(ApiTestcase).filter(ApiTestcase.api_id == param_id).update({'url': new_url, 'request_method': param_request_method})
                db.session.commit()

            api1 = Api.query.get(param_id)
            api1.apiModule_id = param_module_id
            api1.request_method = param_request_method
            api1.api_name = param_api_name
            api1.url = param_url
            api1.summary = param_summary
            api1.independent = param_independent
            db.session.commit()

            output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '保存失败', 'exception': e.args[0], 'success': False}

    return jsonify(output)


"""删除api"""
@api.route('/deleteApi', methods=['delete'])
@token_util.login_required()
def delete_api():
    # 从delete请求拿参数
    param_id = request.args.get('id')
    param_apiModule_id = request.args.get('apiModule_id')
    param_seq = int(request.args.get('seq'))
    try:
        api1 = Api.query.get(param_id)
        db.session.delete(api1)
        # 删除后要将排序号更大的数据批量更新-1
        apis = db.session.query(Api).filter(Api.apiModule_id == param_apiModule_id, Api.seq > param_seq).all()
        for api in apis:
            api.seq = api.seq - 1
        db.session.commit()
        output = {'code': 1, 'msg': '删除成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '删除失败', 'exception': e, 'success': False}

    return jsonify(output)


"""api上移"""
@api.route('/upApi', methods=['get'])
@token_util.login_required()
def up_api():
    # 从get请求获取参数
    param_apiModule_id = request.args.get('apiModule_id')
    param_seq = int(request.args.get('seq'))
    param_form_apiModule_name = request.args.get('form_apiModule_name')
    try:
        if param_form_apiModule_name == '' or param_form_apiModule_name is None:
            output = {'code': 0, 'msg': '未选择模块，不能上移', 'exception': None, 'success': False}
        else:
            api1 = db.session.query(Api).filter(Api.apiModule_id == param_apiModule_id, Api.seq == param_seq).first()
            api2 = db.session.query(Api).filter(Api.apiModule_id == param_apiModule_id, Api.seq == param_seq - 1).first()
            api1.seq = param_seq - 1
            api2.seq = param_seq
            db.session.commit()
            output = {'code': 1, 'msg': '上移成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '上移失败', 'exception': e, 'success': False}

    return jsonify(output)


"""api下移"""
@api.route('/downApi', methods=['get'])
@token_util.login_required()
def down_api():
    # 从get请求获取参数
    param_apiModule_id = request.args.get('apiModule_id')
    param_seq = int(request.args.get('seq'))
    param_form_apiModule_name = request.args.get('form_apiModule_name')
    try:
        if param_form_apiModule_name == '' or param_form_apiModule_name is None:
            output = {'code': 0, 'msg': '未选择模块，不能下移', 'exception': None, 'success': False}
        else:
            api1 = db.session.query(Api).filter(Api.apiModule_id == param_apiModule_id, Api.seq == param_seq).first()
            api2 = db.session.query(Api).filter(Api.apiModule_id == param_apiModule_id, Api.seq == param_seq + 1).first()
            api1.seq = param_seq + 1
            api2.seq = param_seq
            db.session.commit()
            output = {'code': 1, 'msg': '下移成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '下移失败', 'exception': e, 'success': False}

    return jsonify(output)


"""状态启用/禁用"""
@api.route('/changeApiStatus', methods=['get'])
@token_util.login_required()
def change_status():
    # 从get请求获取参数
    param_id = request.args.get('id')
    param_status = request.args.get('status')
    try:
        api1 = Api.query.get(param_id)
        if param_status == 'true':
            api1.status = 1
        else:
            api1.status = 0
        db.session.commit()
        output = {'code': 1, 'msg': '变更状态成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '变更状态失败', 'exception': e, 'success': False}

    return jsonify(output)


# @api.route('/test', methods=['get'])
# def test():
#     lists = db.session.query(Api, ApiModule)\
#         .join(ApiModule, ApiModule.id == Api.apiModule_id)\
#         .filter(ApiModule.projectEnvironment_id == 1).all()
#
#     for list in lists:
#         print(list[0].to_json())
#         print(list[1].to_json())
#
#     return 'yes'

