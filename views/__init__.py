# from flask import Flask, render_template
# from flask_socketio import SocketIO
# from config import SQLSETTING
# from flask_sqlalchemy import SQLAlchemy
#
# db = SQLAlchemy()
# socketio = SocketIO()
#
# def app_create():
#     app = Flask(__name__, static_folder="static", template_folder="templates")
#     app.config.from_object(SQLSETTING)
#
#     db.init_app(app)
#     db.create_all(app=app)
#
#     from views.project.projectView import project
#     from views.project.projectEnvironmentView import projectEnvironment
#     from views.apiTest.apiModuleView import apiModule
#     from views.apiTest.apiView import api
#     from views.apiTest.apiTestcaseView import apiTestcase
#
#     app.register_blueprint(project, url_prefix='/project')
#     app.register_blueprint(projectEnvironment, url_prefix='/project')
#     app.register_blueprint(apiModule, url_prefix='/apiTest')
#     app.register_blueprint(api, url_prefix='/apiTest')
#     app.register_blueprint(apiTestcase, url_prefix='/apiTest')
#
#     socketio.init_app(app=app)
