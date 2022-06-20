import os

from flask import Blueprint, jsonify, request, send_file, after_this_request

from models.baseModel import DataDictionary
from utils import tokenUtil
from engine import api_test
from utils.log import Log
from utils.extensions import db
from models.apiTestModel import ApiTestcase
from models.apiTestModel import Api
from models.projectModel import ProjectModule
from models.projectModel import ProjectEnvironment
import ast, uuid
from config import setting
import mimetypes
from utils.sshConnect import SSH
from utils import errorCode

apiTestcase = Blueprint('apiTestcase', __name__)

"""获取测试用例列表"""
@apiTestcase.route('/apiTestcaseList', methods=['get'])
@tokenUtil.login_required('admin_role', 'test_role')
def list_apiTestcase():
    # 从get请求获取参数
    param_currentPage = request.args.get('currentPage')
    param_pageSize = request.args.get('pageSize')
    param_apiId = request.args.get('api_id')
    # 判断有没有apiId
    if not param_apiId:
        return errorCode.ValError()
    # 获取完整的测试url
    # projectEnvironment_id = db.session.query(ApiModule.projectEnvironment_id).join(Api).filter(Api.id == param_apiId).first()
    # base_url = db.session.query(ProjectEnvironment.url).filter(ProjectEnvironment.id == projectEnvironment_id[0]).first()
    # url = db.session.query(Api.url).filter(Api.id == param_apiId).first()
    # c_url = base_url[0] + url[0]
    # 获取apiTestcase列表
    apiTestcases = ApiTestcase.query.filter(ApiTestcase.api_id == param_apiId).paginate(int(param_currentPage), int(param_pageSize)).items
    num = ApiTestcase.query.filter(ApiTestcase.api_id == param_apiId).count()
    # 封装字典并转成json返回前端
    output = {'code': 1000, 'msg': None, 'count': num, 'success': True}
    list = []
    for apiTestcase in apiTestcases:
        dic = apiTestcase.to_json()
        # dic['url'] = c_url
        del dic['encode']
        del dic['request_body']
        # del dic['request_param']
        del dic['request_header']
        del dic['verify']
        list.append(dic)
    output['data'] = list

    return jsonify(output)


"""删除测试用例"""
@apiTestcase.route('/deleteApiTestcase', methods=['delete'])
@tokenUtil.login_required('admin_role', 'test_role')
def delete_apiTestcase():
    # 从delete请求拿参数
    param_id = request.args.get('id')
    if not param_id:
        return errorCode.ValError()

    apiTestcase1 = ApiTestcase.query.get(param_id)
    db.session.delete(apiTestcase1)
    db.session.commit()
    output = {'code': 1000, 'msg': '删除成功', 'exception': None, 'success': True}

    return jsonify(output)


"""复制测试用例"""
@apiTestcase.route('/copyTestcase', methods=['get'])
@tokenUtil.login_required('admin_role', 'test_role')
def copy_testcase():
    # 从get请求获取参数
    param_id = request.args.get('id')
    if not param_id:
        return errorCode.ValError()

    apiTestcase1 = ApiTestcase.query.get(param_id)
    apitestcase2 = ApiTestcase(api_id=apiTestcase1.api_id, title=apiTestcase1.title, request_method=apiTestcase1.request_method, request_header=apiTestcase1.request_header
                               , request_body=apiTestcase1.request_body, encode=apiTestcase1.encode, verify=apiTestcase1.verify
                               , url=apiTestcase1.url, is_assert=apiTestcase1.is_assert, assert_content=apiTestcase1.assert_content, is_post_processor=apiTestcase1.is_post_processor
                               , post_processor_content=apiTestcase1.post_processor_content, encrypt_type=1)
    db.session.add(apitestcase2)
    db.session.commit()
    output = {'code': 1, 'msg': '复制成功', 'exception': None, 'success': True, 'id': apitestcase2.id}

    return jsonify(output)


