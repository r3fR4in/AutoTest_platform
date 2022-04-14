from utils.extensions import db


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields

# class ApiModule(db.Model, EntityBase):
#     __tablename__ = 'api_module'
#     id = db.Column(db.Integer, primary_key=True)
#     projectEnvironment_id = db.Column(db.Integer, db.ForeignKey('project_environment.id'))
#     parent_id = db.Column(db.Integer)
#     module_name = db.Column(db.String(50))
#     module_description = db.Column(db.String(300))
#     create_time = db.Column(db.DateTime)
#     api = db.relationship('Api', backref=db.backref('api_module'))

class Api(db.Model, EntityBase):
    __tablename__ = 'api'
    id = db.Column(db.Integer, primary_key=True)
    apiModule_id = db.Column(db.Integer, db.ForeignKey('project_module.id'))
    api_name = db.Column(db.String(100))  # 接口名称
    request_method = db.Column(db.String(20))
    url = db.Column(db.String(100))
    summary = db.Column(db.String(50))
    seq = db.Column(db.Integer)  # 序号，用来排序
    status = db.Column(db.Boolean(10))  # 状态，是否启用
    independent = db.Column(db.Boolean(10))  # 是否为独立接口
    api_testcase = db.relationship('ApiTestcase', backref=db.backref('api'), lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)

class ApiTestcase(db.Model, EntityBase):
    __tablename__ = 'api_testcase'
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.Integer, db.ForeignKey('api.id', ondelete='CASCADE'))
    title = db.Column(db.String(100))  # 标题
    request_method = db.Column(db.String(10))  # 请求方法
    request_header = db.Column(db.String(3000))  # 请求头
    request_body = db.Column(db.String(3000))  # 请求体
    # request_param = db.Column(db.String(3000))  # 请求体
    encode = db.Column(db.String(50))  # 请求体编码
    verify = db.Column(db.String(10))  # 是否移除ssl认证
    url = db.Column(db.String(500))  # url
    is_assert = db.Column(db.String(10))  # 判断是否需要断言
    # assert_pattern = db.Column(db.String(20))  # 断言模式
    assert_content = db.Column(db.String(3000))  # 断言内容
    is_post_processor = db.Column(db.String(10))  # 判断是否需要后置处理
    post_processor_content = db.Column(db.String(500))  # 后置处理内容
    file_name = db.Column(db.String(1000))  # 上传文件的名字

class ApiTestTask(db.Model, EntityBase):
    __tablename__ = 'apiTest_task'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    title = db.Column(db.String(50))
    summary = db.Column(db.String(200))
    create_time = db.Column(db.DateTime)
    status = db.Column(db.Integer)  # 0:待执行,1:执行中,2:执行完成,3:执行失败
    apiTest_detail = db.relationship('ApiTestDetail', backref=db.backref('apiTest_task'), lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)

class ApiTestDetail(db.Model, EntityBase):
    __tablename__ = 'apiTest_detail'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('apiTest_task.id', ondelete='CASCADE'))
    apiTestcase_id = db.Column(db.Integer)
    module_name = db.Column(db.String(100))
    api_name = db.Column(db.String(100))
    testcase_name = db.Column(db.String(100))
    output_log = db.Column(db.Text)
    create_time = db.Column(db.DateTime)
    status = db.Column(db.Integer)  # 0:待执行,1:测试通过,2:测试不通过

class EnvironmentVariable(db.Model, EntityBase):
    __tablename__ = 'environment_variable'
    id = db.Column(db.Integer, primary_key=True)
    e_id = db.Column(db.Integer, db.ForeignKey('project_environment.id'))
    name = db.Column(db.String(50))
    value = db.Column(db.String(300))
