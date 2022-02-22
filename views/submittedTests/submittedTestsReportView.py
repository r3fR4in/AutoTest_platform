import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import and_

from utils.extensions import db
from utils import token_util, redis_util
from models.project.projectModel import Project
from models.base.dataDictionaryModel import DataDictionary
from models.submittedTests.submittedTestsModel import SubmittedTests
import ast

submittedTestsReport = Blueprint('submittedTestsReport', __name__)

"""
完成提测冒烟测试排名
报表字段：提测项目、提测负责人、提测总数、冒烟测试通过数、冒烟测试通过率
过滤：时间->项目->提测负责人
"""
@submittedTestsReport.route('/smokeTestingRankReport', methods=['GET'])
@token_util.login_required()
def smokeTesting_rank_report():
    # 从get请求获取参数`
    param_start_date = request.args.get('start_date')
    param_end_date = request.args.get('end_date')
    try:
        # 用原生sql查出报表，列名project_id、项目名称、提测负责人、提测总数、冒烟测试通过数、冒烟测试通过率
        # 先查出project_id、项目名称、提测负责人、提测总数，再查冒烟测试通过数，然后两表合并，急算冒烟测试通过率
        sql = """
        select d.project_id, d.projectName as 'projectName', d.submitted_test_director as 'submitted_test_director', d.`submittedTest_num`, 
            case when e.`smokeTesting_pass_num` is null then 0 else e.`smokeTesting_pass_num` end as 'smokeTesting_pass_num', 
            case when `smokeTesting_pass_num`/`submittedTest_num`*100 is null then 0 else `smokeTesting_pass_num`/`submittedTest_num`*100 end as 'smokeTesting_pass_rate'
        from
        (SELECT a.project_id, b.projectName, a.submitted_test_director, 
            count(*) as 'submittedTest_num' 
        FROM submitted_tests a inner join project b 
        on a.project_id = b.id 
        where a.submitted_date BETWEEN :start_date and :end_date  and a.test_status != 1 
        GROUP BY a.project_id, b.projectName, a.submitted_test_director order BY a.project_id, a.submitted_test_director) d
        left join 
        (select c.project_id, c.submitted_test_director, count(*) as 'smokeTesting_pass_num' 
        from submitted_tests c 
        where c.submitted_date BETWEEN :start_date and :end_date  and c.test_status != 1 and c.smoke_testing_result = 1 
        GROUP BY c.project_id, c.submitted_test_director order BY c.project_id, c.submitted_test_director) e
        on d.project_id = e.project_id and d.submitted_test_director = e.submitted_test_director
        order by `smokeTesting_pass_rate` desc"""
        rets = db.session.execute(sql, {'start_date': param_start_date, 'end_date': param_end_date})
        rets = list(rets)
        result_list = []
        # 查询结果集格式调整为符合json的格式
        for ret in rets:
            # 取出结果集中的列明和值，将tuple类型转为list类型，再把冒烟测试通过率的decimal类型转成保留两位小数的float类型，并添加进result_list中
            column = list(ret._fields)
            row = list(ret._data)
            row[5] = round(float(row[5]), 2)
            dic = dict(zip(column, row))
            result_list.append(dic)
        output = {'code': 1, 'msg': None, 'success': True, 'data': result_list}
    except Exception as e:
        output = {'code': 0, 'msg': '查询失败', 'exception': e.args[0], 'success': False}

    return jsonify(output)


