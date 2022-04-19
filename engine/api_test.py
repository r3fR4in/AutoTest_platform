from requests import Response

from utils.extensions import db
from models.apiTestModel import EnvironmentVariable
from models.apiTestModel import ApiTestDetail
from models.apiTestModel import ApiTestcase
from models.projectModel import ProjectModule
from models.apiTestModel import Api
from models.apiTestModel import ApiTestTask
from engine import requests
import ast
from utils.extensions import celery
from utils.log import Log

"""断言"""
def assert_util(pattern, expected, actual):
    if pattern == 'in':
        result = expected in actual
    elif pattern == 'equal':
        result = expected == actual
    elif pattern == 'not in':
        result = expected not in actual
    elif pattern == 'not equal':
        result = expected != actual
    else:
        result = 'pattern错误'

    return result


"""替换环境变量"""
def replace_environment_variable(s, model, e_id):
    start = s.find('{{')
    end = s.find('}}')
    # 从数据库获取环境变量
    environmentVariable = db.session.query(model.value).filter(model.e_id == e_id, model.name == s[start+2:end]).first()
    if environmentVariable is not None:
        s = s.replace(s[start:end+2], environmentVariable[0])

    return s


"""调试api"""
# @socketio.on('log_output', namespace='/debug_log')
def debug(log, e_id, title, url, header, method, body, files, encode, verify, is_assert, assert_content, is_post_processor, post_processor_content):
    final_result = True
    debug_log = [log.info_return_message("==============================================start==============================================")]
    # start_line = log.get_number_of_rows()
    try:
        # 設置請求頭
        debug_log.append(log.info_return_message("标题:" + title))
        if '{{' in url and '}}' in url:
            debug_log.append(log.info_return_message("url替换环境变量"))
            url = replace_environment_variable(url, EnvironmentVariable, e_id)
        debug_log.append(log.info_return_message("url:" + url))
        debug_log.append(log.info_return_message("请求方法:" + method))
        if '{{' in str(header) and '}}' in str(header):
            debug_log.append(log.info_return_message("请求头替换环境变量"))
            header = ast.literal_eval(replace_environment_variable(str(header), EnvironmentVariable, e_id))
        debug_log.append(log.info_return_message("请求头:" + str(header).replace('\'', '"')))

        if verify == 'true':
            verify = False
        else:
            verify = True

        # 替換環境變量
        if '{{' in body and '}}' in body:
            debug_log.append(log.info_return_message("请求体替换环境变量"))
            body = replace_environment_variable(body, EnvironmentVariable, e_id)
        # 判断有无文件，有则打印日志
        if files:
            files = ast.literal_eval(str(files))
            debug_log.append(log.info_return_message("文件名:" + files[0]['name'] + "，後臺文件名:" + files[0]['realname']))
        # 发送请求
        debug_log.append(log.info_return_message("请求体:" + str(body)))
        re = requests.SendRequests(method, url, header, body, files, encode, verify, log).request()

        # 判断有没有拿到响应，沒有則打印異常信息
        if type(re) is not Response:
            debug_log.append(log.error_return_message(str(re)))
            debug_log.append(log.error_return_message("获取响应失败，请检查"))
            final_result = False
            raise Exception  # 主動抛出異常，執行finally語句

        # 輸出響應數據
        debug_log.append(log.info_return_message("响应码:" + str(re.status_code)))
        response_headers = str(re.headers).replace('{\'', '{"').replace('\':', '":').replace(': \'', ': "').replace('\',', '",').replace(', \'', ', "')\
            .replace('\'}', '"}').replace('True', 'true').replace('False', 'false').replace('None', 'null')
        debug_log.append(log.info_return_message("响应头:" + response_headers))
        response = str(re.json()).replace('{\'', '{"').replace('\':', '":').replace(': \'', ': "').replace('\',', '",').replace(', \'', ', "')\
            .replace('\'}', '"}').replace('True', 'true').replace('False', 'false').replace('None', 'null')
        debug_log.append(log.info_return_message("响应内容:" + response))
        if str(re.status_code) != '200':
            final_result = False
            raise Exception  # 主動抛出異常，執行finally語句

        # 判断是否需要后置处理
        if is_post_processor == 'true':
            debug_log.append(log.info_return_message("开始后置处理"))
            dic = ast.literal_eval(post_processor_content)
            for key in dic:
                debug_log.append(log.info_return_message("获取" + dic[key]))
                json_list = dic[key].split('.')
                result = dict(re.json(), **re.headers)
                for k in json_list:
                    if '[' in k:
                        l = k.replace(']', '').split('[')
                        result = result[l[0]][int(l[1])]
                    else:
                        result = result[k]
                debug_log.append(log.info_return_message("成功获取值" + str(result)))
                # 检查环境变量表有没有重复数据，有则更新，无则新增
                ev = EnvironmentVariable.query.filter(EnvironmentVariable.e_id == e_id, EnvironmentVariable.name == key).first()
                if ev is None:
                    ev1 = EnvironmentVariable(e_id=e_id, name=key, value=result)
                    db.session.add(ev1)
                    db.session.commit()
                else:
                    ev.name = key
                    ev.value = result
                    db.session.commit()
                debug_log.append(log.info_return_message("已更新环境变量" + str(key)))

        # 判断是否需要断言
        if is_assert == 'true':
            if '{{' in assert_content and '}}' in assert_content:
                debug_log.append(log.info_return_message("断言替换环境变量"))
                assert_content = replace_environment_variable(assert_content, EnvironmentVariable, e_id)
            assert_list = ast.literal_eval(assert_content)
            # 遍历断言列表
            for assert_dict in assert_list:
                debug_log.append(log.info_return_message("断言模式:" + assert_dict['pattern']))
                debug_log.append(log.info_return_message("断言内容:" + assert_dict['content']))
                assert_result = assert_util(assert_dict['pattern'], assert_dict['content'], str(re.json()))
                if assert_result:
                    debug_log.append(log.info_return_message("断言结果:通过"))
                elif not assert_result:
                    debug_log.append(log.error_return_message("断言结果:失败"))
                    final_result = False
                else:
                    debug_log.append(log.error_return_message("断言结果:" + assert_result))
    except Exception as e:
        final_result = False
        if str(e) != '':
            debug_log.append(log.error_return_message(str(e)))
    finally:
        # 輸出最終結果并返回日志數據
        if final_result is True:
            debug_log.append(log.info_return_message("最终测试结果:通过"))
        else:
            debug_log.append(log.error_return_message("最终测试结果:失败"))
        log.info("==============================================end==============================================")

        # end_line = log.get_number_of_rows() + 1
        # # 根據開始結束行數，讀取返回日志文件指定行數的日志
        # debugLog = log.get_log(start_line, end_line)
        # debugLog.append(final_result)
        debug_log.append(final_result)

    return debug_log


