import datetime

from flask import Blueprint, jsonify, request, send_file, after_this_request
from sqlalchemy import or_

from utils.extensions import db
from utils import tokenUtil, errorCode
from models.projectModel import Project
from models.baseModel import DataDictionary, UserProject
from models.submittedTestsModel import SubmittedTests
from views.base import messageView
from config import setting
import ast
import uuid
import os
import mimetypes
import traceback

from utils.log import Log
from utils.sshConnect import SSH

log = Log('log')

submittedTests = Blueprint('submittedTests', __name__)

"""获取提测申请列表"""
@submittedTests.route('/submittedTestsList', methods=['get'])
@tokenUtil.login_required()
def list_submittedTests():
    # 从get请求获取参数
    param_currentPage = request.args.get('currentPage')
    param_pageSize = request.args.get('pageSize')
    param_projectName = request.args.get('projectName')
    param_test_status = request.args.get('test_status')
    param_smoke_testing_result = request.args.get('smoke_testing_result')
    param_test_result = request.args.get('test_result')
    param_start_date = request.args.get('start_date')
    param_end_date = request.args.get('end_date')

    filterList = []

    # 解析token獲取user_id和role
    token = request.headers["Authorization"]
    user = tokenUtil.verify_token(token)
    if user['role'] == 'dev_role':
        userProjects = UserProject.query.filter(UserProject.user_id == user['id']).all()
        list = []
        for userProject in userProjects:
            dic = userProject.to_json()
            list.append(dic['project_id'])
        filterList.append(SubmittedTests.project_id.in_(list))
    if param_projectName is not None and param_projectName != '':
        # 根据projectName找到project
        project = Project.query.filter(Project.projectName == param_projectName).first()
        if project is not None:
            filterList.append(SubmittedTests.project_id == project.id)
        else:
            return errorCode.ProjectDoesNotExist()
    if param_test_status is not None and param_test_status != '':
        filterList.append(SubmittedTests.test_status == int(param_test_status))
    if param_smoke_testing_result is not None and param_smoke_testing_result != '':
        filterList.append(SubmittedTests.smoke_testing_result == int(param_smoke_testing_result))
    if param_test_result is not None and param_test_result != '':
        filterList.append(SubmittedTests.test_result == int(param_test_result))
    if param_start_date is not None and param_start_date != '' and param_end_date is not None and param_end_date != '':
        filterList.append(SubmittedTests.submitted_date >= param_start_date)
        filterList.append(SubmittedTests.submitted_date <= param_end_date)

    submittedTests = SubmittedTests.query.filter(*filterList).order_by(SubmittedTests.id.desc()).paginate(int(param_currentPage), int(param_pageSize)).items
    num = SubmittedTests.query.filter(*filterList).count()

    # 封装字典并转成json返回前端
    output = {'code': 1000, 'msg': None, 'count': num, 'success': True}
    list = []
    for submittedTest in submittedTests:
        # 获取关联的projectName，并加入字典中
        p_name = submittedTest.project.projectName
        dict = submittedTest.to_json()
        dict['projectName'] = p_name
        # 删除字典中的project对象，否则转json会报错
        del dict['project']
        # 将fix_bug_director_id从str转成list
        if dict['fix_bug_director_id'] != '' and dict['fix_bug_director_id'] is not None:
            dict['fix_bug_director_id'] = ast.literal_eval(dict['fix_bug_director_id'])
        # 将文件名从字符串转成列表
        if dict['file_name'] != '':
            if dict['file_name'] is None:
                dict['file_name'] = []
            else:
                file_list = eval(dict['file_name'])
                file_name = []
                for file in file_list:
                    file_name.append({'name': file['name'], 'realname': file['realname']})
                dict['file_name'] = file_name
        list.append(dict)
    output['data'] = list

    return jsonify(output)


"""获取冒烟测试不通过原因选项"""
@submittedTests.route('/getReasonOption', methods=['GET'])
@tokenUtil.login_required()
def get_reason_option():
    reason_option = DataDictionary.query.filter(DataDictionary.key == 'reason_option').first()
    output = {'code': 1000, 'data': ast.literal_eval(reason_option.value), 'success': True}

    return jsonify(output)