"""获取测试用例数据"""
@apiTestcase.route('/apiTestcaseData', methods=['get'])
@tokenUtil.login_required('admin_role', 'test_role')
def get_apiTestcase():
    # 从get请求获取参数
    param_id = request.args.get('id')
    param_apiId = request.args.get('api_id')
    # 获取Api数据
    output = {'code': 1000, 'msg': None, 'success': True}
    if param_id != '':
        apiTestcase = ApiTestcase.query.filter(ApiTestcase.id == param_id).first()
        apiTestcase = apiTestcase.to_json()
        # 封装字典并转成json返回前端
        # apiTestcase['url'] = c_url
        # apiTestcase['request_method'] = request_method
        output['data'] = apiTestcase
        if output['data']['file_name'] != '':
            if output['data']['file_name'] is None:
                output['data']['file_name'] = []
            else:
                file_list = eval(output['data']['file_name'])
                file_name = []
                for file in file_list:
                    file_name.append({'name': file['name'], 'realname': file['realname']})
                output['data']['file_name'] = file_name
    else:
        # 获取完整的测试url和request_method
        # 判断是否为独立接口，是则直接取api url，否则要拼接url
        api = db.session.query(Api.url, Api.request_method, Api.independent).filter(Api.id == param_apiId).first()
        if api[2] == 0:
            projectEnvironment_id = db.session.query(ProjectModule.projectEnvironment_id).join(Api).filter(Api.id == param_apiId).first()
            base_url = db.session.query(ProjectEnvironment.url).filter(ProjectEnvironment.id == projectEnvironment_id[0]).first()
            c_url = base_url[0] + api[0]
            request_method = api[1]
        else:
            c_url = api[0]
            request_method = api[1]
        dic = {'api_id': param_apiId, 'encode': '', 'id': '', 'request_body': '', 'request_param': '', 'request_header': '', 'request_method': request_method, 'title': '',
               'url': c_url, 'verify': '', 'is_assert': '', 'assert_pattern': '', 'assert_content': '', 'file_name': '', 'is_post_processor': '', 'post_processor_content': ''}
        output['data'] = dic

    return jsonify(output)


"""保存测试用例数据"""
@apiTestcase.route('/saveApiTestcase', methods=['post'])
@tokenUtil.login_required('admin_role', 'test_role')
def add_apiTestcase():
    data = request.get_json()
    param_api_id = data['api_id']
    param_encode = data['encode']
    param_encrypt_type = data['encrypt_value']
    if param_encrypt_type is None or param_encrypt_type == '':
        param_encrypt_type = 1
    param_request_body = data['request_body']
    param_request_header = data['request_header']
    param_request_method = data['request_method']
    param_title = data['title']
    param_verify = 'true' if data['verify'] is True else 'false'
    param_url = data['url']
    param_assert = 'true' if data['assert'] is True else 'false'
    param_assert_content = data['assert_content']
    param_post_processor = 'true' if data['postProcessor'] is True else 'false'
    param_post_processor_content = data['post_processor_content']
    apiTestcase1 = ApiTestcase(api_id=param_api_id, title=param_title, request_method=param_request_method, request_header=param_request_header, request_body=param_request_body
                                , encode=param_encode, encrypt_type=param_encrypt_type, verify=param_verify, url=param_url, is_assert=param_assert
                                , assert_content=param_assert_content, is_post_processor=param_post_processor
                                , post_processor_content=param_post_processor_content)
    db.session.add(apiTestcase1)
    db.session.commit()
    output = {'code': 1000, 'msg': '保存成功', 'exception': None, 'success': True, 'id': apiTestcase1.id}

    return jsonify(output)


