from flask import Blueprint, jsonify, request
from sqlalchemy import and_

from utils.extensions import db
from models.apiTestModel import Api, ApiTestcase
from models.projectModel import ProjectModule, ProjectEnvironment
from utils import tokenUtil
from utils import errorCode
from utils.log import Log
from utils.extensions import celery
import datetime
from engine import send_requests

apiImport = Blueprint('apiImport', __name__)

"""从swagger导入api"""


@apiImport.route('/importFromSwagger', methods=['get'])
@tokenUtil.login_required('admin_role', 'test_role')
def import_api_from_swagger():
    try:
        # 从get请求获取参数
        param_e_id = request.args.get('id')
        param_url = request.args.get('url')
        if param_e_id == '' or param_e_id is None:
            return {'code': 1000, 'msg': '请选择项目环境', 'exception': None, 'success': False}
        if param_url == '' or param_url is None:
            return {'code': 1000, 'msg': '请输入url', 'exception': None, 'success': False}
        import_api_from_swagger_task.delay(param_e_id, param_url)
        output = {'code': 1000, 'msg': '已添加导入任务', 'exception': None, 'success': True}

        return jsonify(output)
    except Exception as e:
        log = Log('log')
        log.error(e)
        return errorCode.SwaggerApiImportError()


"""从swagger导入api异步任务"""
@celery.task()
def import_api_from_swagger_task(e_id, url):
    try:
        # 从swagger获取数据
        log = Log('log')
        re = send_requests.SendRequests('get', url, '', '', '', 'utf-8', True, log).request()
        swagger_data = re.json()
        # 获取环境的url
        env = ProjectEnvironment.query.filter(ProjectEnvironment.id == e_id).all()
        base_url = env[0].url
        # 从数据库获取已有的api数据
        api_datas = Api.query.join(ProjectModule, Api.apiModule_id == ProjectModule.id).filter(ProjectModule.projectEnvironment_id == e_id).all()
        exist_api_list = []
        for api_data in api_datas:
            dic1 = api_data.to_json()
            dic2 = {'url': dic1['url'], 'request_method': dic1['request_method']}
            exist_api_list.append(dic2)
        # 判断环境下有没有未分类接口模块，没有则加上
        unclassified_module = ProjectModule.query.filter(and_(ProjectModule.projectEnvironment_id == e_id, ProjectModule.module_name == '未分类接口')).all()
        if len(unclassified_module) == 0:
            projectModule1 = ProjectModule(projectEnvironment_id=e_id, parent_id=0, module_name='未分类接口', module_description='外部导入的新接口将放入未分类接口中', create_time=datetime.datetime.now())
            db.session.add(projectModule1)
            db.session.commit()
            projectModule_id = projectModule1.id
        else:
            projectModule_id = unclassified_module[0].id
        # 遍历swagger数据，与数据库已存在数据对比，若不存在则入库，同时建一个默认的用例
        for path in swagger_data['paths']:
            dic = {'url': path}
            for request_method in swagger_data['paths'][path]:
                dic['request_method'] = request_method
                # 判断api是否已存在
                if dic not in exist_api_list:
                    num = Api.query.filter(Api.apiModule_id == projectModule_id).count()
                    api1 = Api(apiModule_id=projectModule_id, request_method=request_method, api_name=swagger_data['paths'][path][request_method]['summary'], url=path, summary=swagger_data['paths'][path][request_method]['tags'][0], seq=num + 1, status=False, independent=False)
                    db.session.add(api1)
                    db.session.commit()
                    # 遍历parameters，新建默认的用例
                    headers = {}
                    body = {}
                    for parameter in swagger_data['paths'][path][request_method]['parameters']:
                        if parameter['in'] == 'header':
                            if 'default' in parameter:
                                headers[parameter['name']] = parameter['default']
                            else:
                                headers[parameter['name']] = ''
                        elif parameter['in'] == 'body' or parameter['in'] == 'query':
                            # 使用递归获取完整字段参数，并更新至body中
                            for key, value in get_schema(parameter, swagger_data['definitions']).items():
                                body[key] = value
                    # 添加用例
                    apiTestcase1 = ApiTestcase(api_id=api1.id, title='默认用例', request_method=request_method, request_header=str(headers).replace('\'', '"'), request_body=str(body).replace('\'', '"')
                                               , encode='utf8', encrypt_type='1', verify='true', url=base_url + path, is_assert='false'
                                               , assert_content='', is_post_processor='false'
                                               , post_processor_content='')
                    db.session.add(apiTestcase1)
                    db.session.commit()
    except Exception as e:
        log = Log('log')
        log.error(e)


"""递归获取body参数"""
def get_schema(parameter, definitions):
    if 'schema' in parameter.keys():
        if '$ref' in parameter['schema'].keys():
            schema = parameter['schema']['$ref'].split('#/definitions/')[1]
            body_temp = {}
            for key, value in definitions[schema]['properties'].items():
                dic = {'name': key}
                dic.update(value)
                body_temp.update(get_schema(dic, definitions))
            return {parameter['name']: body_temp}
        else:
            body = {parameter['name']: parameter['schema']['type']}
            return body
    elif 'items' in parameter.keys():
        if '$ref' in parameter['items'].keys():
            schema = parameter['items']['$ref'].split('#/definitions/')[1]
            body_temp = {}
            for key, value in definitions[schema]['properties'].items():
                dic = {'name': key}
                dic.update(value)
                body_temp.update(get_schema(dic, definitions))
            return {parameter['name']: body_temp}
        else:
            body = {parameter['name']: parameter['items']['type']}
            return body
    elif '$ref' in parameter.keys():
        schema = parameter['$ref'].split('#/definitions/')[1]
        body_temp = {}
        for key, value in definitions[schema]['properties'].items():
            dic = {'name': key}
            dic.update(value)
            body_temp.update(get_schema(dic, definitions))
        return {parameter['name']: body_temp}
    else:
        if 'description' in parameter:
            body = {parameter['name']: parameter['type'] + ' ' + parameter['description']}
        else:
            body = {parameter['name']: parameter['type']}
        return body
