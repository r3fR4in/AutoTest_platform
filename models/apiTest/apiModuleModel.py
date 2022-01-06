from utils.extensions import db


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields

class ApiModule(db.Model, EntityBase):
    __tablename__ = 'api_module'
    id = db.Column(db.Integer, primary_key=True)
    projectEnvironment_id = db.Column(db.Integer, db.ForeignKey('project_environment.id'))
    module_name = db.Column(db.String(50))
    module_description = db.Column(db.String(300))
    create_time = db.Column(db.DateTime)
    api = db.relationship('Api', backref=db.backref('api_module'))