"""保存测试用例数据"""
@apiTestcase.route('/saveApiTestcase', methods=['put'])
@tokenUtil.login_required('admin_role', 'test_role')
def edit_apiTestcase():
    data = request.get_json()
    param_api_id = data['api_id']
    param_encode = data['encode']
    param_encrypt_type = data['encrypt_value']
    if param_encrypt_type is None or param_encrypt_type == '':
        param_encrypt_type = 1
    param_id = data['id']
    param_request_body = data['request_body']
    param_request_header = data['request_header']
    param_request_method = data['request_method']
    param_title = data['title']
    param_verify = 'true' if data['verify'] is True else 'false'
    param_url = data['url']
    param_assert = 'true' if data['assert'] is True else 'false'
    param_assert_content = data['assert_content']
    param_post_processor = 'true' if data['postProcessor'] is True else 'false'
    param_post_processor_content = data['post_processor_content']

    apiTestcase1 = ApiTestcase.query.get(param_id)
    apiTestcase1.api_id = param_api_id
    apiTestcase1.title = param_title
    apiTestcase1.request_method = param_request_method
    apiTestcase1.request_header = param_request_header
    apiTestcase1.request_body = param_request_body
    apiTestcase1.encode = param_encode
    apiTestcase1.encrypt_type = param_encrypt_type
    apiTestcase1.verify = param_verify
    apiTestcase1.url = param_url
    apiTestcase1.is_assert = param_assert
    apiTestcase1.assert_content = param_assert_content
    apiTestcase1.is_post_processor = param_post_processor
    apiTestcase1.post_processor_content = param_post_processor_content
    db.session.commit()
    output = {'code': 1000, 'msg': '保存成功', 'exception': None, 'success': True}

    return jsonify(output)


# """json editor如果传{}或双引号，处理为空字符串"""
# def json_editor_format(json):
#     if json == '\"\"' or json == '{}':
#         json = ''
#     return json


"""获取上传的文件并保存"""
@apiTestcase.route('/uploadFile', methods=['post'])
@tokenUtil.login_required('admin_role', 'test_role')
def getAndSaveUploadFile():
    file = request.files['file']
    param_id = request.form.get('id')
    # 获取文件后缀，生成随机文件名
    file_name = uuid.uuid4().hex
    suffix = os.path.splitext(file.filename)[-1]
    # 检查表有无用例数据，无返回提示，有则保存文件路径
    if param_id == '':
        return errorCode.TestcaseNotSave()
    apiTestcase1 = ApiTestcase.query.get(param_id)
    if apiTestcase1.file_name == '' or apiTestcase1.file_name is None:
        apiTestcase1.file_name = str([{'realname': file_name + suffix, 'name': file.filename}])
    else:
        file_list = eval(apiTestcase1.file_name)
        file_list.append({'realname': file_name + suffix, 'name': file.filename})
        apiTestcase1.file_name = str(file_list)
    if not os.path.exists(setting.updateFiles_DIR_apiTest):
        os.mkdir(setting.updateFiles_DIR_apiTest)
    file.save(setting.updateFiles_DIR_apiTest + '/' + file_name + suffix)
    # 文件上传远程服务器
    ssh = SSH(setting.host, setting.port, setting.username, setting.password)
    ssh.upload_file(setting.updateFiles_DIR_apiTest, setting.remote_updateFiles_DIR_apiTest, file_name + suffix)
    ssh.close_connect()
    # 删除镜像本地的文件
    os.remove(setting.updateFiles_DIR_apiTest + '/' + file_name + suffix)
    db.session.commit()
    output = {'code': 1000, 'msg': '上传成功', 'exception': None, 'success': True, 'file_name': file.filename, 'real_file_name': file_name + suffix}

    return jsonify(output)


"""删除上传的文件"""
@apiTestcase.route('/deleteUploadFile', methods=['delete'])
@tokenUtil.login_required('admin_role', 'test_role')
def deleteUploadFile():
    # 从delete请求拿参数
    param_file_name = request.args.get('file')
    param_id = request.args.get('id')

    # 遍历表中记录，查找对应的文件名，并剔除
    apiTestcase1 = ApiTestcase.query.get(param_id)
    file_list = eval(apiTestcase1.file_name)
    new_file_name = ''
    # 遍历找到删掉后，跳出循环
    for i in range(len(file_list)):
        if param_file_name in file_list[i]['name']:
            new_file_name = file_list[i]['realname']
            del file_list[i]
            break
    # file_list.remove(param_file_name)
    if not file_list:
        file_list = ''
    apiTestcase1.file_name = str(file_list)
    # 删除对应路径的文件
    ssh = SSH(setting.host, setting.port, setting.username, setting.password)
    if ssh.exist_file(setting.remote_updateFiles_DIR_apiTest + '/' + new_file_name):
        ssh.delete_file(setting.remote_updateFiles_DIR_apiTest, new_file_name)
        ssh.close_connect()
        db.session.commit()
        output = {'code': 1000, 'msg': '删除成功', 'exception': None, 'success': True}
        return jsonify(output)
    else:
        return errorCode.FileDoesNotExist()


