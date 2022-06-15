from flask import Blueprint, jsonify, request

from utils.extensions import db
from models.apiTestModel import Api
from models.apiTestModel import ApiTestcase
from models.projectModel import ProjectModule
from utils import tokenUtil
from utils import errorCode

api = Blueprint('api', __name__)


"""根据项目环境配置的id查找module"""
@api.route('/getAllApiModule', methods=['get'])
@tokenUtil.login_required('admin_role', 'test_role')
def load_all_apiModule():
    # 从get请求获取参数
    param_e_id = request.args.get('id')
    # 根据id找到module
    apiModules = ProjectModule.query.filter(ProjectModule.projectEnvironment_id == param_e_id).all()
    output = []
    if apiModules is not None:
        for apiModule in apiModules:
            dic = {'value': apiModule.module_name, 'id': apiModule.id}
            output.append(dic)

    return jsonify(output)


"""获取api列表"""
@api.route('/apiList', methods=['get'])
@tokenUtil.login_required('admin_role', 'test_role')
def list_api():
    # 从get请求获取参数
    param_currentPage = request.args.get('currentPage')
    param_pageSize = request.args.get('pageSize')
    param_projectEnvironmentId = request.args.get('projectEnvironmentId')
    param_apiModuleId = request.args.get('apiModuleId')
    param_apiModuleName = request.args.get('apiModuleName')
    param_apiName = request.args.get('apiName')
    param_url = request.args.get('url')
    # 判断有没有选项目环境
    if param_projectEnvironmentId == '':
        return errorCode.DoesNotChooseProjectEnv()

    filterList = []

    # 判断param_apiModuleId是否为空，为空代表用户未输入模块名查询，默认显示该环境下所有api
    if param_apiModuleId is not None and param_apiModuleId != '':
        # apiModule = ProjectModule.query.filter(ProjectModule.id == param_apiModuleId).first()
        sql = """
                WITH RECURSIVE cte AS
                (SELECT * FROM project_module WHERE id = :id
                UNION ALL
                SELECT project_module.* FROM project_module INNER JOIN cte ON project_module.parent_id = cte.id)
                SELECT distinct * FROM cte;
                """
        rets = db.session.execute(sql, {'id': param_apiModuleId})
        rets = list(rets)
        rets_list = []
        for ret in rets:
            # 取出结果集中的第一列id，并添加进result_list中
            row = list(ret._data)
            rets_list.append(row[0])

        if rets_list is not None:
            filterList.append(Api.apiModule_id.in_(rets_list))
    else:
        if param_apiModuleName is not None and param_apiModuleName != '':
            output = {'code': 1000, 'msg': None, 'count': 0, 'success': True, 'data': ''}
            return jsonify(output)
        # 找出当前环境id下所有api_module
        apiModules = ProjectModule.query.filter(ProjectModule.projectEnvironment_id == param_projectEnvironmentId).all()
        if apiModules is not None:
            # 遍历取出所有id组成list
            id_list = []
            for apiModule in apiModules:
                id_list.append(apiModule.id)
            filterList.append(Api.apiModule_id.in_(id_list))

    if param_apiName is not None and param_apiName != '':
        filterList.append(Api.api_name.like('%{keyword}%'.format(keyword=param_apiName)))
    if param_url is not None and param_url != '':
        filterList.append(Api.url.like('%{keyword}%'.format(keyword=param_url)))

    apis = Api.query.filter(*filterList).order_by(Api.seq).paginate(int(param_currentPage), int(param_pageSize)).items
    num = Api.query.filter(*filterList).count()

    # 封装字典并转成json返回前端
    output = {'code': 1000, 'msg': None, 'count': num, 'success': True}
    data_list = []
    for api in apis:
        module_name = api.project_module.module_name
        dic = api.to_json()
        dic['module_name'] = module_name
        # 删除字典中的project对象，否则转json会报错
        del dic['project_module']
        data_list.append(dic)
    output['data'] = data_list

    return jsonify(output)


