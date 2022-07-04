from utils.extensions import db


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields

class User(db.Model, EntityBase):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    status = db.Column(db.Integer)  # 狀態：1正常，2禁用
    role = db.Column(db.String(50))  # 角色：管理員 admin_role

class DataDictionary(db.Model, EntityBase):
    __tablename__ = 'data_dictionary'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50))
    value = db.Column(db.String(10240))

class UserProject(db.Model, EntityBase):
    __tablename__ = 'user_project'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

class Message(db.Model, EntityBase):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(50))
    content = db.Column(db.String(200))
    create_time = db.Column(db.DateTime)
    is_push = db.Column(db.Integer)  # 是否推送：0未推送，1已推送
    is_read = db.Column(db.Integer)  # 是否已读：0未读，1已读
