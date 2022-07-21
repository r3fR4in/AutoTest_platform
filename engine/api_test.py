from requests import Response

from utils.extensions import db
from models.apiTestModel import EnvironmentVariable
from models.apiTestModel import ApiTestDetail
from models.apiTestModel import ApiTestcase
from models.projectModel import ProjectModule
from models.apiTestModel import Api
from models.apiTestModel import ApiTestTask
from engine import send_requests
import ast
from utils.extensions import celery
from utils.log import Log
from utils import encryptUtil
from utils import errorCode
import uuid
import functools
import json
from engine import funcUtil

"""断言"""
def assert_util(pattern, key, expected, response):
    # 根据key获取需要断言的内容
    if key != '':
        response = dict(response)
        json_list = key.split('.')
        for k in json_list:
            if '[' in k:
                l = k.replace(']', '').split('[')
                response = response[l[0]][int(l[1])]
            else:
                response = response[k]
    response = str(response)

    if pattern == 'in':
        result = expected in response
    elif pattern == 'equal':
        result = expected == response
    elif pattern == 'not in':
        result = expected not in response
    elif pattern == 'not equal':
        result = expected != response
    else:
        result = 'pattern错误'

    return result


"""替换环境变量"""
def replace_environment_variable(s, model, e_id):
    try:
        start = s.find('{{')
        while start > 0:
            s_temp = s[start:]
            end = s_temp.find('}}')
            environmentVariable = db.session.query(model.value).filter(model.e_id == e_id, model.name == s_temp[2:end]).first()
            if environmentVariable is not None:
                s = s.replace(s[start:start + end + 2], str(environmentVariable[0]), 1)
            else:
                raise errorCode.ReplaceEVError()
            start = s.find('{{')

        return s
    except Exception as e:
        log = Log('log')
        log.error(e)
        raise errorCode.ReplaceEVError()


"""装饰器用于替换环境变量"""
def replace_ev_and_func():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_args = list(args)
            for i in range(0, len(new_args)):
                if '{{' in str(new_args[i]) and '}}' in str(new_args[i]):
                    new_args[i] = replace_environment_variable(str(new_args[i]), EnvironmentVariable, new_args[1]).replace('\'', '"')  # new_args[1]指e_id
                if '${' in str(new_args[i]):
                    new_args[i] = funcUtil.replace_func(str(new_args[i]))

            return func(*tuple(new_args), **kwargs)

        return wrapper

    return decorator


"""调试api入口"""
def debug_entrance(encrypt_type, log, e_id, title, url, header, method, body, files, encode, verify, is_assert, assert_content, is_post_processor, post_processor_content):
    if encrypt_type == 1:
        return normal_debug(log, e_id, title, url, header, method, body, files, encode, verify, is_assert, assert_content, is_post_processor, post_processor_content)
    elif encrypt_type == 2:
        return buddy_encrypt_debug(log, e_id, title, url, header, method, body, files, encode, verify, is_assert, assert_content, is_post_processor, post_processor_content)
    else:
        return [log.error_return_message('加密模式错误，encrypt_type:' + encrypt_type)]