"""保存提测申请"""
@submittedTests.route('/saveSubmittedTest', methods=['POST'])
@tokenUtil.login_required()
def add_submittedTest():
    # 从post请求拿参数
    data = request.get_json()
    param_projectName = data['projectName']
    param_submitted_test_name = data['submitted_test_name']
    param_submitted_date = datetime.datetime.strptime(data['submitted_date'], '%Y-%m-%d')
    param_test_date = datetime.datetime.strptime(data['test_date'], '%Y-%m-%d')
    if data['online_date'] == '' or data['online_date'] is None:
        param_online_date = None
    else:
        param_online_date = datetime.datetime.strptime(data['online_date'], '%Y-%m-%d')
    # param_online_date = data['online_date'] if data['online_date'] == '' or data['online_date'] is None else datetime.datetime.strptime(data['online_date'], '%Y-%m-%d')
    param_submitted_test_director_id = data['submitted_test_director_id']
    param_submitted_test_director = data['submitted_test_director']
    param_fix_bug_director_id = data['fix_bug_director_id']
    param_fix_bug_director = data['fix_bug_director']
    param_self_test_report_url = data['self_test_report_url']
    param_test_url = data['test_url']
    param_test_scope = data['test_scope']
    param_influence_scope = data['influence_scope']
    param_points_for_attention = data['points_for_attention']
    param_config_url = data['config_url']
    param_script_url = data['script_url']
    param_compatibility_desc = data['compatibility_desc']
    param_test_director_id = data['test_director_id']
    if param_test_director_id == '':
        param_test_director_id = None
    param_test_director = data['test_director']
    param_file_name = data['file_name']

    project1 = Project.query.filter(Project.projectName == param_projectName).first()
    if None is project1:
        return errorCode.ProjectDoesNotExist()
    else:
        project1_dict = project1.to_json()
        submittedTests1 = SubmittedTests(project_id=project1_dict['id'], submitted_test_name=param_submitted_test_name,
                                         submitted_date=param_submitted_date, test_date=param_test_date, online_date=param_online_date, fix_bug_director=param_fix_bug_director,
                                         self_test_report_url=param_self_test_report_url, test_url=param_test_url, test_scope=param_test_scope, influence_scope=param_influence_scope,
                                         points_for_attention=param_points_for_attention, config_url=param_config_url, script_url=param_script_url, compatibility_desc=param_compatibility_desc,
                                         submitted_test_director=param_submitted_test_director, test_director=param_test_director, test_status=1, smoke_testing_result=0, test_result=0,
                                         file_name=str(param_file_name), submitted_test_director_id=param_submitted_test_director_id, fix_bug_director_id=str(param_fix_bug_director_id),
                                         test_director_id=param_test_director_id)
        db.session.add(submittedTests1)
        db.session.commit()

        # 添加消息
        messageView.add_submitted_test_message(param_test_director_id, param_projectName, param_submitted_test_name, param_submitted_test_director)

        output = {'code': 1000, 'msg': '保存成功', 'exception': None, 'success': True}

    return jsonify(output)


"""保存提测申请"""
@submittedTests.route('/saveSubmittedTest', methods=['put'])
@tokenUtil.login_required()
def edit_submittedTest():
    # 从put请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_submitted_test_name = data['submitted_test_name']
    param_submitted_date = datetime.datetime.strptime(data['submitted_date'], '%Y-%m-%d')
    param_test_date = datetime.datetime.strptime(data['test_date'], '%Y-%m-%d')
    if data['online_date'] == '' or data['online_date'] is None:
        param_online_date = None
    else:
        param_online_date = datetime.datetime.strptime(data['online_date'], '%Y-%m-%d')
    # param_online_date = data['online_date'] if data['online_date'] == '' or data['online_date'] is None else datetime.datetime.strptime(data['online_date'], '%Y-%m-%d')
    param_submitted_test_director_id = data['submitted_test_director_id']
    param_submitted_test_director = data['submitted_test_director']
    param_fix_bug_director_id = data['fix_bug_director_id']
    param_fix_bug_director = data['fix_bug_director']
    param_self_test_report_url = data['self_test_report_url']
    param_test_url = data['test_url']
    param_test_scope = data['test_scope']
    param_influence_scope = data['influence_scope']
    param_points_for_attention = data['points_for_attention']
    param_config_url = data['config_url']
    param_script_url = data['script_url']
    param_compatibility_desc = data['compatibility_desc']
    param_test_director_id = data['test_director_id']
    param_test_director = data['test_director']

    if not param_id:
        return errorCode.ValError()

    submittedTests1 = SubmittedTests.query.get(param_id)
    if submittedTests1.test_director_id != param_test_director_id:
        project = Project.query.get(submittedTests1.project_id)
        messageView.edit_submitted_test_message(param_test_director_id, project.projectName, param_submitted_test_name, param_submitted_test_director)
    submittedTests1.submitted_test_name = param_submitted_test_name
    submittedTests1.submitted_date = param_submitted_date
    submittedTests1.test_date = param_test_date
    submittedTests1.online_date = param_online_date
    submittedTests1.submitted_test_director_id = param_submitted_test_director_id
    submittedTests1.submitted_test_director = param_submitted_test_director
    submittedTests1.fix_bug_director_id = str(param_fix_bug_director_id)
    submittedTests1.fix_bug_director = param_fix_bug_director
    submittedTests1.self_test_report_url = param_self_test_report_url
    submittedTests1.test_url = param_test_url
    submittedTests1.test_scope = param_test_scope
    submittedTests1.influence_scope = param_influence_scope
    submittedTests1.points_for_attention = param_points_for_attention
    submittedTests1.config_url = param_config_url
    submittedTests1.script_url = param_script_url
    submittedTests1.compatibility_desc = param_compatibility_desc
    submittedTests1.test_director_id = param_test_director_id
    submittedTests1.test_director = param_test_director
    db.session.commit()
    output = {'code': 1000, 'msg': '保存成功', 'exception': None, 'success': True}

    return jsonify(output)


