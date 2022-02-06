from flask import Flask, render_template
from utils import time
from flask_socketio import SocketIO
from config import SQLSETTING, setting
# from config.SchedulerConfig import SchedulerConfig
# from config import scheduler  # 引入APScheduler
# from celery import Celery
# from utils import celery
# from models.exts import db

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.json_encoder = time.CustomJSONEncoder  # 替换默认的json编码器，用于修改返回时间日期的格式
    app.config.from_object(SQLSETTING)  # 导入数据库连接配置
    # app.config.from_object(SchedulerConfig)  # 导入定时任务配置

    # 導入setting的redis配置
    app.config['REDIS_HOST'] = setting.REDIS['HOST']
    app.config['REDIS_PORT'] = setting.REDIS['PORT']
    app.config['REDIS_DB'] = setting.REDIS['DB']
    app.config['REDIS_PWD'] = setting.REDIS['PASSWD']
    app.config['REDIS_EXPIRE'] = setting.REDIS['EXPIRE']

    # 配置celery並創建實例，需要用時從app引用celery
    # 啓動命令：進入項目目錄的Scripts，celery -A app:celery worker -l INFO -P threads
    app.config['broker_url'] = "redis://127.0.0.1:6379/1"
    app.config['result_backend'] = "redis://127.0.0.1:6379/2"
    app.config['worker_redirects_stdouts_level'] = "INFO"
    app.config['worker_redirect_stdouts'] = "Disable"
    # celery = Celery(app.name, broker=app.config['broker_url'], backend=app.config['result_backend'])
    # celery.conf.update(app.config)
    # celery.conf.timezone = 'Asia/Shanghai'
    #
    #
    # db.init_app(app)


    # 裝載定時任務
    # scheduler.init_app(app)  # 把任务列表载入实例flask
    # scheduler.start()  # 启动任务计划

    # async_mode = None
    # socketio = SocketIO()
    # socketio.init_app(app, async_mode=async_mode)

    register_blueprint(app)

    return app

def register_blueprint(app):
    # 藍圖路由
    with app.app_context():
        from views.project.projectView import project
        from views.project.projectEnvironmentView import projectEnvironment
        from views.apiTest.apiModuleView import apiModule
        from views.apiTest.apiView import api
        from views.apiTest.apiTestcaseView import apiTestcase
        from views.apiTest.environmentVariableView import environmentVariable
        from views.apiTest.apiTestTaskView import apiTestTask
        from views.base.userView import user
    app.register_blueprint(project, url_prefix='/project')
    app.register_blueprint(projectEnvironment, url_prefix='/project')
    app.register_blueprint(apiModule, url_prefix='/apiTest')
    app.register_blueprint(api, url_prefix='/apiTest')
    app.register_blueprint(apiTestcase, url_prefix='/apiTest')
    app.register_blueprint(environmentVariable, url_prefix='/apiTest')
    app.register_blueprint(apiTestTask, url_prefix='/apiTest')
    app.register_blueprint(user, url_prefix='/user')
