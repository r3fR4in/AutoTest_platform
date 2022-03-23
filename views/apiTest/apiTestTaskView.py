from flask import Blueprint, jsonify, request
from sqlalchemy import and_, distinct

# from config import scheduler  # 导入已初始化的scheduler对象

from utils.extensions import db
from models.apiTestModel import ApiTestTask
from models.apiTestModel import ApiTestDetail
from models.projectModel import Project
from models.projectModel import ProjectEnvironment
from models.apiTestModel import Api
from models.apiTestModel import ApiTestcase
import datetime
from utils import test_util, token_util

from utils.log import Log

apiTestTask = Blueprint('apiTestTask', __name__)


"""获取测试任务列表"""
@apiTestTask.route('/apiTestTaskList', methods=['get'])
@token_util.login_required()
def list_apiTestTask():
    try:
        # 从get请求获取参数
        param_currentPage = request.args.get('currentPage')
        param_pageSize = request.args.get('pageSize')
        param_projectName = request.args.get('projectName')
        param_title = request.args.get('title')

        filterList = []

        if param_projectName is not None and param_projectName != '':
            # 根据projectName找到project
            project = Project.query.filter(Project.projectName == param_projectName).first()
            if project is not None:
                filterList.append(ApiTestTask.project_id == project.id)
            else:
                output = {'code': 0, 'msg': '项目不存在', 'count': 0, 'success': False, 'errorMsg': ''}
                return jsonify(output)
        if param_title is not None and param_title != '':
            filterList.append(ApiTestTask.title.like("%" + str(param_title) + "%"))

        apiTestTasks = ApiTestTask.query.filter(*filterList).order_by(ApiTestTask.create_time.desc()).paginate(int(param_currentPage), int(param_pageSize)).items
        num = ApiTestTask.query.filter(*filterList).count()

        # 封装字典并转成json返回前端
        output = {'code': 1, 'msg': None, 'count': num, 'success': True}
        list = []
        for apiTestTask in apiTestTasks:
            p_name = apiTestTask.project.projectName
            dic = apiTestTask.to_json()
            dic['projectName'] = p_name
            # 删除字典中的project对象，否则转json会报错
            del dic['project']
            list.append(dic)
        output['data'] = list
        # test_util.execute_apitest_task(42)
    except Exception as e:
        output = {'code': 0, 'msg': '获取项目环境配置列表失败', 'count': 0, 'success': False, 'errorMsg': e}

    return jsonify(output)


"""添加测试任务"""
@apiTestTask.route('/addApiTestTask', methods=['post'])
@token_util.login_required()
def add_apiTest_Task():
    # 从post请求拿参数
    data = request.get_json()
    param_projectEnvironmentId = data['projectEnvironment_id']
    param_title = data['title']
    param_summary = data['summary']
    param_moduleSelection = data['moduleSelection']
    try:
        if param_moduleSelection == '' or param_moduleSelection is None:
            output = {'code': 0, 'msg': '未选择测试模块', 'count': 0, 'success': False}
            return jsonify(output)
        # 根据projectEnvironmentId获取projectId，添加apitest_task
        projectId = db.session.query(ProjectEnvironment.project_id).filter(ProjectEnvironment.id == param_projectEnvironmentId).first()
        apiTestTask1 = ApiTestTask(project_id=projectId[0], title=param_title, summary=param_summary, create_time=datetime.datetime.now(), status=0)
        db.session.add(apiTestTask1)
        # 遍历moduleSelection，获取apiModuleId后api和apiTestcase关联查询，再添加apitest_detail
        for moduleSelection in param_moduleSelection:
            results = db.session.query(Api, ApiTestcase).join(Api, Api.id == ApiTestcase.api_id)\
                .filter(and_(Api.apiModule_id == moduleSelection['id'], Api.status == 1)).order_by(Api.seq).all()
            for result in results:
                apiTestcase_id = result[1].to_json()['id']
                module_name = moduleSelection['module_name']
                api = result[0]
                apiTestcase = result[1]
                api_name = api.to_json()['api_name']
                testcase_name = apiTestcase.to_json()['title']
                apiTestDetail1 = ApiTestDetail(task_id=apiTestTask1.id, apiTestcase_id=apiTestcase_id, module_name=module_name, api_name=api_name, testcase_name=testcase_name, create_time=datetime.datetime.now(), status=0)
                db.session.add(apiTestDetail1)
        db.session.commit()
        output = {'code': 1, 'msg': '添加任务成功', 'success': True}
        # api_test_job()
        # 調用執行測試任務
        # log = Log('log')
        test_util.execute_apitest_task.delay(apiTestTask1.id)
    except Exception as e:
        output = {'code': 0, 'msg': '添加任务失败', 'success': False, 'errorMsg': str(e)}

    return jsonify(output)


