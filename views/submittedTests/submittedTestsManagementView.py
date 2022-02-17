import datetime

from flask import Blueprint, jsonify, request
from utils.extensions import db
from utils import token_util, redis_util
from models.project.projectModel import Project
from models.base.dataDictionaryModel import DataDictionary
from models.submittedTests.submittedTestsModel import SubmittedTests
import ast

submittedTests = Blueprint('submittedTests', __name__)

"""获取提测申请列表"""
@submittedTests.route('/submittedTestsList', methods=['get'])
@token_util.login_required()
def list_submittedTests():
    # 从get请求获取参数
    param_currentPage = request.args.get('currentPage')
    param_pageSize = request.args.get('pageSize')
    param_projectName = request.args.get('projectName')
    try:
        # 判断param_projectName是否为空，为空代表用户未输入搜索框查询，默认显示所有数据
        if param_projectName != '':
            # 根据projectName找到project
            project = Project.query.filter(Project.projectName == param_projectName).first()
            if project is not None:
                # 根据project的id找到submittedTests
                submittedTests = SubmittedTests.query.filter(SubmittedTests.project_id == project.id).order_by(SubmittedTests.id.desc())\
                    .paginate(int(param_currentPage), int(param_pageSize)).items
                num = SubmittedTests.query.filter(SubmittedTests.project_id == project.id).count()
            else:
                output = {'code': 1, 'msg': None, 'count': 0, 'success': True, 'data': ''}
                return jsonify(output)
        else:
            submittedTests = SubmittedTests.query.order_by(SubmittedTests.id.desc()).paginate(int(param_currentPage), int(param_pageSize)).items
            num = SubmittedTests.query.count()

        # 封装字典并转成json返回前端
        output = {'code': 1, 'msg': None, 'count': num, 'success': True}
        list = []
        for submittedTest in submittedTests:
            # 获取关联的projectName，并加入字典中
            p_name = submittedTest.project.projectName
            dict = submittedTest.to_json()
            dict['projectName'] = p_name
            # 删除字典中的project对象，否则转json会报错
            del dict['project']
            list.append(dict)
        output['data'] = list
    except Exception as e:
        output = {'code': 0, 'msg': '获取项目环境配置列表失败', 'count': 0, 'success': False, 'errorMsg': e}

    return jsonify(output)


"""获取冒烟测试不通过原因选项"""
@submittedTests.route('/getReasonOption', methods=['GET'])
@token_util.login_required()
def get_reason_option():
    try:
        reason_option = DataDictionary.query.filter(DataDictionary.key == 'reason_option').first()
        output = {'code': 1, 'data': ast.literal_eval(reason_option.value), 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '获取冒烟测试不通过原因选项失败', 'success': False, 'exception': e}

    return jsonify(output)


"""保存提测申请"""
@submittedTests.route('/saveSubmittedTest', methods=['POST'])
@token_util.login_required()
def save_submittedTest():
    # 从post请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_projectName = data['projectName']
    param_submitted_test_name = data['submitted_test_name']
    param_submitted_date = datetime.datetime.strptime(data['submitted_date'], '%Y-%m-%d')
    param_submitted_test_director = data['submitted_test_director']
    param_submitted_test_detail = data['submitted_test_detail']
    param_test_director = data['test_director']
    try:
        # 根据id判断新增或编辑，id为空则是新增，否则为编辑
        if param_id == '':
            project1 = Project.query.filter(Project.projectName == param_projectName).first()
            if None is project1:
                output = {'code': 0, 'msg': '保存失败，请输入存在的项目名称', 'exception': None, 'success': False}
            else:
                project1_dict = project1.to_json()
                submittedTests1 = SubmittedTests(project_id=project1_dict['id'], submitted_test_name=param_submitted_test_name, submitted_test_detail=param_submitted_test_detail,
                                                 submitted_date=param_submitted_date, submitted_test_director=param_submitted_test_director, test_director=param_test_director,
                                                 test_status=1, smoke_testing_result=0, test_result=0)
                db.session.add(submittedTests1)
                db.session.commit()
                output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
        else:
            submittedTests1 = SubmittedTests.query.get(param_id)
            submittedTests1.submitted_test_name = param_submitted_test_name
            submittedTests1.submitted_test_detail = param_submitted_test_detail
            submittedTests1.submitted_date = param_submitted_date
            submittedTests1.submitted_test_director = param_submitted_test_director
            submittedTests1.test_director = param_test_director
            db.session.commit()
            output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '保存失败', 'exception': e.args[0], 'success': False}

    return jsonify(output)


"""删除提测申请"""
@submittedTests.route('/deleteSubmittedTest', methods=['DELETE'])
@token_util.login_required()
def delete_submittedTest():
    # 从delete请求拿参数
    param_id = request.args.get('id')
    try:
        submittedTests1 = SubmittedTests.query.get(param_id)
        db.session.delete(submittedTests1)
        db.session.commit()
        output = {'code': 1, 'msg': '删除成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '删除失败', 'exception': e, 'success': False}

    return jsonify(output)


"""保存冒烟测试结果"""
@submittedTests.route('/saveSmokeTestingResult', methods=['POST'])
@token_util.login_required()
def save_smokeTesting_result():
    # 从post请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_smoke_testing_result = int(data['smoke_testing_result'])
    param_smoke_testing_fail_reason = data['smoke_testing_fail_reason']
    try:
        if param_smoke_testing_result == 1:
            # 测试通过
            submittedTests1 = SubmittedTests.query.get(param_id)
            submittedTests1.smoke_testing_result = param_smoke_testing_result
            db.session.commit()
            output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
        else:
            # 测试不通过
            param_complete_date = datetime.datetime.strptime(data['complete_date'], '%Y-%m-%d')
            submittedTests1 = SubmittedTests.query.get(param_id)
            param_smoke_testing_fail_reason_category = param_smoke_testing_fail_reason[0]
            param_smoke_testing_fail_reason_detail = param_smoke_testing_fail_reason[1]
            submittedTests1.smoke_testing_result = param_smoke_testing_result
            submittedTests1.smoke_testing_fail_reason_category = param_smoke_testing_fail_reason_category
            submittedTests1.smoke_testing_fail_reason_detail = param_smoke_testing_fail_reason_detail
            submittedTests1.complete_date = param_complete_date
            submittedTests1.test_status = 3
            submittedTests1.test_result = 2
            db.session.commit()
            output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '保存失败', 'exception': e.args[0], 'success': False}

    return jsonify(output)


"""保存最终测试结果"""
@submittedTests.route('/saveTestResult', methods=['POST'])
@token_util.login_required()
def save_test_result():
    # 从post请求拿参数
    data = request.get_json()
    param_id = data['id']
    param_test_result = int(data['test_result'])
    param_complete_date = datetime.datetime.strptime(data['complete_date'], '%Y-%m-%d')
    try:
        submittedTests1 = SubmittedTests.query.get(param_id)
        submittedTests1.test_result = param_test_result
        submittedTests1.complete_date = param_complete_date
        submittedTests1.test_status = 2
        db.session.commit()
        output = {'code': 1, 'msg': '保存成功', 'exception': None, 'success': True}
    except Exception as e:
        output = {'code': 0, 'msg': '保存失败', 'exception': e.args[0], 'success': False}

    return jsonify(output)