"""执行测试任务"""
@celery.task()
def execute_apitest_task(task_id):
    log = Log('log')
    # celery传参不能传实例，所以传任务id进来，再用任务id查询对应实例
    apiTestTask = ApiTestTask.query.filter(ApiTestTask.id == task_id).first()
    try:
        apitest_details = ApiTestDetail.query.filter(ApiTestDetail.task_id == task_id).order_by(ApiTestDetail.id).all()
        if apitest_details is not None:
            # 遍历apitest_details，获取apitestcase，传入debug中
            for apitest_detail in apitest_details:
                log.info("模块套件:" + '' if apitest_detail.module_name is None or apitest_detail.module_name == '' else apitest_detail.module_name)
                log.info("api:" + '' if apitest_detail.api_name is None or apitest_detail.api_name == '' else apitest_detail.api_name)
                log.info("用例标题:" + '' if apitest_detail.testcase_name is None or apitest_detail.testcase_name == '' else apitest_detail.testcase_name)
                api_testcase1 = ApiTestcase.query.get(apitest_detail.apiTestcase_id)
                if api_testcase1 is not None:
                    try:
                        e_id = db.session.query(ProjectModule.projectEnvironment_id).join(Api).filter(Api.id == api_testcase1.api_id).first()
                        request_header = api_testcase1.request_header.replace('\n', '').replace(' ', '')
                        request_body = api_testcase1.request_body.replace('\n', '').replace(' ', '')
                        # request_param = api_testcase1.request_param.replace('\n', '').replace(' ', '')
                        if request_header != '':
                            request_header = ast.literal_eval(request_header)
                        debug_log = debug(log, e_id[0], api_testcase1.title, api_testcase1.url, request_header, api_testcase1.request_method, request_body, api_testcase1.file_name
                                          , api_testcase1.encode, api_testcase1.verify, api_testcase1.is_assert, api_testcase1.assert_content, api_testcase1.is_post_processor
                                          , api_testcase1.post_processor_content)
                        if debug_log[-1] is True:
                            apitest_detail.status = 1
                        else:
                            apitest_detail.status = 2
                        del debug_log[-1]
                        apitest_detail.output_log = str({"log": debug_log})
                        db.session.commit()
                    except Exception as e:
                        log.error(e)
                        apitest_detail.output_log = str(e)
                        apitest_detail.status = 2
                        db.session.commit()
                        pass
                else:
                    # 如果没有api_testcase，返回相应异常处理
                    log.info("找不到对应的用例，执行失败")
                    apitest_detail.output_log = '找不到对应的用例，执行失败'
                    apitest_detail.status = 2
                    db.session.commit()
            apiTestTask.status = 2
            db.session.commit()
        else:
            # 如果没有apitest_detail，状态改为执行失败
            apiTestTask.status = 3
            db.session.commit()
    except Exception as e:
        log.error(e)
        apiTestTask.status = 3
        db.session.commit()