"""保存api"""
@api.route('/saveApi', methods=['post'])
@tokenUtil.login_required('admin_role', 'test_role')
def add_api():
    # 从post请求拿参数
    data = request.get_json()
    param_module_id = data['module_id']
    param_request_method = data['request_method']
    param_api_name = data['api_name']
    param_url = data['url']
    param_summary = data['summary']
    param_independent = data['independent']

    num = Api.query.filter(Api.apiModule_id == param_module_id).count()
    api1 = Api(apiModule_id=param_module_id, request_method=param_request_method, api_name=param_api_name, url=param_url, summary=param_summary, seq=num+1, status=False, independent=param_independent)
    db.session.add(api1)
    db.session.commit()
    output = {'code': 1000, 'msg': '保存成功', 'exception': None, 'success': True}

    return jsonify(output)


"""保存api"""
@api.route('/saveApi', methods=['put'])
@tokenUtil.login_required('admin_role', 'test_role')
def edit_api():
    # 从put请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_module_id = data['module_id']
    param_request_method = data['request_method']
    param_api_name = data['api_name']
    param_url = data['url']
    param_summary = data['summary']
    param_independent = data['independent']
    if not param_id:
        return errorCode.ValError()

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
    output = {'code': 1000, 'msg': '保存成功', 'exception': None, 'success': True}

    return jsonify(output)


"""删除api"""
@api.route('/deleteApi', methods=['delete'])
@tokenUtil.login_required('admin_role', 'test_role')
def delete_api():
    # 从delete请求拿参数
    param_id = request.args.get('id')
    param_apiModule_id = request.args.get('apiModule_id')
    param_seq = int(request.args.get('seq'))
    if not param_id:
        return errorCode.ValError()

    api1 = Api.query.get(param_id)
    db.session.delete(api1)
    # 删除后要将排序号更大的数据批量更新-1
    apis = db.session.query(Api).filter(Api.apiModule_id == param_apiModule_id, Api.seq > param_seq).all()
    for api in apis:
        api.seq = api.seq - 1
    db.session.commit()
    output = {'code': 1000, 'msg': '删除成功', 'exception': None, 'success': True}

    return jsonify(output)


"""api上移"""
@api.route('/upApi', methods=['put'])
@tokenUtil.login_required('admin_role', 'test_role')
def up_api():
    # 从put请求获取参数
    data = request.get_json()
    param_apiModule_id = data['apiModule_id']
    param_seq = int(data['seq'])
    param_form_apiModule_name = data['form_apiModule_name']

    if param_form_apiModule_name == '' or param_form_apiModule_name is None:
        return errorCode.DoesNotChooseModule()
    else:
        api1 = db.session.query(Api).filter(Api.apiModule_id == param_apiModule_id, Api.seq == param_seq).first()
        api2 = db.session.query(Api).filter(Api.apiModule_id == param_apiModule_id, Api.seq == param_seq - 1).first()
        api1.seq = param_seq - 1
        api2.seq = param_seq
        db.session.commit()
        output = {'code': 1000, 'msg': '上移成功', 'exception': None, 'success': True}

    return jsonify(output)


"""api下移"""
@api.route('/downApi', methods=['put'])
@tokenUtil.login_required('admin_role', 'test_role')
def down_api():
    # 从put请求获取参数
    data = request.get_json()
    param_apiModule_id = data['apiModule_id']
    param_seq = int(data['seq'])
    param_form_apiModule_name = data['form_apiModule_name']

    if param_form_apiModule_name == '' or param_form_apiModule_name is None:
        return errorCode.DoesNotChooseModule()
    else:
        api1 = db.session.query(Api).filter(Api.apiModule_id == param_apiModule_id, Api.seq == param_seq).first()
        api2 = db.session.query(Api).filter(Api.apiModule_id == param_apiModule_id, Api.seq == param_seq + 1).first()
        api1.seq = param_seq + 1
        api2.seq = param_seq
        db.session.commit()
        output = {'code': 1000, 'msg': '下移成功', 'exception': None, 'success': True}

    return jsonify(output)


"""状态启用/禁用"""
@api.route('/changeApiStatus', methods=['put'])
@tokenUtil.login_required('admin_role', 'test_role')
def change_status():
    # 从put请求获取参数
    data = request.get_json()
    param_id = data['id']
    param_status = data['status']
    if not param_id:
        return errorCode.ValError()

    api1 = Api.query.get(param_id)
    if param_status is True:
        api1.status = 1
    else:
        api1.status = 0
    db.session.commit()
    output = {'code': 1000, 'msg': '变更状态成功', 'exception': None, 'success': True}

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

