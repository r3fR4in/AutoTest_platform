# from flask_script import Manager
# from views import app_create
# from flask_migrate import Migrate, MigrateCommand
# from views import db, socketio
#
# app = app_create()
# manager = Manager(app)
# migrate = Migrate(app, db)
#
# manager.add_command('db', MigrateCommand)
# manager.add_command('run', socketio.run(app=app, host='127.0.0.1', port=5000, normal_debug=True))  # 新加入的代码，重写manager的run命令
#
#
# if __name__ == '__main__':
#     manager.run()













# 数据库迁移，用于修改model之后更新数据库表，因为修改model后flask sqlalchemy不会帮我修改数据库表
from flask_migrate import Migrate, MigrateCommand
from models.exts import db
from flask_script import Manager
from app import app
from models import apiTestModel
from models import baseModel
from models import projectModel
from models import submittedTestsModel

db.init_app(app)

# 实例化一个manager对象
manager = Manager(app)

# 绑定数据库与app
Migrate(app, db)

# 添加迁移命令集，到脚本命令
manager.add_command('db', MigrateCommand)


#如果是以此脚本作为主脚本程序，就执行
if __name__ == '__main__':
    manager.run()

"""
迁移动作:

在项目目录下，进入控制台输入命令

1.初始化迁移文件
python manage.py db init

2.将模型添加到迁移文件
python manage.py db migrate

3.迁移文件中的模型映射到数据库中
python manage.py db upgrade


"""