"""不加密调试api"""
@replace_ev_and_func()
def normal_debug(log, e_id, title, url, header, method, body, files, encode, verify, is_assert, assert_content, is_post_processor, post_processor_content):
    final_result = True
    debug_log = [log.info_return_message("==============================================start==============================================")]
    try:
        # 設置請求頭
        debug_log.append(log.info_return_message("标题:" + title))
        debug_log.append(log.info_return_message("url:" + url))
        debug_log.append(log.info_return_message("请求方法:" + method))
        header = ast.literal_eval(str(header))  # 从str转回dict
        log.info_return_message("请求头:" + str(header).replace('\'', '"'))
        debug_log.append(log.info_return_message("请求头:"))
        debug_log.append(header)

        if verify == 'true':
            verify = False
        else:
            verify = True

        # 判断有无文件，有则打印日志
        if files:
            files = ast.literal_eval(str(files))
            debug_log.append(log.info_return_message("文件名:" + files[0]['name'] + "，後臺文件名:" + files[0]['realname']))
        # 发送请求
        log.info_return_message("请求体:" + str(body).replace('\'', '"'))
        debug_log.append(log.info_return_message("请求体:"))
        debug_log.append(json.loads(str(body).replace('\'', '"')))
        re = send_requests.SendRequests(method, url, header, body, files, encode, verify, log).request()

        # 判断有没有拿到响应，沒有則打印異常信息
        if type(re) is not Response:
            debug_log.append(log.error_return_message(str(re)))
            debug_log.append(log.error_return_message("获取响应失败，请检查"))
            final_result = False
            raise Exception  # 主動抛出異常，執行finally語句

        # 輸出響應數據
        debug_log.append(log.info_return_message("响应码:" + str(re.status_code)))
        # response_headers = str(re.headers).replace('{\'', '{"').replace('\':', '":').replace(': \'', ': "').replace('\',', '",').replace(', \'', ', "')\
        #     .replace('\'}', '"}').replace('True', 'true').replace('False', 'false').replace('None', 'null').replace('[\'', '["').replace('\']', '"]')
        response_headers = str(re.headers)
        log.info_return_message("响应头:" + response_headers)
        debug_log.append(log.info_return_message("响应头"))
        debug_log.append(dict(re.headers))
        try:
            response = str(re.json())
            log.info_return_message("响应内容:" + response)
            debug_log.append(log.info_return_message("响应内容"))
            debug_log.append(re.json())
        except:
            response = re.text
            log.info_return_message("响应内容:" + response)
            debug_log.append(log.info_return_message("响应内容"))
            debug_log.append(re.text)
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
                    ev1 = EnvironmentVariable(e_id=e_id, name=key, value=str(result))
                    db.session.add(ev1)
                    db.session.commit()
                else:
                    ev.name = key
                    ev.value = str(result)
                    db.session.commit()
                debug_log.append(log.info_return_message("已更新环境变量" + str(key)))

        # 判断是否需要断言
        if is_assert == 'true':
            assert_list = ast.literal_eval(assert_content)
            # 遍历断言列表
            for assert_dict in assert_list:
                debug_log.append(log.info_return_message("断言模式:" + assert_dict['pattern']))
                debug_log.append(log.info_return_message("断言内容:" + assert_dict['content']))
                assert_result = assert_util(assert_dict['pattern'], assert_dict['key'], assert_dict['content'], re.json())
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

        debug_log.append(final_result)

    return debug_log


