from utils.extensions import db

class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields

class DataDictionary(db.Model, EntityBase):
    __tablename__ = 'data_dictionary'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50))
    value = db.Column(db.String(10240))
