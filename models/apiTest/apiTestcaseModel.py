from utils.extensions import db


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields

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