"""删除测试任务"""
@apiTestTask.route('/deleteApiTestTask', methods=['delete'])
@token_util.login_required()
def delete_apiTest_task():
    # 从post请求拿参数
    param_id = request.args.get('id')
    try:
        # 检查任务状态是否为执行中
        apiTestTask1 = ApiTestTask.query.get(param_id)
        if apiTestTask1.status == 1:
            output = {'code': 0, 'msg': '执行中的任务不能删除', 'exception': None, 'success': False}
        else:
            # 删除测试任务
            db.session.delete(apiTestTask1)
            db.session.commit()
            output = {'code': 1, 'msg': '删除成功', 'exception': None, 'success': True}
    except Exception as e:
        db.session.rollback()
        output = {'code': 0, 'msg': '删除任务失败', 'success': False, 'errorMsg': e}

    return jsonify(output)


# """apitest定时任务"""
# def api_test_job():
#     log = Log('log')
#     log.info('开始检查任务列表')
#     # 使用上下文
#     with scheduler.app.app_context():
#         #
#         apiTestTask1 = ApiTestTask.query.filter(ApiTestTask.status == 0).order_by(ApiTestTask.create_time).first()
#         if apiTestTask1 is not None:
#             log.info('存在未执行任务，开始执行')
#             test_util.execute_apitest_task(log, apiTestTask1)
#         else:
#             log.info('无待执行任务')


"""输出测试报告"""
@apiTestTask.route('/apiTestReport', methods=['get'])
@token_util.login_required()
def api_test_report():
    # 从get请求获取参数
    param_task_id = request.args.get('task_id')
    try:
        # 获取所有测试用例
        names = db.session.query(distinct(ApiTestDetail.module_name), ApiTestDetail.api_name).filter(ApiTestDetail.task_id == param_task_id).order_by(ApiTestDetail.module_name).all()
        api_list = []
        for i in range(len(names)):
            apiTest_details = ApiTestDetail.query.filter(and_(ApiTestDetail.module_name == names[i][0], ApiTestDetail.api_name == names[i][1], ApiTestDetail.task_id == param_task_id)).all()
            api_dic = {'module_name': apiTest_details[0].module_name, 'api_name': apiTest_details[0].api_name}
            testcase_list = []
            for apiTest_detail in apiTest_details:
                try:
                    testcase_dic = {'testcase_name': apiTest_detail.testcase_name, 'output_log': eval(apiTest_detail.output_log)['log'], 'status': apiTest_detail.status}
                except Exception as e:
                    testcase_dic = {'testcase_name': apiTest_detail.testcase_name, 'output_log': str(e), 'status': apiTest_detail.status}
                testcase_list.append(testcase_dic)
            api_dic['testcase'] = testcase_list
            api_list.append(api_dic)
        # 统计每个api的测试结果
        for i in range(len(api_list)):
            all_count = len(api_list[i]['testcase'])
            pass_count = 0
            fail_count = 0
            for j in range(all_count):
                if api_list[i]['testcase'][j]['status'] == 1:
                    pass_count = pass_count + 1
                elif api_list[i]['testcase'][j]['status'] == 2:
                    fail_count = fail_count + 1
            api_list[i]['all_count'] = all_count
            api_list[i]['pass_count'] = pass_count
            api_list[i]['fail_count'] = fail_count
        # 获取统计结果
        title = db.session.query(ApiTestTask.title).filter(ApiTestTask.id == param_task_id).first()
        all_count = ApiTestDetail.query.filter(ApiTestDetail.task_id == param_task_id).count()
        pass_count = ApiTestDetail.query.filter(and_(ApiTestDetail.task_id == param_task_id, ApiTestDetail.status == 1)).count()
        fail_count = ApiTestDetail.query.filter(and_(ApiTestDetail.task_id == param_task_id, ApiTestDetail.status == 2)).count()
        output = {'code': 1, 'msg': '获取测试报告成功', 'exception': None, 'success': True, 'all_count': all_count, 'pass_count': pass_count, 'fail_count': fail_count,
                  'data': api_list, 'title': title[0]}
    except Exception as e:
        output = {'code': 0, 'msg': '获取测试报告失败', 'success': False, 'errorMsg': str(e)}

    return jsonify(output)

