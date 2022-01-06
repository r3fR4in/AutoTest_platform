from utils.extensions import db


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields

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