"""下载上传的文件"""
@apiTestcase.route('/downloadFile', methods=['get'])
@tokenUtil.login_required('admin_role', 'test_role')
def download_file():
    param_realname = request.args.get('file')
    path = setting.updateFiles_DIR_apiTest + '/' + param_realname

    # 把文件从远程服务器拉到镜像本地
    ssh = SSH(setting.host, setting.port, setting.username, setting.password)
    if ssh.exist_file(setting.remote_updateFiles_DIR_apiTest + '/' + param_realname):
        ssh.download_file(setting.updateFiles_DIR_apiTest, setting.remote_updateFiles_DIR_apiTest, param_realname)
        ssh.close_connect()
        if os.path.exists(path):
            mimetype = mimetypes.guess_type(path)[0]
            res = send_file(path, mimetype=mimetype, attachment_filename=param_realname, as_attachment=True)
            return res
        else:
            return errorCode.FileDoesNotExist()
    else:
        return errorCode.FileDoesNotExist()


"""调试api"""
@apiTestcase.route('/debugApi', methods=['post'])
@tokenUtil.login_required('admin_role', 'test_role')
def debugApi():
    log = Log('debugLog')
    # log_path = log.get_filepath()
    data = request.get_json()
    param_api_id = data['api_id']
    param_encode = data['encode']
    # param_request_body = data['request_body'].replace('\n', '').replace(' ', '')
    param_request_body = data['request_body'].replace('\n', '')
    param_request_file = data['request_file']
    # param_request_header = data['request_header'].replace('\n', '').replace(' ', '')
    param_request_header = data['request_header'].replace('\n', '')
    if param_request_header != '':
        param_request_header = ast.literal_eval(param_request_header)
    param_request_method = data['request_method']
    param_title = data['title']
    param_url = data['url']
    param_encrypt_type = data['encrypt_value']
    if param_encrypt_type is None or param_encrypt_type == '':
        param_encrypt_type = 1
    param_verify = 'true' if data['verify'] is True else 'false'
    param_assert = 'true' if data['assert'] is True else 'false'
    # param_assert_pattern = request.form.get('assert_pattern')
    param_assert_content = data['assert_content']
    param_is_post_processor = 'true' if data['postProcessor'] is True else 'false'
    param_post_processor_content = data['post_processor_content']
    # 获取项目环境id，给后续取环境变量
    e_id = db.session.query(ProjectModule.projectEnvironment_id).join(Api).filter(Api.id == param_api_id).first()

    data = api_test.debug_entrance(param_encrypt_type, log, e_id[0], param_title, param_url, param_request_header, param_request_method, param_request_body
                                 , param_request_file, param_encode, param_verify, param_assert, param_assert_content, param_is_post_processor
                                 , param_post_processor_content)
    del data[-1]  # 返回值最後一行會帶上測試結果的bool值，測試任務用的，所以要調試這裏要刪掉

    output = {'code': 1000, 'msg': '调试任务启动成功', 'exception': None, 'success': True, 'data': data}

    return jsonify(output)


"""获取加密下拉选项"""
@apiTestcase.route('/getEncryptOption', methods=['GET'])
@tokenUtil.login_required('admin_role', 'test_role')
def get_encrypt_option():
    encrypt_option = DataDictionary.query.filter(DataDictionary.key == 'encrypt_option').first()
    output = {'code': 1000, 'data': ast.literal_eval(encrypt_option.value), 'success': True}

    return jsonify(output)
