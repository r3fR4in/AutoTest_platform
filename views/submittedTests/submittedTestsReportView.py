import json

from flask import Blueprint, jsonify, request, Response

from utils.extensions import db
from utils import tokenUtil, errorCode

submittedTestsReport = Blueprint('submittedTestsReport', __name__)

"""
完成提测冒烟测试排名
报表字段：提测项目、提测负责人、提测总数、冒烟测试通过数、冒烟测试通过率
过滤：时间->项目->提测负责人
"""
@submittedTestsReport.route('/smokeTestingRankReport', methods=['GET'])
@tokenUtil.login_required('admin_role', 'test_role')
def smokeTesting_rank_report():
    # 从get请求获取参数`
    param_start_date = request.args.get('start_date')
    param_end_date = request.args.get('end_date')

    if param_start_date is None or param_end_date is None:
        return errorCode.DateCanNotNone()

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
    output = {'code': 1000, 'msg': None, 'success': True, 'data': result_list}

    return jsonify(output)


"""
项目非一次性通过原因分析
报表字段：原因分类、原因分析、出现次数、占比、总占比
"""
@submittedTestsReport.route('/smokeTestingFailReasonAnalysisReport', methods=['GET'])
@tokenUtil.login_required('admin_role', 'test_role')
def smokeTesting_fail_reason_analysis_report():
    # 从get请求获取参数`
    param_start_date = request.args.get('start_date')
    param_end_date = request.args.get('end_date')
    param_dimension = request.args.get('dimension')

    if param_start_date is None or param_end_date is None:
        return errorCode.DateCanNotNone()

    if param_dimension == '1':
        output = smokeTesting_fail_reason_analysis_report_by_project(param_start_date, param_end_date)
    elif param_dimension == '2':
        output = smokeTesting_fail_reason_analysis_report_by_all(param_start_date, param_end_date)
    else:
        return {'code': 1000, 'msg': '统计维度不能为空', 'success': False}

    # 防止jsonify修改返回数据的顺序，用以下方式来返回响应
    return Response(json.dumps(output), mimetype='application/json')


"""项目非一次性通过原因分析-按项目"""
def smokeTesting_fail_reason_analysis_report_by_project(start_date, end_date):
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
        order by project_id, smoke_testing_fail_reason_category
        """
    rets = db.session.execute(sql, {'start_date': start_date, 'end_date': end_date})
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
        where submitted_date BETWEEN '""" + start_date + """' and '""" + end_date + """' and test_status = 3
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
                list1['category_rate'] = round(float(list1['smoke_testing_fail_reason_category_num'] / list1['smoke_testing_fail_num'] * 100), 2)
    # 合并list后，按项目拆分list
    # final_list = []
    project = {}
    rowspan = 1
    pos = 0
    for i in range(0, len(result_list1)):
        if i == 0:
            project[result_list1[i]['projectName']] = []
            result_list1[i]['rowspan'] = rowspan
            project[result_list1[i]['projectName']].append(result_list1[i])
        else:
            if result_list1[i]['project_id'] == result_list1[i - 1]['project_id']:
                if result_list1[i]['smoke_testing_fail_reason_category'] == result_list1[i - 1]['smoke_testing_fail_reason_category']:
                    result_list1[i]['rowspan'] = 0
                    rowspan += 1
                    project[result_list1[i]['projectName']][pos]['rowspan'] = rowspan
                else:
                    rowspan = 1
                    pos = len(project[result_list1[i]['projectName']])
                    result_list1[i]['rowspan'] = rowspan
                project[result_list1[i]['projectName']].append(result_list1[i])
            else:
                rowspan = 1
                pos = 0
                result_list1[i]['rowspan'] = rowspan
                project[result_list1[i]['projectName']] = []
                project[result_list1[i]['projectName']].append(result_list1[i])
    # final_list.append(project)
    output = {'code': 1000, 'msg': None, 'success': True, 'data': project}

    return output


"""项目非一次性通过原因分析-按全部"""
def smokeTesting_fail_reason_analysis_report_by_all(start_date, end_date):
    sql = """
    SELECT a.smoke_testing_fail_reason_category, a.smoke_testing_fail_reason_detail, a.smoke_testing_fail_reason_detail_num, b.smoke_testing_fail_reason_category_num,
    ROUND(a.smoke_testing_fail_reason_detail_num/c.smoke_testing_fail_num*100, 2) AS detail_rate,
    ROUND(b.smoke_testing_fail_reason_category_num/c.smoke_testing_fail_num*100, 2) AS category_rate
    FROM
    (SELECT smoke_testing_fail_reason_category, smoke_testing_fail_reason_detail, count(*) AS smoke_testing_fail_reason_detail_num
    FROM submitted_tests 
    where test_status = 3 and submitted_date BETWEEN :start_date and :end_date
    GROUP BY smoke_testing_fail_reason_category, smoke_testing_fail_reason_detail
    ORDER BY smoke_testing_fail_reason_category)a,
    (SELECT smoke_testing_fail_reason_category, count(*) AS smoke_testing_fail_reason_category_num
    FROM submitted_tests
    where test_status = 3 and submitted_date BETWEEN :start_date and :end_date
    GROUP BY smoke_testing_fail_reason_category)b,
    (SELECT count(*) AS smoke_testing_fail_num FROM submitted_tests where test_status = 3 and submitted_date BETWEEN :start_date and :end_date)c
    where a.smoke_testing_fail_reason_category = b.smoke_testing_fail_reason_category
    """
    rets = db.session.execute(sql, {'start_date': start_date, 'end_date': end_date})
    rets = list(rets)
    result_list = []

    # 查询结果集格式调整为符合json的格式
    for ret in rets:
        # 取出结果集中的列明和值，将tuple类型转为list类型，再把占比的decimal类型转成保留两位小数的float类型，并添加进result_list中
        column = list(ret._fields)
        row = list(ret._data)
        row[4] = round(float(row[4]), 2)
        row[5] = round(float(row[5]), 2)
        dic = dict(zip(column, row))
        result_list.append(dic)

    # 加rowspan
    rowspan = 1
    pos = 0
    for i in range(0, len(result_list)):
        if i == 0:
            result_list[i]['rowspan'] = rowspan
        else:
            if result_list[i]['smoke_testing_fail_reason_category'] == result_list[i - 1]['smoke_testing_fail_reason_category']:
                result_list[i]['rowspan'] = 0
                rowspan += 1
                result_list[pos]['rowspan'] = rowspan
            else:
                rowspan = 1
                pos = i
                result_list[i]['rowspan'] = rowspan

    output = {'code': 1000, 'msg': None, 'success': True, 'data': {'全部项目': result_list}}

    return output
