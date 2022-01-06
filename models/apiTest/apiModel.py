from utils.extensions import db


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields

class Api(db.Model, EntityBase):
    __tablename__ = 'api'
    id = db.Column(db.Integer, primary_key=True)
    apiModule_id = db.Column(db.Integer, db.ForeignKey('api_module.id'))
    api_name = db.Column(db.String(100))  # 接口名称
    request_method = db.Column(db.String(20))
    url = db.Column(db.String(100))
    summary = db.Column(db.String(50))
    seq = db.Column(db.Integer)  # 序号，用来排序
    status = db.Column(db.Boolean(10))  # 状态，是否启用
    independent = db.Column(db.Boolean(10))  # 是否为独立接口
    api_testcase = db.relationship('ApiTestcase', backref=db.backref('api'), lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)