"""
项目非一次性通过原因分析
报表字段：原因分类、原因分析、出现次数、占比、总占比
"""
@submittedTestsReport.route('/smokeTestingFailReasonAnalysisReport', methods=['GET'])
@token_util.login_required()
def smokeTesting_fail_reason_analysis_report():
    # 从get请求获取参数`
    param_start_date = request.args.get('start_date')
    param_end_date = request.args.get('end_date')
    try:
        # 用原生sql，先查出主表，包含project_id,projectName,原因大类,原因小类,小类的统计数和占比
        sql = """
        select d.project_id, d.projectName, d.smoke_testing_fail_reason_category, d.smoke_testing_fail_reason_detail, 
            d.smoke_testing_fail_reason_detail_num, e.smoke_testing_fail_num, d.smoke_testing_fail_reason_detail_num/e.smoke_testing_fail_num * 100 as detail_rate
        from
        (select c.project_id, c.projectName, c.smoke_testing_fail_reason_category, c.smoke_testing_fail_reason_detail, 
            COUNT(c.smoke_testing_fail_reason_detail) as smoke_testing_fail_reason_detail_num
        from
        (select b.projectName, a.project_id, a.smoke_testing_fail_reason_category, a.smoke_testing_fail_reason_detail
        from submitted_tests a left join project b on a.project_id = b.id 
        where a.submitted_date BETWEEN :start_date and :end_date and a.test_status = 3)c
        GROUP BY c.project_id, c.projectName, c.smoke_testing_fail_reason_category, c.smoke_testing_fail_reason_detail)d,
        (select project_id, count(*) as smoke_testing_fail_num from submitted_tests 
        where submitted_date BETWEEN :start_date and :end_date and test_status = 3
        GROUP BY project_id)e
        where d.project_id = e.project_id
        order by project_id
        """
        rets = db.session.execute(sql, {'start_date': param_start_date, 'end_date': param_end_date})
        rets = list(rets)
        result_list1 = []
        # 查询结果集格式调整为符合json的格式
        for ret in rets:
            # 取出结果集中的列明和值，将tuple类型转为list类型，再把占比的decimal类型转成保留两位小数的float类型，并添加进result_list中
            column = list(ret._fields)
            row = list(ret._data)
            row[6] = round(float(row[6]), 2)
            dic = dict(zip(column, row))
            result_list1.append(dic)
        # 再用原生sql，查出原因大类的统计数
        sql = """
        select project_id, smoke_testing_fail_reason_category, count(*) as smoke_testing_fail_reason_category_num from submitted_tests 
        where submitted_date BETWEEN '""" + param_start_date + """' and '""" + param_end_date + """' and test_status = 3
        GROUP BY project_id, smoke_testing_fail_reason_category
        """
        rets = db.session.execute(sql)
        rets = list(rets)
        result_list2 = []
        for ret in rets:
            # 取出结果集中的列明和值，将tuple类型转为list类型，并添加进result_list中
            column = list(ret._fields)
            row = list(ret._data)
            dic = dict(zip(column, row))
            result_list2.append(dic)
        # 两个结果集合并并计算出大类的占比
        for list1 in result_list1:
            for list2 in result_list2:
                if list1['project_id'] == list2['project_id'] and list1['smoke_testing_fail_reason_category'] == list2['smoke_testing_fail_reason_category']:
                    # 向list1中加入list2的原因大类总数，并计算出大类占比
                    list1['smoke_testing_fail_reason_category_num'] = list2['smoke_testing_fail_reason_category_num']
                    list1['category_rate'] = float(list1['smoke_testing_fail_reason_category_num']/list1['smoke_testing_fail_num']*100)
        # 合并list后，按项目拆分list
        final_list = []
        a = 1
        project = {'project' + str(a): []}
        for i in range(0, len(result_list1)):
            if i == 0:
                project['project'+str(a)].append(result_list1[i])
            else:
                if result_list1[i]['project_id'] == result_list1[i-1]['project_id']:
                    project['project' + str(a)].append(result_list1[i])
                else:
                    a += 1
                    project['project' + str(a)] = []
                    project['project' + str(a)].append(result_list1[i])
        final_list.append(project)
        output = {'code': 1, 'msg': None, 'success': True, 'data': final_list}
    except Exception as e:
        output = {'code': 0, 'msg': '查询失败', 'exception': e.args[0], 'success': False}

    return jsonify(output)
