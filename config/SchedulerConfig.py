
# 定时任务配置类
class SchedulerConfig:
    JOBS = [
        {
            'id': 'api_test_job',  # 任务id
            # 'func': 'config:SchedulerConfig.api_test_job',  # 任务执行程序
            'func': 'views:apiTest.apiTestTaskView.api_test_job',  # 任务执行程序
            'args': None,  # 执行程序参数
            'trigger': 'interval',  # 任务执行类型，定时器
            'seconds': 50000,  # 任务执行时间，单位秒
        }
    ]
    # 设置时区，时区不一致会导致定时任务的时间错误
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'