"""获取上传的文件并保存"""
@submittedTests.route('/uploadFile', methods=['post'])
@tokenUtil.login_required()
def get_and_save_upload_files():
    file = request.files['file']
    param_id = request.form.get('id')

    # 获取文件后缀，生成随机文件名
    file_name = uuid.uuid4().hex
    suffix = os.path.splitext(file.filename)[-1]
    # 通过id检查是新增还是编辑
    if param_id == '':
        # 新增：保存文件，并将新旧名字传回给前端
        if not os.path.exists(setting.updateFiles_DIR_submittedTests):
            os.mkdir(setting.updateFiles_DIR_submittedTests)
        file.save(setting.updateFiles_DIR_submittedTests + '/' + file_name + suffix)
        # 文件上传远程服务器
        ssh = SSH(setting.host, setting.port, setting.username, setting.password)
        ssh.upload_file(setting.updateFiles_DIR_submittedTests, setting.remote_updateFiles_DIR_submittedTests, file_name + suffix)
        ssh.close_connect()
        # 删除镜像本地的文件
        os.remove(setting.updateFiles_DIR_submittedTests + '/' + file_name + suffix)
        output = {'code': 1, 'msg': '上传成功', 'exception': None, 'success': True, 'file_name': file.filename, 'real_file_name': file_name + suffix}
    else:
        # 编辑：保存文件，同时更新表字段值
        submittedTests1 = SubmittedTests.query.get(param_id)
        if submittedTests1.file_name == '' or submittedTests1.file_name is None:
            submittedTests1.file_name = str([{'realname': file_name + suffix, 'name': file.filename}])
        else:
            file_list = eval(submittedTests1.file_name)
            file_list.append({'realname': file_name + suffix, 'name': file.filename})
            submittedTests1.file_name = str(file_list)
        file.save(setting.updateFiles_DIR_submittedTests + '/' + file_name + suffix)
        # 文件上传远程服务器
        ssh = SSH(setting.host, setting.port, setting.username, setting.password)
        ssh.upload_file(setting.updateFiles_DIR_submittedTests, setting.remote_updateFiles_DIR_submittedTests, file_name + suffix)
        ssh.close_connect()
        # 删除镜像本地的文件
        os.remove(setting.updateFiles_DIR_submittedTests + '/' + file_name + suffix)
        db.session.commit()
        output = {'code': 1, 'msg': '上传成功', 'exception': None, 'success': True, 'file_name': file.filename, 'real_file_name': file_name + suffix}

    return jsonify(output)


"""删除上传的文件"""
@submittedTests.route('/deleteUploadFile', methods=['delete'])
@tokenUtil.login_required()
def delete_upload_file():
    # 从delete请求拿参数
    param_file_realname = request.args.get('file')
    param_id = request.args.get('id')

    # 通过id检查是新增还是编辑
    if param_id != '':
        # 编辑：删除后台文件，且更新表字段值
        # 新增：直接删除后台文件
        submittedTests1 = SubmittedTests.query.get(param_id)
        file_list = eval(submittedTests1.file_name)
        # 遍历找到删掉后，跳出循环
        for i in range(len(file_list)):
            if param_file_realname in file_list[i]['realname']:
                del file_list[i]
                break
        if not file_list:
            file_list = ''
        submittedTests1.file_name = str(file_list)
    ssh = SSH(setting.host, setting.port, setting.username, setting.password)
    if ssh.exist_file(setting.remote_updateFiles_DIR_submittedTests + '/' + param_file_realname):
        ssh.delete_file(setting.remote_updateFiles_DIR_submittedTests, param_file_realname)
        ssh.close_connect()
        db.session.commit()
        output = {'code': 1, 'msg': '删除成功', 'exception': None, 'success': True}
    else:
        return errorCode.FileDoesNotExist()

    return jsonify(output)