"""buddy加密调试api"""
@replace_ev_and_func()
def buddy_encrypt_debug(log, e_id, title, url, header, method, body, files, encode, verify, is_assert, assert_content, is_post_processor, post_processor_content):
    final_result = True
    debug_log = [log.info_return_message("==============================================start==============================================")]
    try:
        # 設置請求頭
        debug_log.append(log.info_return_message("标题:" + title))
        debug_log.append(log.info_return_message("url:" + url))
        debug_log.append(log.info_return_message("请求方法:" + method))
        header = ast.literal_eval(str(header))  # 从str转回dict
        log.info_return_message("请求头:" + str(header).replace('\'', '"'))
        debug_log.append(log.info_return_message("请求头:"))
        debug_log.append(header)
        debug_log.append(log.info_return_message("提醒:header不传versionCode，response就不会加密"))

        if verify == 'true':
            verify = False
        else:
            verify = True

        # 加密，获取rsaKey和uniqueId
        log.info_return_message("加密前请求体:" + str(body).replace('\'', '"'))
        debug_log.append(log.info_return_message("加密前请求体:"))
        debug_log.append(json.loads(str(body).replace('\'', '"')))
        debug_log.append(log.info_return_message("开始加密处理，获取rsaKey和uniqueId"))
        secretKey_api = 'http://172.30.22.139/crm_api/crm-portal-server/n/buddy/secretKey?language=zh-TW'
        secretKey_header = {
            'Content-Type': 'application/json'
        }
        secretKey_res = send_requests.SendRequests('GET', secretKey_api, secretKey_header, '', '', 'utf-8', '', log).request()
        secretKey_res_json = secretKey_res.json()
        rsaKey = '-----BEGIN RSA PRIVATE KEY-----\n' + secretKey_res_json['data']['rsaKey'] + '\n-----END RSA PRIVATE KEY-----'
        uniqueId = secretKey_res_json['data']['uniqueId']
        debug_log.append(log.info_return_message("rsaKey:" + rsaKey))
        debug_log.append(log.info_return_message("uniqueId:" + uniqueId))
        # 生成16位随机数randomKey
        randomKey = str(uuid.uuid4().int >> 64)[0:16]
        debug_log.append(log.info_return_message("生成16位随机数randomKey:" + randomKey))
        # RSA加密randomKey得到secretKey
        secretKey = encryptUtil.encrypt_by_rsa(randomKey, rsaKey)
        debug_log.append(log.info_return_message("RSA加密randomKey得到secretKey:" + secretKey))
        debug_log.append(log.info_return_message("开始对请求体AES加密"))
        iv = 'tdrdadq59tbss5Y5'
        debug_log.append(log.info_return_message("偏移量iv:" + iv))
        encrypt_api_body = encryptUtil.encrypt_by_aes(str(body), randomKey.encode('utf-8'), iv.encode('utf-8'))
        body = {
            'encryptData': encrypt_api_body,
            'secretKey': secretKey,
            'uniqueId': uniqueId
        }
        log.info_return_message("加密后请求体:" + str(body).replace('\'', '"'))
        debug_log.append(log.info_return_message("加密后请求体:"))
        debug_log.append(json.loads(str(body).replace('\'', '"')))

        # 判断有无文件，有则打印日志
        if files:
            files = ast.literal_eval(str(files))
            debug_log.append(log.info_return_message("文件名:" + files[0]['name'] + "，后台文件名:" + files[0]['realname']))
        # 发送请求
        re = send_requests.SendRequests(method, url, header, body, files, encode, verify, log).request()

        # 判断有没有拿到响应，没有则打印异常信息
        if type(re) is not Response:
            debug_log.append(log.error_return_message(str(re)))
            debug_log.append(log.error_return_message("获取响应失败，请检查"))
            final_result = False
            raise Exception  # 主動抛出異常，執行finally語句

        # 输出响应数据
        debug_log.append(log.info_return_message("响应码:" + str(re.status_code)))
        # response_headers = str(re.headers).replace('{\'', '{"').replace('\':', '":').replace(': \'', ': "').replace('\',', '",').replace(', \'', ', "')\
        #     .replace('\'}', '"}').replace('True', 'true').replace('False', 'false').replace('None', 'null').replace('[\'', '["').replace('\']', '"]')
        # debug_log.append(log.info_return_message("响应头:" + response_headers))
        response_headers = str(re.headers)
        log.info_return_message("响应头:" + response_headers)
        debug_log.append(log.info_return_message("响应头"))
        debug_log.append(dict(re.headers))
        # 响应数据解密
        if 'versionCode' in header:
            debug_log.append(log.info_return_message("解密前响应内容:" + str(re.text)))
            dec_res = encryptUtil.decrypt_by_aes(re.text[8:], 'hrerujfgjsrtasfr'.encode('utf-8'), 'tdrdadq59tbss5Y5'.encode('utf-8'))
            log.info_return_message("解密后响应内容:" + dec_res)
            debug_log.append(log.info_return_message("解密后响应内容:"))
            debug_log.append(json.loads(dec_res[:-6]))  # 解密后的字符串后六位是不知道什么来的非法字符，需要去除后才能转格式
        else:
            # response = str(re.json()).replace('{\'', '{"').replace('\':', '":').replace(': \'', ': "').replace('\',', '",').replace(', \'', ', "') \
            #     .replace('\'}', '"}').replace('True', 'true').replace('False', 'false').replace('None', 'null').replace('[\'', '["').replace('\']', '"]')
            # debug_log.append(log.info_return_message("响应内容:" + response))
            response = str(re.json())
            log.info_return_message("响应内容:" + response)
            debug_log.append(log.info_return_message("响应内容"))
            debug_log.append(re.json())
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
            assert_list = ast.literal_eval(assert_content)
            # 遍历断言列表
            for assert_dict in assert_list:
                debug_log.append(log.info_return_message("断言模式:" + assert_dict['pattern']))
                debug_log.append(log.info_return_message("断言内容:" + assert_dict['content']))
                assert_result = assert_util(assert_dict['pattern'], assert_dict['key'], assert_dict['content'], re.json())
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

        debug_log.append(final_result)

    return debug_log


"""执行测试任务"""
@celery.task()
def execute_apitest_task(task_id):
    log = Log('ApiTaskLog')
    # celery传参不能传实例，所以传任务id进来，再用任务id查询对应实例
    apiTestTask = ApiTestTask.query.filter(ApiTestTask.id == task_id).first()
    apiTestTask.status = 1
    db.session.commit()
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
                        debug_log = debug_entrance(api_testcase1.encrypt_type, log, e_id[0], api_testcase1.title, api_testcase1.url, request_header, api_testcase1.request_method, request_body, api_testcase1.file_name
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
