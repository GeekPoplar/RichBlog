from flask import Flask
# 从配置文件引入配置类
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
#import logging
# flask使用此包来写日志
#from logging.handlers import SMTPHandler

# 为app提供配置
app = Flask(__name__)
app.config.from_object(Config)
# 初始化数据库和数据库迁移引擎

db = SQLAlchemy(app)
#以SQLAlchemy()包来注册一个数据库，这个包是一个ORM（先有个印象），允许应用程序使用高级实体而不是表和SQL来管理数据库
#ORM的工作就是将高级操作转换为数据库命令
migrate = Migrate(app, db)
#Migrate是Alembic的一个flask封装，是SQlAlchemy的一个数据库迁移框架

login=LoginManager(app)

login.login_view='login'
#给flask_login实例的login属性赋上登录页面的视图函数名

login.login_message = "请登录！"

mail=Mail(app)

bootstrap=Bootstrap(app)

moment=Moment(app)

from app import routes,models,errors



app.run()  # flask启动的地方,不被flask run命令依赖，是直接执行本文件必不可少的命令