import logging, time
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import setting
import linecache

# 日志存放文件夹，如不存在，则自动创建一个logs目录
if not os.path.exists(setting.LOG_DIR):os.mkdir(setting.LOG_DIR)

class Log():
    """
    日志记录类
    """
    def __init__(self, filename):
        # 文件的命名
        # self.logname = os.path.join(setting.LOG_DIR, '%s.log'%time.strftime('%Y-%m-%d %H_%M_%S'))
        self.logname = os.path.join(setting.LOG_DIR, filename + '%s.log' % time.strftime('%Y-%m-%d'))
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        # 日志输出格式
        self.formatter = logging.Formatter('[%(asctime)s] [%(filename)s|%(funcName)s] [line:%(lineno)d] %(levelname)-8s: %(message)s')

    def __console(self, level, message):
        # 创建一个FileHandler，用于写到本地日志文件
        fh = logging.FileHandler(self.logname, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        # 创建一个StreamHandler,用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

        if level == 'info':
            self.logger.info(message)
        elif level == 'normal_debug':
            self.logger.debug(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        # 这两行代码是为了避免日志输出重复问题
        self.logger.removeHandler(ch)
        self.logger.removeHandler(fh)
        # 关闭打开的文件
        fh.close()

    def debug(self, message):
        self.__console('normal_debug', message)

    def info(self, message):
        self.__console('info', message)

    def warning(self, message):
        self.__console('warning', message)

    def error(self, message):
        self.__console('error', message)

    def info_return_message(self, message):
        self.__console('info', message)
        m = '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']INFO : ' + message
        return m

    def error_return_message(self, message):
        self.__console('error', message)
        m = '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']ERROR : ' + message
        return m


    def get_filepath(self):
        return self.logname

    def get_number_of_rows(self):
        return len(open(self.logname, encoding='utf-8').readlines())

    def get_log(self, start, end):
        """獲取指定行數的日志信息"""
        result = []
        for line in range(start, end):
            current_context = linecache.getline(self.logname, line).strip()
            result.append(current_context)
        linecache.clearcache()  # 用完linecache要清除緩存，否則無法讀取到最新的文件

        return result
