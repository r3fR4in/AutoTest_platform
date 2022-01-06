from utils.extensions import db


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields

class EnvironmentVariable(db.Model, EntityBase):
    __tablename__ = 'environment_variable'
    id = db.Column(db.Integer, primary_key=True)
    e_id = db.Column(db.Integer, db.ForeignKey('project_environment.id'))
    name = db.Column(db.String(50))
    value = db.Column(db.String(300))
