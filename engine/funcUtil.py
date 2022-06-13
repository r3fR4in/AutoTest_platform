import random
import re

"""提取字符串函数并替换结果"""
def replace_func(s):
    try:
        start = s.find('${')
        while start > 0:
            # 用切片获取函数字符串
            s_temp = s[start:]
            end = s_temp.find('}')
            func = s_temp[2:end]
            # 拿到函数字符串后执行函数
            result = eval(func)
            # 计算原字符串中的函数字符串的下标范围，使用切片替换结果值
            s = s.replace(s[start:start+end+1], result, 1)
            start = s.find('${')

    except Exception as e:
        raise AttributeError('函数替换失败')

    return s

def randomNum(a, b):
    return random.randint(a, b)

def randomValue(num):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(num):
        random_str +=base_str[random.randint(0, length)]

    return random_str


# print(replace_func('{"key":"value_${randomValue(3)}$"},"key2":"value_${randomValue(3)}$"}'))
