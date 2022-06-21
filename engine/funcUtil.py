import random
from utils import errorCode
from utils.log import Log

"""提取字符串函数并替换结果"""
def replace_func(s):
    try:
        start = s.find('${')
        while start > 0:
            # 用切片获取函数字符串
            s_temp = s[start:]
            end = s_temp.find(')}')
            func = s_temp[2:end+1]
            # 拿到函数字符串后执行函数
            result = eval(func)
            # 计算原字符串中的函数字符串的下标范围，使用切片替换结果值
            s = s.replace(s[start:start+end+2], str(result), 1)
            start = s.find('${')

        return s
    except Exception as e:
        log = Log('log')
        log.error(e)
        raise errorCode.ReplaceEVError()


"""返回a到b的随机值"""
def randomNum(a, b):
    return random.randint(a, b)


"""返回长度为num的随机字符串"""
def randomValue(num):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(num):
        random_str +=base_str[random.randint(0, length)]

    return random_str


"""根据标点符号截取字符串，并返回对应下标的字符串"""
def splitStr(s, punc, sub):
    s_list = s.split(punc)
    return s_list[sub]

# print(replace_func('{"key":"value_${randomValue(3)}$"},"key2":"value_${randomValue(3)}$"}'))
