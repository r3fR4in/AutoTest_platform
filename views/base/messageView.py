import copy

from flask import Blueprint, jsonify, request
from sqlalchemy import and_

from config import setting
from models.baseModel import Message
from models.baseModel import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from utils import tokenUtil
from utils.extensions import db
import datetime

message = Blueprint('message', __name__)


"""获取用户消息"""
@message.route('/getMessage', methods=['GET'])
@tokenUtil.login_required()
def get_message():
    token = request.headers["Authorization"]
    s = Serializer(setting.SECRET_KEY)
    user = s.loads(token)
    messages = Message.query.filter(Message.user_id == user['id']).order_by(Message.create_time.desc()).limit(20).all()

    result_list = []
    unread_count = 0
    for m in messages:
        m = m.to_json()
        if m['is_read'] == 0:
            unread_count += 1
        result_list.append(m)
    output = {'code': 1000, 'msg': None, 'success': True, 'data': result_list, 'unread_count': unread_count}

    return jsonify(output)


"""批量清空未读提示"""
@message.route('/clearUnreadMessage', methods=['GET'])
@tokenUtil.login_required()
def clear_unread_message():
    token = request.headers["Authorization"]
    s = Serializer(setting.SECRET_KEY)
    user = s.loads(token)
    db.session.query(Message).filter(and_(Message.user_id == user['id'], Message.is_read == 0)).update({Message.is_push: 1, Message.is_read: 1})
    db.session.commit()

    output = {'code': 1000, 'msg': '保存成功', 'exception': None, 'success': True}

    return jsonify(output)


"""推送未推送消息"""
@message.route('/pushMessage', methods=['GET'])
@tokenUtil.login_required()
def push_message():
    token = request.headers["Authorization"]
    s = Serializer(setting.SECRET_KEY)
    user = s.loads(token)
    messages = Message.query.filter(and_(Message.user_id == user['id'], Message.is_push == 0)).order_by(Message.create_time.desc()).limit(20).all()
    result_list = []
    for m in messages:
        m = m.to_json()
        result_list.append(m)
    # db.session.commit会改变result_lst的内存地址的指向，导致result_list数据都变成空，所以要深复制一个数组，返回该数组
    copy_result_list = copy.deepcopy(result_list)

    db.session.query(Message).filter(and_(Message.user_id == user['id'], Message.is_push == 0)).update({Message.is_push: 1}, synchronize_session=False)
    db.session.commit()

    return jsonify(copy_result_list)


"""新增提测写入消息"""
def add_submitted_test_message(receive_id, project_name, submitted_test_name, submitted_test_director):
    # 给管理员和传入id的账号添加未读消息
    admin_ids = db.session.query(User.id).filter(User.role == 'admin_role').all()
    if receive_id is None:
        receive_id = []
    else:
        receive_id = [receive_id]
    for admin_id in admin_ids:
        receive_id.append(admin_id[0])
    create_time = datetime.datetime.now()
    for userid in receive_id:
        Message1 = Message(user_id=userid, title=project_name + ' 提测', content=submitted_test_director + ' 提测 ' + submitted_test_name + ' ，请及时查看处理', create_time=create_time,
                           is_push=0, is_read=0)
        db.session.add(Message1)
        db.session.commit()


"""编辑提测测试负责人写入消息"""
def edit_submitted_test_message(receive_id, project_name, submitted_test_name, submitted_test_director):
    create_time = datetime.datetime.now()
    Message1 = Message(user_id=receive_id, title=project_name + ' 提测', content=submitted_test_director + ' 提测 ' + submitted_test_name + ' ，请及时查看处理', create_time=create_time,
                       is_push=0, is_read=0)
    db.session.add(Message1)
    db.session.commit()


"""冒烟测试完成写入消息"""
def smoke_test_finish_message(receive_id, project_name, submitted_test_name, smoke_testing_result):
    # 给管理员和传入id的账号添加未读消息
    admin_ids = db.session.query(User.id).filter(User.role == 'admin_role').all()
    if receive_id is None:
        receive_id = []
    else:
        receive_id = [receive_id]
    for admin_id in admin_ids:
        receive_id.append(admin_id[0])
    create_time = datetime.datetime.now()
    if smoke_testing_result == 1:
        smoke_testing_result = '测试通过'
    else:
        smoke_testing_result = '测试不通过'
    for userid in receive_id:
        Message1 = Message(user_id=userid, title=project_name + ' 冒烟测试结果', content=project_name + ' ' + submitted_test_name + ' 冒烟测试已完成，' + smoke_testing_result,
                           create_time=create_time, is_push=0, is_read=0)
        db.session.add(Message1)
        db.session.commit()


"""最终测试完成写入消息"""
def test_finish_message(receive_id, project_name, submitted_test_name, test_result):
    # 给管理员和传入id的账号添加未读消息
    admin_ids = db.session.query(User.id).filter(User.role == 'admin_role').all()
    if receive_id is None:
        receive_id = []
    else:
        receive_id = [receive_id]
    for admin_id in admin_ids:
        receive_id.append(admin_id[0])
    create_time = datetime.datetime.now()
    if test_result == 1:
        test_result = '测试通过'
    else:
        test_result = '测试不通过'
    for userid in receive_id:
        Message1 = Message(user_id=userid, title=project_name + ' 测试结果', content=project_name + ' ' + submitted_test_name + ' 测试已完成，' + test_result,
                           create_time=create_time, is_push=0, is_read=0)
        db.session.add(Message1)
        db.session.commit()