"""下载上传的文件"""
@submittedTests.route('/downloadFile', methods=['get'])
@tokenUtil.login_required()
def download_file():
    param_realname = request.args.get('file')
    path = setting.updateFiles_DIR_submittedTests + '/' + param_realname

    # 把文件从远程服务器拉到镜像本地
    ssh = SSH(setting.host, setting.port, setting.username, setting.password)
    if ssh.exist_file(setting.remote_updateFiles_DIR_submittedTests + '/' + param_realname):
        ssh.download_file(setting.updateFiles_DIR_submittedTests, setting.remote_updateFiles_DIR_submittedTests, param_realname)
        ssh.close_connect()
        if os.path.exists(path):
            mimetype = mimetypes.guess_type(path)[0]
            res = send_file(path, mimetype=mimetype, attachment_filename=param_realname, as_attachment=True)
            return res
        else:
            return errorCode.FileDoesNotExist()
    else:
        return errorCode.FileDoesNotExist()


"""删除提测申请"""
@submittedTests.route('/deleteSubmittedTest', methods=['DELETE'])
@tokenUtil.login_required('admin_role', 'test_role')
def delete_submittedTest():
    # 从delete请求拿参数
    param_id = request.args.get('id')
    if not param_id:
        return errorCode.ValError()
    submittedTests1 = SubmittedTests.query.get(param_id)
    # 删除文件
    if submittedTests1.file_name is not None and submittedTests1.file_name != '':
        file_list = eval(submittedTests1.file_name)
        for i in range(len(file_list)):
            # 删除对应路径的文件
            path = setting.updateFiles_DIR_submittedTests + '/' + file_list[i]['realname']
            if os.path.exists(path):
                os.remove(path)
    # 删除数据
    db.session.delete(submittedTests1)
    db.session.commit()
    output = {'code': 1, 'msg': '删除成功', 'exception': None, 'success': True}

    return jsonify(output)


"""保存冒烟测试结果"""
@submittedTests.route('/saveSmokeTestingResult', methods=['put'])
@tokenUtil.login_required('admin_role', 'test_role')
def save_smokeTesting_result():
    # 从put请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_smoke_testing_result = int(data['smoke_testing_result'])
    param_smoke_testing_fail_reason = data['smoke_testing_fail_reason']
    if not param_id:
        return errorCode.ValError()

    submittedTests1 = SubmittedTests.query.get(param_id)
    if param_smoke_testing_result == 1:
        # 测试通过
        submittedTests1.smoke_testing_result = param_smoke_testing_result
        db.session.commit()
    else:
        # 测试不通过
        param_complete_date = datetime.datetime.strptime(data['complete_date'], '%Y-%m-%d')
        param_smoke_testing_fail_reason_category = param_smoke_testing_fail_reason[0]
        param_smoke_testing_fail_reason_detail = param_smoke_testing_fail_reason[1]
        submittedTests1.smoke_testing_result = param_smoke_testing_result
        submittedTests1.smoke_testing_fail_reason_category = param_smoke_testing_fail_reason_category
        submittedTests1.smoke_testing_fail_reason_detail = param_smoke_testing_fail_reason_detail
        submittedTests1.complete_date = param_complete_date
        submittedTests1.test_status = 3
        submittedTests1.test_result = 2
        db.session.commit()

    project = Project.query.get(submittedTests1.project_id)
    messageView.smoke_test_finish_message(submittedTests1.submitted_test_director_id, project.projectName, submittedTests1.submitted_test_name, param_smoke_testing_result)

    output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}

    return jsonify(output)


"""保存最终测试结果"""
@submittedTests.route('/saveTestResult', methods=['put'])
@tokenUtil.login_required('admin_role', 'test_role')
def save_test_result():
    # 从put请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_test_result = int(data['test_result'])
    param_complete_date = datetime.datetime.strptime(data['complete_date'], '%Y-%m-%d')
    if not param_id:
        return errorCode.ValError()

    submittedTests1 = SubmittedTests.query.get(param_id)
    submittedTests1.test_result = param_test_result
    submittedTests1.complete_date = param_complete_date
    submittedTests1.test_status = 2
    db.session.commit()

    project = Project.query.get(submittedTests1.project_id)
    messageView.test_finish_message(submittedTests1.submitted_test_director_id, project.projectName, submittedTests1.submitted_test_name, param_test_result)

    output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}

    return jsonify(output)


"""获取下拉框选项"""
@submittedTests.route('/getSubmittedTestOptions', methods=['get'])
@tokenUtil.login_required()
def get_submittedTest_options():
    datas = DataDictionary.query.filter(or_(DataDictionary.key == 'test_status_option', DataDictionary.key == 'smoke_testing_result_option', DataDictionary.key == 'test_result_option')).all()
    options_dic = {}
    for d in datas:
        dic = d.to_json()
        options_dic[dic['key']] = ast.literal_eval(dic['value'])
    output = {'code': 1, 'data': options_dic, 'exception': None, 'success': True}

    return jsonify(output)
