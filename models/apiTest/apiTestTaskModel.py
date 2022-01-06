from utils.extensions import db


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields

class ApiTestTask(db.Model, EntityBase):
    __tablename__ = 'apiTest_task'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    title = db.Column(db.String(50))
    summary = db.Column(db.String(200))
    create_time = db.Column(db.DateTime)
    status = db.Column(db.Integer)  # 0:待执行,1:执行中,2:执行完成,3:执行失败
    apiTest_detail = db.relationship('ApiTestDetail', backref=db.backref('apiTest_task'), lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)
