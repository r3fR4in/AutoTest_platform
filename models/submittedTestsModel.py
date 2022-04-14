from utils.extensions import db


class EntityBase(object):
    def to_json(self):
        fields = self.__dict__
        if "_sa_instance_state" in fields:
            del fields["_sa_instance_state"]
        return fields

class SubmittedTests(db.Model, EntityBase):
    __tablename__ = 'submitted_tests'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    submitted_test_name = db.Column(db.String(100))  # 提测名称
    submitted_test_detail = db.Column(db.String(1000))  # 提测详情
    submitted_date = db.Column(db.Date)
    submitted_test_director = db.Column(db.String(20))  # 提测负责人
    test_director = db.Column(db.String(20))  # 测试负责人
    file_name = db.Column(db.String(1000))  # 上传文件的名字
    test_status = db.Column(db.Integer)  # 测试状态 1：已提测；2：测试完成；3：退回
    smoke_testing_result = db.Column(db.Integer)  # 冒烟测试结果 0：未标记；1：测试通过；2：测试不通过
    smoke_testing_fail_reason_category = db.Column(db.String(20))  # 冒烟测试不通过原因大类
    smoke_testing_fail_reason_detail = db.Column(db.String(20))  # 冒烟测试不通过原因小类
    test_result = db.Column(db.Integer)  # 最终测试结果 0：未标记；1：测试通过；2：测试不通过
    complete_date = db.Column(db.Date)  # 测试完成时间
