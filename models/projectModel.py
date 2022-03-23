from utils.extensions import db


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields

class Project(db.Model, EntityBase):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    projectName = db.Column(db.String(50), unique=True)
    projectDescription = db.Column(db.String(300))
    create_time = db.Column(db.DateTime)
    project_environment = db.relationship('ProjectEnvironment', backref=db.backref('project'))
    apiTest_task = db.relationship('ApiTestTask', backref=db.backref('project'))
    submitted_tests = db.relationship('SubmittedTests', backref=db.backref('project'))

class ProjectEnvironment(db.Model, EntityBase):
    __tablename__ = 'project_environment'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    e_name = db.Column(db.String(50))
    url = db.Column(db.String(100))
    e_description = db.Column(db.String(300))
    create_time = db.Column(db.DateTime)
    api_module = db.relationship('ApiModule', backref=db.backref('project_environment'))


