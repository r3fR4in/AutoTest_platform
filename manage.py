# 数据库迁移，用于修改model之后更新数据库表，因为修改model后flask sqlalchemy不会帮我修改数据库表
from flask_migrate import Migrate, MigrateCommand
from utils.extensions import db
from flask_script import Manager
from app import app

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

3.迁移文件中的模型映射到数据库中(注意：执行前先检查生成的迁移脚本！！！)
python manage.py db upgrade


"""
